# Handoff - AI Scorer

## Scope

Produce broad-pass scores and reasoning for each canonical business type against the founder thesis.

## Inputs

- `canonical_dataset.*` from Dataset Shaper
- locked metric set, scoring rules, verbal rank labels, and founder thesis from `execution-master-context.md`

## Execution Loop

Follow the mandatory execution protocol from `execution-package-index.md`:
1. plan the implementation approach and get it approved before writing code
2. write, run, verify each part
3. advance only after verified pass

## Model Strategy

- primary: balanced reasoning model for batch scoring
- escalation: stronger reasoning model only for low-confidence, invalid, or borderline outputs
- scoring mode: small-batch (e.g. 10-30 businesses per batch) for practical speed with manageable retry logic

## Prompt Structure Rule

Within each scoring call, the model must follow this order:
1. reason about the business as a whole candidate against the full metric lens and founder thesis
2. only after the whole-business reasoning block, assign per-metric scores
3. produce per-metric reasoning using verbal rank labels (Weak / Emerging / Solid / Strong) with confidence
4. produce 1-2 line overall summary

This "reason first, score second" order is a hard requirement — metric scores must follow from coherent whole-business analysis, not precede it.

## Required Work

1. evaluate each business type as a whole candidate first (see prompt structure rule)
2. assign all metric scores (0-3)
3. produce per-metric reasoning (1-2 sentences using verbal rank label + alignment explanation) and confidence (low / medium / high)
4. produce overall fit summary per candidate
5. emit `passes_floor` based on floor metrics
6. validate output schema and score bounds
7. route failed or low-confidence records to rerun/escalation queue

## Output Artifacts

- `broad_pass_packet.*`
- `scoring_validation_report.*`
- `scoring_rerun_queue.*` (if needed)

## Verify

- every candidate has complete metric coverage
- no scores outside 0-3
- per-metric reasoning uses verbal rank labels and includes confidence
- overall summary present
- floor-pass logic matches locked rule
- rerun queue exists for failed or incomplete model responses

## Pass Gate

Pass only if scoring output is complete and schema-valid.

## On Failure

- fix scoring prompt/validator path
- rerun failed subset or full batch
- escalate persistent failures to stronger model
- regenerate validation report
