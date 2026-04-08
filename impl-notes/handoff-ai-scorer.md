# Handoff - AI Scorer

## Scope

Produce broad-pass scores and reasoning for each canonical business type against the founder thesis.

## Inputs

- `canonical_dataset.*` from Dataset Shaper
- locked metric set, scoring rules, verbal rank labels, and founder thesis from `execution-master-context.md`

## Pre-Planning Gate: Founder Metric Review — COMPLETED

The mandatory founder metric review session was conducted. Outcomes:

### Changes Made

1. **Metric `operational_complexity` replaced** by `owner_independence_potential` — measures whether the business can eventually run without the founder being hands-on daily, aligned with the 5-10 year self-running business goal.
2. **Metric `revenue_fragmentation` dropped** — redundant with `market_headroom` and penalized valid concentrated-revenue B2B models.
3. **Metric `regulatory_liability_drag` demoted to informational** — scored but excluded from the non-floor average calculation. Regulation can be a moat; it should not penalize otherwise excellent candidates.
4. **Founder thesis expanded** with personal context: first-time founder, Jerusalem-based, ~150K NIS starting capital, 5-10 year self-running goal.
5. **Metric tiers established**: Tier 1 (floor gates), Tier 2 (high priority), Tier 3 (important signal), Informational.
6. **Non-floor average** now computed from Tier 2 + Tier 3 only (8 metrics), excluding `regulatory_liability_drag`.

All changes locked in `execution-master-context.md`.

## Scoring Prompt

The locked scoring prompt is stored as files (not inline) for maintainability:

- **System prompt**: `src/ai_scorer/prompts/scoring_system_prompt.txt`
- **User prompt template**: `src/ai_scorer/prompts/scoring_user_prompt_template.txt`

The prompt encodes:
- Full founder thesis and personal context
- All 12 metrics with tier labels, plain-language descriptions, and anchor examples (0 and 3)
- "Reason first, score second" ordering rule
- Strict JSON output schema
- Classification fields (business_model_archetype, primary_customer_type, revenue_model)

## Model Strategy — LOCKED (Updated after benchmark + shootout testing)

- Model: `o3` via OpenAI Batch API (JSON mode)
- Batch size: 5 businesses per API call (~722 batches total)
- API method: Batch API (async, 50% cost reduction, no timeout risk)
- Retry: up to 2 retries with `o3` for failed/invalid records
- Estimated cost: ~$18 (Batch API pricing)
- Estimated runtime: submit once, results within 24 hours (no machine uptime required)

### Model Selection Evidence

Benchmark tested gpt-4.1, gpt-4.1-mini, gpt-4.1-nano across batch sizes 5/10/20.
Shootout tested o3, o1, o4-mini, gpt-4o, gpt-4.1 head-to-head on same 5 diverse businesses.
Results stored in `data/output/benchmark_results.json` and `data/output/model_shootout_results.json`.

Key finding: o3 produced the most conservative and realistic calibration on edge cases.
o1 was 15x more expensive with no quality improvement.
Prompt improvements (middle anchors, calibration baseline, geographic weight) had larger accuracy impact than any model change.

## Sub-part Execution Order

This phase is broken into three sub-parts. Execute in order; each must pass before the next begins.

### Sub-part A: Scoring Infrastructure
- **Handoff**: `handoff-ai-scorer-subpart-a.md`
- **Scope**: Build LLM client, batch manager, response parser, validator, orchestrator CLI
- **Pass gate**: Test batch of 20 businesses scored, validated, and persisted to SQLite

### Sub-part B: Batch Execution
- **Handoff**: `handoff-ai-scorer-subpart-b.md`
- **Scope**: Full scoring run across all 3,606 records with retry and escalation
- **Pass gate**: All records scored (or documented as permanent failures) in SQLite

### Sub-part C: Post-processing & Output
- **Handoff**: `handoff-ai-scorer-subpart-c.md`
- **Scope**: Compute floor pass and non-floor average, generate output artifacts, run final verification
- **Pass gate**: All three output artifacts generated and validated

## Prompt Structure Rule

Within each scoring call, the model must follow this order:
1. reason about the business as a whole candidate against the full metric lens and founder thesis
2. only after the whole-business reasoning block, assign per-metric scores
3. produce per-metric reasoning using verbal rank labels (Weak / Emerging / Solid / Strong) with confidence
4. produce 2-3 sentence overall summary

This "reason first, score second" order is a hard requirement.

## Output Artifacts (Phase 3 Final)

- `data/output/broad_pass_packet.json`
- `data/output/scoring_validation_report.json`
- `data/output/scoring_rerun_queue.json`

## Verify

- every candidate has complete metric coverage (12 metrics)
- no scores outside 0-3
- per-metric reasoning uses verbal rank labels and includes confidence
- overall summary present
- floor-pass logic matches locked rule
- non-floor average computed from correct 8 metrics
- rerun queue exists for failed or incomplete model responses

## Pass Gate

Pass only if scoring output is complete and schema-valid across all 3,606 records.

## On Failure

- fix scoring prompt/validator path
- rerun failed subset or full batch with `o3`
- regenerate validation report
