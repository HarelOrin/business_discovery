# Handoff - Gate Keeper

## Scope

Apply shortlist gates and approval routing using locked decision policy. This phase is deterministic rules only — no LLM is used for gate decisions.

## Inputs

- `broad_pass_packet.*` from AI Scorer

## Execution Loop

Follow the mandatory execution protocol from `execution-package-index.md`:
1. plan the implementation approach and get it approved before writing code
2. write, run, verify each part
3. advance only after verified pass

## Non-Floor Metrics Reference

Floor metrics (must pass >= 2): `market_headroom`, `margin_quality`, `distribution_efficiency`

Non-floor metrics (used for average calculation): `startup_capital_intensity`, `speed_to_first_revenue`, `team_model_fit`, `operational_complexity`, `demand_urgency`, `recurring_revenue_potential`, `revenue_fragmentation`, `regulatory_liability_drag`, `non_commodity_differentiation`, `ai_automation_leverage`

## Required Work

1. apply floor checks:
   - market_headroom >= 2
   - margin_quality >= 2
   - distribution_efficiency >= 2
2. compute non-floor average score (average of all 10 non-floor metrics listed above)
3. apply shortlist rule: candidate must pass floor AND have non-floor average >= 1.9
4. apply manual approval routing for shortlisted candidates:
   - non-floor average < 2.5 -> manual approval queue
   - non-floor average >= 2.5 -> auto-approved for deep research
5. emit decision packets and queue outputs

## Output Artifacts

- `shortlist_decision_packet.*`
- `manual_approval_queue.*`
- `auto_approved_queue.*`
- `gate_validation_report.*`

## Verify

- floor logic and threshold logic are deterministic and reproducible
- manual queue and auto-approved queue are mutually exclusive
- all shortlisted candidates are assigned to exactly one approval path
- non-floor average is computed from exactly the 10 non-floor metrics

## Pass Gate

Pass only if gate outputs are complete, deterministic, and policy-compliant.

## On Failure

- fix gate rule implementation
- rerun gate pass
- rerun validation checks
