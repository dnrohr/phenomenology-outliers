# Phenomenology Outlier Registry

This repository is a growing, source-linked catalog of unusually structured conscious experiences and cognitive capacities. It collects spontaneous first-person reports, formal case studies, and book-length clinical narratives. The aim is discovery: preserve what was reported, identify within-person contrasts, and let unusual cases expand the taxonomy.

The registry currently contains **223 accounts**. Start with the [catalog index](catalog/README.md), the [taxonomy](taxonomy/README.md), or the [method and record format](METHOD.md).

## Epistemic stance

Accounts are recorded **at face value as accounts**. The catalog does not treat a self-report as a diagnosis, nor does it silently replace a person's description with a clinical explanation. Every entry separates:

- what the person or source reports;
- the circumstances and functional consequences;
- catalog tags and contrasts;
- limitations of what the source makes available.

Inclusion is not endorsement of a causal interpretation. Discovery comes first; verification and adjudication can be added later without erasing the original claim.

## Repository map

```text
catalog/
  self-reports/       spontaneous or conversational first-person accounts
  journal-cases/      named or anonymized participants in scholarly reports
  book-cases/         narrative clinical and autobiographical book accounts
  README.md           browsable master index
taxonomy/
  README.md           evolving dimensions derived from the prior survey
assets/
  POR-####/           source-associated images and provenance notes
scripts/
  validate_catalog.py structural and catalog validation
  validate_new_links.py network-check only new or changed source URLs
research/
  SOURCE_WORKFLOW.md source discovery, retention, and deduplication strategy
  source-ledger.tsv durable record of found, used, and rejected sources
METHOD.md             inclusion rules, source policy, and entry template
```

The account type is used for filesystem stability. Phenomenological categories are many-to-many tags, so an account can simultaneously concern imagery, dreaming, memory, inner speech, bodily sensation, agency, and time without being duplicated or forced into one diagnostic folder.

## Validate

```powershell
python scripts/validate_catalog.py
python scripts/validate_new_links.py
```

The catalog validator checks IDs, required metadata, original-source links, local image references, index coverage, and expansion coverage. The network checker compares the working tree with `HEAD`, assumes unchanged links are already trusted, and requests only new or changed URLs.

After committing but before pushing, compare the commit with the remote branch:

```powershell
python scripts/validate_new_links.py --base-ref origin/main
```

Publisher responses `401`, `403`, and `429` are reported as `BLOCKED` without failing by default because they commonly reject automated requests. Use `--strict-blocked` when every URL must produce a successful automated response.
