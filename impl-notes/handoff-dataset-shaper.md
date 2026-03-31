# Handoff - Dataset Shaper

## Scope

Transform raw intake into canonical dataset used by scoring.

## Inputs

- `raw_intake_combined.*` from Source Puller

## Execution Loop

Follow the mandatory execution protocol from `execution-package-index.md`:
1. plan the implementation approach and get it approved before writing code
2. write, run, verify each part
3. advance only after verified pass

## Required Work

1. normalize names (case, punctuation, singular/plural, aliases)
2. dedupe using three-tier model:
   - tier 1: exact match on normalized text
   - tier 2: rule-based alias matching (maintained synonym/alias map)
   - tier 3: similarity candidate generation (thresholded suggestions routed to review queue — never silent auto-merge)
3. generate canonical records matching locked dataset contract from `execution-master-context.md`
4. retain provenance through merge process
5. validate acceptance gate for dataset readiness

Recommended approach: SQL-first shaping pipeline for canonicalization and dedupe traceability; keep deterministic normalization rules as the primary mechanism.

## Output Artifacts

- `canonical_dataset.*`
- `merge_log.*`
- `conflict_queue.*`
- `dataset_validation_report.*`

## Verify

- `700+` active canonical records post-dedupe
- required fields exist for all active records
- provenance retained for canonical records
- unresolved conflict backlog within accepted threshold
- output contract is stable for AI Scorer input without schema changes

## Pass Gate

Pass only if canonical dataset contract is satisfied and ready for scoring.

## On Failure

- fix normalization/dedupe rules
- rerun shaping
- rerun validation report
