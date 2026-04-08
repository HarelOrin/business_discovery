# Handoff — AI Scorer Sub-part C: Post-processing & Output

## Scope

Extract all scored results from SQLite, compute derived fields (floor pass, non-floor average), generate the three required output artifacts, and run final validation.

## Pre-requisites

- Sub-part B passed: all 3,606 records scored and persisted in SQLite
- `data/output/scoring_progress.db` contains complete scoring results

## Inputs

- `data/output/scoring_progress.db` — SQLite with all scored results
- `data/output/canonical_dataset.json` — original records (for merging source fields)
- `impl-notes/execution-master-context.md` — gate logic rules

## Required Work

### 1. Floor Pass Computation

For each scored record, compute `passes_floor` (boolean):
- `market_headroom >= 2` AND `margin_quality >= 2` AND `distribution_efficiency >= 2`
- All three must pass; any one below 2 means `passes_floor = false`

### 2. Non-Floor Average Computation

For each scored record, compute `non_floor_average` (float, 2 decimal places):
- Average of Tier 2 metrics: `startup_capital_intensity`, `speed_to_first_revenue`, `team_model_fit`, `recurring_revenue_potential`, `owner_independence_potential`
- Plus Tier 3 metrics: `demand_urgency`, `non_commodity_differentiation`, `ai_automation_leverage`
- Total: 8 metrics averaged
- `regulatory_liability_drag` is EXCLUDED from this average (informational only)

### 3. Generate `broad_pass_packet.json`

Array of all 3,606 scored records. Each record contains:

```json
{
  "record_id": "canon_0001",
  "business_type": ".NET Developers",
  "definition": null,
  "source_family": "g2",
  "source_ref": "g2.com/categories/net-developers",
  "business_model_archetype": "<from scoring>",
  "primary_customer_type": "<from scoring>",
  "revenue_model": "<from scoring>",
  "whole_business_reasoning": "<from scoring>",
  "metrics": {
    "market_headroom": {"score": 2, "reasoning": "...", "confidence": "high"},
    ...all 12 metrics...
  },
  "overall_fit_summary": "<from scoring>",
  "passes_floor": true,
  "non_floor_average": 2.13,
  "regulatory_liability_drag_score": 2,
  "scoring_metadata": {
    "model_used": "o3",
    "attempt_count": 1,
    "retry_count": 0,
    "low_confidence_count": 0
  }
}
```

### 4. Generate `scoring_validation_report.json`

```json
{
  "run_timestamp": "2026-03-31T...",
  "total_records": 3606,
  "scored_successfully": 3606,
  "failed_permanently": 0,
  "coverage": {
    "full_metric_coverage": 3606,
    "partial_metric_coverage": 0,
    "missing_overall_summary": 0
  },
  "score_bounds": {
    "all_scores_in_range": true,
    "out_of_range_count": 0
  },
  "verbal_labels": {
    "all_reasoning_has_labels": true,
    "missing_label_count": 0
  },
  "confidence_labels": {
    "all_present": true,
    "distribution": {"low": N, "medium": N, "high": N}
  },
  "floor_pass_stats": {
    "total_passing_floor": N,
    "total_failing_floor": N,
    "failure_reasons": {
      "market_headroom_below_2": N,
      "margin_quality_below_2": N,
      "distribution_efficiency_below_2": N
    }
  },
  "non_floor_average_stats": {
    "mean": 1.85,
    "median": 1.88,
    "min": 0.5,
    "max": 2.88,
    "above_1.9_count": N,
    "above_2.5_count": N
  },
  "score_distributions": {
    "market_headroom": {"0": N, "1": N, "2": N, "3": N},
    ...per metric...
  },
  "model_usage": {
    "model": "o3",
    "primary_batches": 722,
    "retry_batches": N,
    "total_tokens_input": N,
    "total_tokens_output": N,
    "estimated_cost_usd": N
  }
}
```

### 5. Generate `scoring_rerun_queue.json`

Array of records that failed validation after all retries and escalation:

```json
{
  "rerun_queue": [
    {
      "record_id": "canon_XXXX",
      "business_type": "...",
      "failure_reason": "missing metrics: [demand_urgency]",
      "attempts": 3
    }
  ],
  "total_in_queue": 0,
  "note": "Empty queue — all records scored successfully"
}
```

If all records scored successfully, this file still exists but with an empty queue and a note.

### 6. Final Verification Script

Run a standalone verification that reads `broad_pass_packet.json` and confirms:
- Record count matches canonical dataset (3,606)
- All 12 metrics present for every record
- All scores in 0-3 range (integers)
- All reasoning strings contain verbal rank labels
- All confidence values are valid
- All `passes_floor` flags match recomputed values
- All `non_floor_average` values match recomputed values
- `overall_fit_summary` present for every record
- Print summary table of results

## Output Artifacts

- `data/output/broad_pass_packet.json`
- `data/output/scoring_validation_report.json`
- `data/output/scoring_rerun_queue.json`
- `src/ai_scorer/post_process.py` (floor pass, average computation, artifact generation)
- `src/ai_scorer/verify_scoring.py` (standalone verification script)

## Verify

- All three output files exist and are valid JSON
- `broad_pass_packet.json` contains 3,606 records with complete scoring data
- `scoring_validation_report.json` shows full coverage and no bounds violations
- `scoring_rerun_queue.json` exists (even if empty queue)
- Floor pass logic verified against manual spot-checks
- Non-floor average verified against manual spot-checks

## Pass Gate

Sub-part C passes when all three output artifacts are generated, validated, and the verification script confirms all acceptance criteria. This completes Phase 3.

## Phase Return Package

After Sub-part C passes, compile and return the Phase 3 return package:
- Scope implemented
- Commands executed
- Verification evidence (validation report contents, sample records)
- Pass/fail status
- Produced artifacts (file paths and descriptions)
- Unresolved issues (if any)
- Recommendation: proceed to Phase 4 (Gate Keeper) or hold
