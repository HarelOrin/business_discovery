# Handoff - AI Scorer

## Scope

Produce broad-pass scores and reasoning for each canonical business type against the founder thesis.

## Inputs

- `canonical_dataset.*` from Dataset Shaper
- locked metric set, scoring rules, verbal rank labels, and founder thesis from `execution-master-context.md`

## Pre-Planning Gate: Founder Metric Review (MANDATORY)

Before entering the plan-write-test cycle, you MUST conduct an interactive review session with the founder. This session must happen FIRST — no planning or code until it completes and decisions are locked.

### What to cover:

1. **Present every scoring metric** with a plain-language explanation of what it measures and why it exists. Walk through them one at a time.
2. **Present the founder thesis** as currently captured in `execution-master-context.md` and ask the founder to confirm, adjust, or expand it.
3. **Ask the founder to evaluate each metric**: Does it matter to their decision? Is it clear? Is anything redundant?
4. **Ask about missing dimensions**: Are there important factors not captured by the current 13 metrics?
5. **Review the gate logic**: Are the three floor metrics the right hard requirements? Should any be added or changed?
6. **Capture weighting intuition**: Even with equal numeric weights, which metrics matter most? This shapes the scoring prompt.
7. **Lock decisions**: Summarize all changes, get explicit founder approval, then update `execution-master-context.md` with any metric/thesis/gate changes BEFORE writing the implementation plan.

### Why this matters:

The metric set defines what "good" means for the entire downstream pipeline — gate logic, shortlisting, and deep research all flow from these scores. Getting the metrics wrong means scoring 3,600+ businesses against the wrong criteria. This is the single highest-leverage decision point in the project.

### Output of this session:

- Confirmed or updated metric set in `execution-master-context.md`
- Confirmed or updated founder thesis in `execution-master-context.md`
- Confirmed or updated gate logic in `execution-master-context.md`
- Only AFTER these are locked: proceed to the execution loop below

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
