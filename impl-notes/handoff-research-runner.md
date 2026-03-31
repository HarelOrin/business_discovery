# Handoff - Research Runner

## Scope

Generate deep-research packets for approved shortlist candidates using AI world-knowledge depth. No live web research for this run — depth improvement over broad-pass comes from structured deep prompting, explicit counterarguments, and calibrated confidence, not real-time web scraping.

## Inputs

- approved candidate queues from Gate Keeper (auto-approved + manually approved)
- broad-pass packet context per candidate (from AI Scorer)
- canonical dataset context per candidate (from Dataset Shaper)
- founder thesis from `execution-master-context.md`

## Execution Loop

Follow the mandatory execution protocol from `execution-package-index.md`:
1. plan the implementation approach and get it approved before writing code
2. write, run, verify each part
3. advance only after verified pass

## Model Strategy

- primary: balanced reasoning model (same tier as AI Scorer primary)
- escalation trigger: when Research Runner self-reports low confidence on 3+ of 8 sections, rerun that candidate with stronger model
- failure handling: incomplete briefs enter rerun queue with adjusted prompting; persistent failures flagged for manual review

## Required Work

For each approved candidate, generate all 8 research sections in a single structured prompt:

1. market landscape brief — TAM, growth, segments, geography
2. competitive intel summary — named players, structure, moats, gaps
3. unit economics estimate — pricing, margins, CAC, LTV
4. regulatory scan — barriers, costs, risk level, variance
5. operating model brief — delivery, team, tech, dependencies, small-team fit
6. thesis stress test — counterarguments per metric scored >= 2, revised confidence
7. speed to revenue assessment — timeline, MVP, prerequisites, blockers
8. risk scan — top risks with severity/likelihood, disqualifier flags

Required behavior:

- prompt includes the full broad-pass packet as context so research can reference and challenge specific scores
- model must produce new/deeper content — do not restate broad-pass reasoning
- confidence label per section (low / medium / high)
- include counterarguments in thesis stress test for every metric scored >= 2
- produce completeness flag
- trigger escalation when 3+ sections self-report low confidence

## Output Artifacts

- `deep_research_packet.*`
- `research_validation_report.*`
- `research_escalation_queue.*` (if needed)

## Verify

- all 8 sections present and non-empty
- confidence labels present for all sections
- at least one risk identified in risk scan
- stress test includes counterarguments for each metric scored >= 2
- no section is a near-duplicate of broad-pass reasoning (semantic check)

## Pass Gate

Pass only if deep research packets are complete and validation-ready for founder review.

## Founder Manual Research (After Automated Briefs)

After Research Runner completes, the founder performs manual review tasks:

1. M1: Personal Energy Check — fast-filter categories the founder has no motivation for
2. M2: Competitor Review — verify competitive claims with real products (15-30 min per candidate)
3. M3: Customer Accessibility Probe — confirm founder can reach target buyers
4. M4: Regulatory Verification — confirm/dismiss regulatory flags (15-20 min for flagged candidates)
5. M5: Final Go/No-Go Judgment — rank survivors and write preference rationale

Order: M1 first as fast filter, M2-M4 in parallel for survivors, M5 last.

## On Failure

- fix prompt/schema checks
- rerun failed candidates through escalation model if needed
- revalidate completeness
