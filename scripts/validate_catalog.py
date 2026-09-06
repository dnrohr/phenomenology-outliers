from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
ENTRY_DIRS = [CATALOG / "self-reports", CATALOG / "journal-cases", CATALOG / "book-cases"]
REQUIRED = {
    "id", "title", "account_type", "subject", "source_title", "source_url",
    "source_date", "accessed", "domains", "phenomena", "images",
}
ID_RE = re.compile(r"POR-\d{4}$")
EXPECTED_COUNT = 223
EXPECTED_IDS = {f"POR-{number:04d}" for number in range(1, EXPECTED_COUNT + 1)}
SECOND_EXPANSION_IDS = {f"POR-{number:04d}" for number in range(124, 224)}
MAJOR_DOMAIN_GROUPS = {
    "perception": {"visual-perception", "auditory-perception", "color-perception", "motion-perception"},
    "imagery": {"visual-imagery", "auditory-imagery", "imagery", "orthographic-imagery"},
    "thought-and-language": {"thought", "conceptual-thought", "inner-speech", "language", "reading", "speech"},
    "memory-and-time": {"memory", "autobiographical-memory", "memory-search", "time", "time-space"},
    "emotion": {"emotion", "affective-valuation"},
    "body-and-interoception": {"body", "bodily-awareness", "interoception", "proprioception", "ownership"},
    "agency-and-self": {"agency", "agency-intention", "self", "identity"},
    "space-and-navigation": {"space", "spatial-cognition", "navigation", "spatial-hearing"},
    "sleep-and-dream": {"sleep", "dreaming", "hypnagogia"},
    "cross-modal": {"synesthesia"},
    "chemical-senses": {"smell", "taste"},
    "mathematics": {"math"},
    "scene-representation": {"scene-representation"},
}
SECOND_EXPANSION_FOCUS_MINIMUMS = {
    "math": 10,
    "spatial-cognition": 20,
    "navigation": 8,
    "scene-representation": 15,
}


def load_entry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("+++\n") or "\n+++\n" not in text[4:]:
        raise ValueError("missing TOML front matter")
    raw = text[4:].split("\n+++\n", 1)[0]
    return tomllib.loads(raw)


def main() -> int:
    errors: list[str] = []
    ids: dict[str, Path] = {}
    files = sorted(p for d in ENTRY_DIRS for p in d.glob("*.md"))
    index = (CATALOG / "README.md").read_text(encoding="utf-8") if (CATALOG / "README.md").exists() else ""

    for path in files:
        try:
            meta = load_entry(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        missing = REQUIRED - meta.keys()
        if missing:
            errors.append(f"{path.relative_to(ROOT)}: missing {sorted(missing)}")
        entry_id = str(meta.get("id", ""))
        if not ID_RE.fullmatch(entry_id):
            errors.append(f"{path.relative_to(ROOT)}: invalid id {entry_id!r}")
        elif entry_id in ids:
            errors.append(f"duplicate {entry_id}: {ids[entry_id]} and {path}")
        else:
            ids[entry_id] = path
        parsed = urlparse(str(meta.get("source_url", "")))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{path.relative_to(ROOT)}: invalid original source URL")
        entry_text = path.read_text(encoding="utf-8")
        if entry_id in SECOND_EXPANSION_IDS and f"]({meta.get('source_url', '')})" not in entry_text:
            errors.append(f"{path.relative_to(ROOT)}: original-source link differs from metadata")
        if entry_id and entry_id not in index:
            errors.append(f"{path.relative_to(ROOT)}: not listed in catalog/README.md")
        expected_index_link = path.relative_to(CATALOG).as_posix()
        if f"]({expected_index_link})" not in index:
            errors.append(
                f"{path.relative_to(ROOT)}: exact file link missing from catalog/README.md"
            )
        for image in meta.get("images", []):
            image_path = (ROOT / image).resolve()
            if ROOT not in image_path.parents or not image_path.is_file():
                errors.append(f"{path.relative_to(ROOT)}: missing image {image}")

    actual_ids = set(ids)
    if len(files) != EXPECTED_COUNT:
        errors.append(f"expected {EXPECTED_COUNT} entries, found {len(files)}")
    if actual_ids != EXPECTED_IDS:
        missing_ids = sorted(EXPECTED_IDS - actual_ids)
        extra_ids = sorted(actual_ids - EXPECTED_IDS)
        errors.append(f"ID sequence mismatch; missing={missing_ids}, extra={extra_ids}")

    all_domains: set[str] = set()
    for path in files:
        try:
            all_domains.update(load_entry(path).get("domains", []))
        except Exception:
            pass
    for group, alternatives in MAJOR_DOMAIN_GROUPS.items():
        if not all_domains.intersection(alternatives):
            errors.append(f"major domain group has no entries: {group}")

    expansion_domains: list[str] = []
    expansion_ids = actual_ids.intersection(SECOND_EXPANSION_IDS)
    if expansion_ids != SECOND_EXPANSION_IDS:
        errors.append(
            f"second expansion must contain exactly POR-0124 through POR-0223; "
            f"found {len(expansion_ids)} entries"
        )
    for entry_id in expansion_ids:
        try:
            expansion_domains.extend(load_entry(ids[entry_id]).get("domains", []))
        except Exception:
            pass
    expansion_domain_set = set(expansion_domains)
    for group, alternatives in MAJOR_DOMAIN_GROUPS.items():
        if not expansion_domain_set.intersection(alternatives):
            errors.append(f"second expansion has no entries in major domain group: {group}")
    for domain, minimum in SECOND_EXPANSION_FOCUS_MINIMUMS.items():
        actual = expansion_domains.count(domain)
        if actual < minimum:
            errors.append(
                f"second expansion needs at least {minimum} {domain!r} reports; found {actual}"
            )

    print(f"Validated {len(files)} catalog entries.")
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    print("Catalog structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
