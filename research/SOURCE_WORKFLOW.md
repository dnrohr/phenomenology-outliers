# Source discovery and retention workflow

This workflow prevents useful sources from being rediscovered or silently discarded and makes corpus expansion systematic.

## Preserve every candidate immediately

Before reading deeply, add each plausible source to `research/source-ledger.tsv`. Use a stable key in this order: DOI, PMID/PMCID, durable post permalink, then canonical URL. Search the ledger with `rg` before opening a new result. One source stays in the ledger even when it is rejected; the status and reason preserve the work already done.

Statuses have specific meanings:

- `found`: captured but not screened;
- `screened`: primary source checked for participant-level phenomenology;
- `queued`: suitable and assigned a proposed domain or report ID;
- `used`: represented in the catalog, with report IDs recorded;
- `rejected`: unsuitable, with a short reusable reason;
- `blocked`: promising, but full text or stable identity is currently unavailable.

Record distinct participants from a case series on separate rows when the paper provides participant-level evidence. Do not create multiple reports from aggregate-only results.

## Find new sources by coverage gap

1. Count current domain tags and choose the least-covered architectural contrast, not merely the least common diagnosis.
2. Search primary-source indexes first: PubMed/PMC, Crossref/DOI, journal sites, institutional repositories, and original public posts.
3. Combine a domain term with evidence-shaped terms such as `single case`, `case series`, `patient`, `participant`, `dissociation`, `preserved`, `impaired`, `intact`, or `phenomenology`.
4. Use backward reference chaining from strong papers to find classic cases and forward citation chaining to find replications or richer descriptions.
5. Harvest case series only when individual accounts or measurements can be separated. Capture every viable sibling case in the ledger during the same pass.
6. Prefer sources with direct descriptions of experience, within-person contrasts, state dependence, compensatory behavior, or task evidence that constrains the report.

## Screening and deduplication

Normalize DOI URLs to `https://doi.org/...` and use PMID or PMCID as a secondary identifier. Before drafting, check the ledger, catalog IDs, source URL, source title, subject initials, and the combination of source plus participant. Similar phenomena from different people are allowed; the same person should not be split unless the source clearly provides independent accounts.

After drafting, run both validators. The differential checker trusts links already present at the selected Git base and spends network time only on new or changed URLs.
