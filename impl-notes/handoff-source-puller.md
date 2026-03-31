# Handoff - Source Puller

## Scope

Ingest locked data sources into raw intake artifacts.

## Inputs

- locked source definitions from `execution-master-context.md`

## Source Locks

- NAICS: use official machine-readable NAICS classification files downloaded once and stored locally in-project
  - do NOT use live NAICS API dependency for core intake
  - do NOT use PDF parsing for core intake
- G2: use `https://www.g2.com/categories?view_hierarchy=true`
  - API-first if access is available
  - deterministic hierarchy scrape fallback if API access is unavailable or insufficient

## Required Work

1. ingest NAICS data from machine-readable official files (local snapshot)
2. ingest G2 category hierarchy (API-first, deterministic scrape fallback)
3. preserve parent/child hierarchy for G2 categories
4. emit raw intake dataset with provenance fields

## Output Artifacts

- `raw_intake_naics.*`
- `raw_intake_g2.*`
- `raw_intake_combined.*`
- source provenance metadata

## Verify

- both sources present in raw intake
- row counts are non-zero and sane
- provenance fields populated
- no schema-breaking nulls on required ingestion columns

## Pass Gate

Pass only if both source streams are valid and written.

## On Failure

- fix source parser/adapter
- rerun ingestion
- re-verify counts/provenance
