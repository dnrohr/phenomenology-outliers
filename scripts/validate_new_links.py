from __future__ import annotations

import argparse
import concurrent.futures
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIRS = (
    ROOT / "catalog" / "self-reports",
    ROOT / "catalog" / "journal-cases",
    ROOT / "catalog" / "book-cases",
)
SOFT_BLOCK_STATUSES = {401, 403, 429}
GET_FALLBACK_STATUSES = SOFT_BLOCK_STATUSES | {400, 405, 501}
HARD_FAILURE_STATUSES = {404, 410}


@dataclass(frozen=True)
class Candidate:
    path: Path
    entry_id: str
    url: str


@dataclass(frozen=True)
class LinkResult:
    candidate: Candidate
    outcome: str
    detail: str


def parse_front_matter(text: str, label: str) -> dict:
    if not text.startswith("+++\n") or "\n+++\n" not in text[4:]:
        raise ValueError(f"{label}: missing TOML front matter")
    raw = text[4:].split("\n+++\n", 1)[0]
    return tomllib.loads(raw)


def git_text(ref: str, path: Path) -> str | None:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        return result.stdout
    return None


def verify_ref(ref: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(f"Git base ref does not resolve to a commit: {ref}")


def find_candidates(base_ref: str) -> list[Candidate]:
    verify_ref(base_ref)
    candidates: list[Candidate] = []
    for directory in CATALOG_DIRS:
        for path in sorted(directory.glob("*.md")):
            current = parse_front_matter(path.read_text(encoding="utf-8"), str(path))
            entry_id = str(current.get("id", "unknown"))
            url = str(current.get("source_url", ""))
            old_text = git_text(base_ref, path)
            old_url = None
            if old_text is not None:
                try:
                    old_url = str(parse_front_matter(old_text, f"{base_ref}:{path.name}").get("source_url", ""))
                except (ValueError, tomllib.TOMLDecodeError):
                    old_url = None
            if old_text is None or url != old_url:
                candidates.append(Candidate(path=path, entry_id=entry_id, url=url))
    return candidates


def request_status(url: str, method: str, timeout: float) -> int:
    headers = {
        "User-Agent": "phenomenology-outliers-link-check/1.0 (+https://github.com/dnrohr/phenomenology-outliers)",
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.1",
    }
    if method == "GET":
        headers["Range"] = "bytes=0-1023"
    request = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def check_candidate(candidate: Candidate, timeout: float, retries: int, strict_blocked: bool) -> LinkResult:
    last_error = "unknown transport error"
    for attempt in range(retries + 1):
        try:
            status = request_status(candidate.url, "HEAD", timeout)
            if status in GET_FALLBACK_STATUSES:
                status = request_status(candidate.url, "GET", timeout)
            if 200 <= status < 400:
                return LinkResult(candidate, "PASS", f"HTTP {status}")
            if status in SOFT_BLOCK_STATUSES:
                outcome = "FAIL" if strict_blocked else "BLOCKED"
                return LinkResult(candidate, outcome, f"HTTP {status}; host refused automated validation")
            if status in HARD_FAILURE_STATUSES:
                return LinkResult(candidate, "FAIL", f"HTTP {status}")
            return LinkResult(candidate, "FAIL", f"HTTP {status}")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = str(exc)
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    return LinkResult(candidate, "FAIL", last_error)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate only catalog source URLs added or changed relative to a Git ref."
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Git commit whose existing source URLs are trusted (default: HEAD)",
    )
    parser.add_argument("--timeout", type=float, default=15.0, help="Seconds per HTTP request")
    parser.add_argument("--retries", type=int, default=1, help="Retries after transport errors")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent URL checks")
    parser.add_argument(
        "--strict-blocked",
        action="store_true",
        help="Fail when a host returns 401, 403, or 429 instead of reporting BLOCKED",
    )
    args = parser.parse_args()

    try:
        candidates = find_candidates(args.base_ref)
    except (ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not candidates:
        print(f"No new or changed source URLs relative to {args.base_ref}.")
        return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [
            executor.submit(
                check_candidate,
                candidate,
                args.timeout,
                max(0, args.retries),
                args.strict_blocked,
            )
            for candidate in candidates
        ]
        results = [future.result() for future in futures]

    order = {"FAIL": 0, "BLOCKED": 1, "PASS": 2}
    for result in sorted(results, key=lambda item: (order[item.outcome], item.candidate.entry_id)):
        relative = result.candidate.path.relative_to(ROOT)
        print(
            f"{result.outcome:7} {result.candidate.entry_id} {result.detail} "
            f"{relative} {result.candidate.url}"
        )

    failures = sum(result.outcome == "FAIL" for result in results)
    blocked = sum(result.outcome == "BLOCKED" for result in results)
    passed = sum(result.outcome == "PASS" for result in results)
    print(
        f"Checked {len(results)} new or changed URLs relative to {args.base_ref}: "
        f"{passed} passed, {blocked} blocked by hosts, {failures} failed."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
