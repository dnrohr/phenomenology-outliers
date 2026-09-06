# Method and record format

## Inclusion

An entry should preserve a specific report about conscious experience or a striking dissociation between closely related capacities. High-value reports often have one or more of these features:

- an explicit within-person contrast (`X is vivid while Y is absent`);
- separation of experience, knowledge, inference, and performance;
- state dependence (waking/dreaming, voluntary/involuntary, perceived/imagined);
- a detailed description of spatial perspective, sensory quality, temporal dynamics, controllability, or functional consequences;
- behavior that constrains a plausible cognitive architecture.

The registry is not limited to recognized diagnoses. A novel description can create a new taxonomy tag.

## Source policy

Every entry must link to the original account: the post or comment thread, the journal article/DOI, or the publisher/original publication page for a book narrative. Secondary sources may be listed only as context. If a source is paywalled, the accessible abstract or publisher description limits what may be asserted.

Short quotations are used only when the exact wording carries phenomenological information. The rest is close paraphrase, both for clarity and copyright compliance. Usernames are retained only when visibly public in the source; deleted or anonymized authors remain anonymous.

Images are stored only when they are integral to the account and the repository records their origin and reuse status. A local copy never replaces the original-source link.

## Metadata header

Each Markdown entry begins with TOML between `+++` markers.

```toml
+++
id = "POR-0000"
title = "Short descriptive title"
account_type = "self-report | journal-case | book-case"
subject = "public username, case initials, or anonymous"
source_title = "Title at source"
source_url = "https://original.example/..."
source_date = "YYYY-MM-DD | YYYY-MM | YYYY | unknown"
accessed = "2026-09-05"
domains = ["visual-imagery"]
phenomena = ["voluntary-involuntary-dissociation"]
images = []
+++
```

## Narrative sections

Entries use these sections where the source supports them:

1. **Account** — the report itself, without diagnostic correction.
2. **Circumstances and course** — onset, duration, state, elicitation, and relevant context.
3. **Structure of the experience** — modality, perspective, vividness, control, dynamics, and access.
4. **Functional consequences and strategies** — behavior, impairment, advantages, and compensation.
5. **Key contrasts** — concise, architecture-relevant dissociations.
6. **Why this case matters** — what dimension or dependency it exposes.
7. **Source boundaries** — what remains unknown or what comes from prompted interpretation.

## Growth rules

- Never recycle an ID.
- Add tags rather than relocating entries when the ontology changes.
- Preserve a source's own labels while recording catalog labels separately.
- Split one source into multiple entries only when it clearly contains multiple people or independent accounts.
- Prefer a durable permalink or DOI.
- Record deleted usernames as `anonymous (deleted account)`.
- When an image is added, include `assets/POR-####/PROVENANCE.md`.

## Research workflow

Record candidate sources, including rejected and temporarily blocked candidates, in [`research/source-ledger.tsv`](research/source-ledger.tsv) as soon as they are found. The detailed [source workflow](research/SOURCE_WORKFLOW.md) defines statuses, deduplication keys, coverage-led discovery, and citation chaining. This makes prior searches reusable instead of forcing each expansion to rediscover and discard the same material.

Before committing, validate structure and only the links changed relative to the current commit:

```powershell
python scripts/validate_catalog.py
python scripts/validate_new_links.py
```

After committing and before pushing, use `--base-ref origin/main` so the link checker tests URLs introduced by the outgoing commit.
