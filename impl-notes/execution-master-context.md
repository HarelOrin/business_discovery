# Execution Master Context

## Mission

Build a practical business discovery engine that:

1. assembles a canonical business-type dataset
2. scores all candidates against founder-fit metrics
3. gates and shortlists candidates
4. generates deep-research briefs for approved candidates

## Locked Decisions

### Data Intake

- one-time run for this cycle
- source inputs are locked:
  - NAICS classification data (machine-readable official files stored locally in-project; avoid live API and PDF parsing)
  - G2 category hierarchy (`https://www.g2.com/categories?view_hierarchy=true`; API-first, deterministic scrape fallback)
- target: at least `700+` active canonical records after dedupe
- each canonical record must retain source provenance

### Initial Dataset Contract

Required fields:

- `record_id`
- `business_type`
- `definition`
- `business_model_archetype`
- `primary_customer_type`
- `revenue_model`
- `source_family`
- `source_ref`
- `normalization_status`
- `record_status`

### Scoring Contract

- metric score range: `0-3`
- verbal rank labels (must appear in per-metric reasoning):
  - `0 -> Weak`
  - `1 -> Emerging`
  - `2 -> Solid`
  - `3 -> Strong`
- per metric output:
  - score
  - 1-2 sentence reasoning using verbal rank label and alignment explanation
  - confidence label (low / medium / high)
- per business output:
  - short overall fit summary paragraph
- scoring order rule: the model must first reason about the business as a whole candidate against the full metric lens and founder thesis, then assign metric-level scores based on that reasoning

Metric set:

- `market_headroom`
- `startup_capital_intensity`
- `speed_to_first_revenue`
- `margin_quality`
- `team_model_fit`
- `operational_complexity`
- `distribution_efficiency`
- `demand_urgency`
- `recurring_revenue_potential`
- `revenue_fragmentation`
- `regulatory_liability_drag`
- `non_commodity_differentiation`
- `ai_automation_leverage`

### Gate Logic

Floor rules (must pass):

- `market_headroom >= 2`
- `margin_quality >= 2`
- `distribution_efficiency >= 2`

Shortlist threshold model:

- candidate must pass floor
- candidate must have non-floor average `>= 1.9`

Manual approval rule:

- if non-floor average `< 2.5` -> manual approval required
- if non-floor average `>= 2.5` -> auto-approved for deep research

### Deep-Research Contract

Research Runner must generate all sections per approved candidate:

1. market landscape brief
2. competitive intel summary
3. unit economics estimate
4. regulatory scan
5. operating model brief
6. thesis stress test
7. speed to revenue assessment
8. risk scan

## Architecture Mode

- CLI-first execution
- simple orchestrated phase flow
- SQLite-first persistence for this run
- lightweight retry/escalation queues where needed

## Founder Thesis Snapshot

The scoring and research layers evaluate every business against this founder profile:

- massive potential customer pool with room to scale despite incumbents
- prefer no employees or a small team of skilled professionals
- high-margin offerings over low-margin commodity dynamics
- boring/crowded categories are acceptable when economics are strong
- avoid dependence on off-the-shelf product selling
- low starting investment and speed-to-scale are explicit fit dimensions

## Model Strategy (in actual code calls)

- `Source Puller`: no LLM required
- `Dataset Shaper`: no LLM required (optional embedding model for duplicate-candidate suggestions only — never auto-merge)
- `AI Scorer`: balanced reasoning model primary; stronger reasoning model only for low-confidence, invalid, or borderline escalation
- `Gate Keeper`: deterministic rules only — no LLM for gate decisions
- `Research Runner`: balanced reasoning model primary; stronger reasoning model for escalation when 3+ of 8 sections self-report low confidence

## Execution Protocol (Hard Requirement)

For each phase:

1. plan: think through the implementation approach, identify sub-parts if the phase is complex, and get the plan approved before writing any code
2. write: implement only the approved plan scope
3. run: execute and test
4. verify: confirm acceptance criteria are met
5. if pass: freeze outputs and move to next phase
6. if fail: fix and rerun until pass

If the plan step reveals the phase should be broken into sub-parts, execute each sub-part before moving to the next sub-part. Only advance to the next phase after all sub-parts pass.

No phase may be skipped.

## Phase Return Package (Required)

Each phase must return:

- scope implemented
- commands executed
- verification evidence
- pass/fail status
- produced artifacts
- unresolved issues
- proceed/hold recommendation

