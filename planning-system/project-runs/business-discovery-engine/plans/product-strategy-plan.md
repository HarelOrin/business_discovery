# Business Discovery Engine - Product Strategy Plan

## Status

- stage: stage-4-technical-planning-and-handoff
- maturity: in progress

## Product Intent

Design a repeatable decision process to identify business categories that match the founder thesis, then shortlist candidates for deeper validation.

## Founder Thesis Snapshot

- massive potential customer pool with room to scale despite incumbents
- prefer no employees or a small team of skilled professionals
- high-margin offerings over low-margin commodity dynamics
- boring/crowded categories are acceptable when economics are strong
- avoid dependence on off-the-shelf product selling
- low starting investment and speed-to-scale are explicit fit dimensions

## Stage-1 Decision Model (Current)

- model style: tag-first coverage, avoid premature elimination
- per-metric output:
  - score: integer 0-3
  - reasoning: 1-2 sentences with verbal rank and alignment explanation
  - confidence: low / medium / high
- per-business output:
  - short overall AI paragraph summarizing fit to founder vision

## Stage-1 Canonical Metric Set (Draft v0.1)

Use this as a tag-first assessment schema (not a hard elimination filter):

- `market_headroom`: how large and expandable demand is even with strong incumbents
- `startup_capital_intensity`: how little upfront capital is required to launch credibly
- `speed_to_first_revenue`: expected time from launch to first meaningful cash inflow
- `margin_quality`: gross margin potential and ability to protect pricing power
- `team_model_fit`: fit with no-employee or small skilled-professional team preference
- `operational_complexity`: day-to-day delivery complexity and management burden
- `distribution_efficiency`: ability to acquire customers without high paid-acquisition dependence
- `demand_urgency`: whether customers treat the offer as must-solve vs nice-to-have
- `recurring_revenue_potential`: likelihood of repeat purchases or retainers vs one-off sales only
- `revenue_fragmentation`: reliance on many customers vs concentration in a few risky accounts
- `regulatory_liability_drag`: licensing/compliance/legal burden that can slow or de-risk growth
- `non_commodity_differentiation`: ability to avoid pure commodity competition and protect value
- `ai_automation_leverage`: how much delivery, sales, or operations can be AI-augmented over time

Scoring interpretation (shared across all metrics):

- `0`: poor alignment
- `1`: limited alignment
- `2`: good alignment
- `3`: strong alignment

Verbal rank labels to use in reasoning:

- `0 -> Weak`
- `1 -> Emerging`
- `2 -> Solid`
- `3 -> Strong`

## Stage-1 Closeout Decision (Approved)

- Stage 1 is approved as good enough and closed.
- strategic minimum thresholds:
  - `market_headroom` must be at least `Solid` (score >= 2)
  - `margin_quality` must be at least `Solid` (score >= 2)
  - `distribution_efficiency` must be at least `Solid` (score >= 2)
- all other metrics remain tag-first (diagnostic) and can be prioritized later.

## Stage-4 Step-3 Deep-Research Scope (Branch Draft For Origin Approval)

### Research Dimensions Per Approved Shortlist Candidate

Every candidate that clears the Stage-3 gate and receives approval (auto or manual) must be investigated across these eight dimensions before the founder makes a final business selection:

1. `market_landscape_brief` — TAM estimates, growth trajectory, customer segment breakdown, geographic signals
2. `competitive_intel_summary` — named incumbents, market structure, competitive moats, white-space gaps
3. `unit_economics_estimate` — typical pricing, gross margin band, CAC patterns, LTV indicators
4. `regulatory_scan` — licensing/compliance barriers, cost ranges, legal risk, jurisdictional variance
5. `operating_model_brief` — delivery mechanics, team requirements, tech stack, vendor dependencies, small-team fit
6. `thesis_stress_test` — counterarguments for high-scoring metrics, revised confidence per metric
7. `speed_to_revenue_assessment` — realistic timeline, minimum viable offering, launch prerequisites, critical-path blockers
8. `risk_scan` — top existential risks with severity/likelihood, single-factor disqualifier flags

Relationship to AI Scorer: deep research substantiates or challenges broad-pass scores with specific evidence. It is an evidence layer, not a re-score.

### Manual Research Track (Founder-Performed)

| Task | Purpose | How-To |
|---|---|---|
| M1: Personal Energy Check | Fast-filter categories the founder has no motivation for | Read automated brief, write 1-sentence gut reaction per candidate. Discard firm "would not" answers. |
| M2: Competitor Review | Verify competitive claims with real products | 15-30 min per candidate: review 2-3 top competitor websites/pricing/reviews. Note commoditization, gaps, entry angle. |
| M3: Customer Accessibility Probe | Confirm founder can reach target buyers | Identify one concrete channel to reach 10 prospects within 2 weeks. Flag distribution risk if none exists. |
| M4: Regulatory Verification | Confirm/dismiss regulatory flags for target geography | 15-20 min for flagged candidates: check licensing portal, industry FAQ, practitioner forum. Record barrier status. |
| M5: Final Go/No-Go Judgment | Produce the founder decision | Rank surviving candidates by conviction. Write 2-3 sentences per finalist explaining preference. |

Operating guidance: M1 first as fast filter. M2-M4 in parallel for survivors. M5 last. Budget ~1-2 hours manual time per candidate.

### Automated Research Track (Research Runner)

The Research Runner produces all 8 research dimension outputs (A1-A8) per candidate in a single structured prompt. Uses AI world-knowledge depth (no live web research for this run). Balanced reasoning model primary; escalation to stronger model when 3+ sections self-report low confidence. Schema validation ensures all sections populated with per-section confidence labels and non-duplicate content vs broad-pass.

### Deep-Research Quality Gate

Research is complete per candidate when:
1. Automated brief has all 8 sections populated
2. No placeholder or "unable to assess" without explicit fallback
3. Per-section confidence labels present
4. Stress test contains counterarguments for each metric scored >= 2
5. Risk scan identifies at least one risk

Research is complete for the full shortlist when:
6. All approved candidates have passing automated briefs
7. Founder completed M1 for all candidates
8. Founder completed M2-M4 for M1 survivors
9. Founder produced M5 ranking
10. At least one candidate has a founder "go" with written rationale

## Open Product Knots

- finalize dual handoffs: founder deliverable plan + implementer-agent coding plan (Stage-4 Step-4)

## Next Checkpoint

Approve Stage-4 Step-4 implementation deliverable package and execution protocol.

## Stage-4 Step-4 Final Deliverables (Origin Draft)

Before execution starts, produce these final plan artifacts:

1. founder-facing plan summary
- concise decision-ready overview of the full system and stage logic
- includes shortlist and deep-research decision process in plain language

2. implementer-facing coding plan
- sectioned technical handoff with build order, contracts, and acceptance gates
- includes strict step execution loop (`write -> run -> verify -> advance/fix`)

3. section handoff briefs
- one brief per build section to keep agent scope clean and reduce clutter
- each brief defines scope boundaries, run checks, and output artifacts

4. execution contract
- origin-coordinated multi-agent protocol for context control and integration
- requires proof of pass before moving between sections

## Stage-4 Architecture Style (Approved)

- architecture style: `origin + specialized branch agents`
- origin agent responsibilities:
  - owns stage progression, decision checkpoints, and final approvals
  - keeps canonical context and plan artifacts synchronized
- specialized branch agent responsibilities:
  - execute narrow scoped analysis/build tasks
  - return structured result packages to origin for integration

## Stage-4 Execution Order (Revised By Founder)

1. plan how to gather and maintain the business-type dataset
2. after dataset plan is stable, plan app architecture (AI call orchestration, output structure, and technology choices)
3. plan deep-research workflow for each shortlisted business, including manual vs automatic work split
4. produce two final deliverables:
   - founder-facing complete plan
   - implementer-facing in-depth coding plan for build agents
5. finalize explicit handoff contracts (what is handed off, to whom, and in what format)

## Stage-4 Step-1 Dataset Gathering (Branch Direction Update)

- decision style: one-time run for this project selection cycle (no recurring refresh logic required)
- volume target: collect and normalize at least `700+` business types before scoring
- source strategy for this run is locked to two inputs: `NAICS PDF` + `G2 category hierarchy`
- source unification: map all incoming entries to a canonical business-type record and deduplicate before scoring
- sequencing note: founder-thesis tags are deferred until after initial dataset collection
- sequencing note: intake-stage readiness can be handled in workflow rules and does not require a dedicated dataset column
- planning boundary: keep this section high-level; no implementation coding detail

## Stage-4 Step-1 Source Lock For This Run (Approved Branch Scope)

The initial dataset for this run is sourced from exactly two inputs:

- `NAICS (North American Industry Classification System) PDF`
- `G2 category hierarchy` (`https://www.g2.com/categories?view_hierarchy=true`)

This lock is accepted for speed and one-time run simplicity.

## Stage-4 Step-1 Input-Specific Sourcing Strategy

### NAICS PDF strategy (taxonomy backbone)

- extract all NAICS entries into structured rows (`code`, `title`, optional description text when present)
- treat NAICS as baseline category spine for broad economic coverage
- convert NAICS rows into candidate business-type labels suitable for opportunity scoring language

### G2 hierarchy strategy (modern market expansion)

- scrape category hierarchy pages and capture category labels across software and service sections
- preserve parent-child hierarchy during extraction so category context is not lost
- treat G2 categories as modern/digital category coverage that complements NAICS

### One coherent dataset unification strategy

- ingest NAICS and G2 raw rows into one shared intake table
- normalize naming (case, pluralization, punctuation, synonym cleanup)
- deduplicate near-equivalent categories and keep a merge log
- output one canonical business-type record per unique category concept
- retain provenance links to both source systems where applicable

## Stage-4 Step-1 Completion Gate (For Return To Origin)

Stage-4 Step-1 is complete enough when all are true:

- canonical dataset has `700+` active records after dedupe
- every canonical record has at least one provenance source reference
- NAICS-derived and G2-derived rows are both represented in final canonical output
- merge/conflict backlog is low enough for Stage-2 scoring to proceed without blocker

## Stage-4 Step-1 Canonical Intake Schema (Required Fields Only)

Initial intake dataset fields (pre-scoring, pre-founder-tagging):

- `record_id`: stable unique identifier
- `business_type`: canonical business category name
- `definition`: 1-2 sentence category boundary (what is included/excluded)
- `business_model_archetype`: service / productized service / software / marketplace / hybrid
- `primary_customer_type`: main buyer segment anchor
- `revenue_model`: one-time / recurring / usage / transaction / mixed
- `source_family`: source-family label used for variety accounting
- `source_ref`: source pointer or citation handle for traceability
- `normalization_status`: new / normalized / merged
- `record_status`: active / hold / excluded

Explicit exclusion for initial intake:

- no `founder_thesis_fit_tags` field at this stage
- no dedicated `scoreability` field at this stage

## Stage-4 Step-1 Working File References

Files explicitly in use for this knot:

- branch context: `planning-system/project-runs/business-discovery-engine/active-contexts/branch-stage4-step1-dataset-gathering-context.md`
- product plan (this file): `planning-system/project-runs/business-discovery-engine/plans/product-strategy-plan.md`
- technical plan linkage: `planning-system/project-runs/business-discovery-engine/plans/technical-implementation-plan.md`

Files expected to be updated when returning this knot to origin:

- `planning-system/project-runs/business-discovery-engine/active-contexts/master-memory.md`
- `planning-system/project-runs/business-discovery-engine/active-contexts/origin-chat-context.md`

## Stage-4 Step-2 App Architecture Direction (Branch Draft For Origin Approval)

- architecture pattern: single orchestrator flow with specialized role modules, aligned to `origin + specialized branch agents`
- interfaces: `CLI-first` execution and artifact review; no web interface is needed for this run
- orchestration style: simple and effective staged flow over heavy workflow platforms
- implementation sequencing rule (locked by founder): each major step must be fully implemented and run-validated before starting the next step
- gating continuity: preserve approved shortlist and human-approval thresholds from Stage-3 without reinterpretation
- source puller lock: NAICS remains a locked source family for this run; implementation source form is official machine-readable NAICS files stored locally in-project
- source puller lock: NAICS implementation should avoid live API dependency and avoid PDF parsing dependency for core intake
- source puller lock: for G2, attempt official API access first; use hierarchy-page scraping fallback only when API access is unavailable or insufficient

Step-2 closure note:

- this architecture package is treated as good enough for planning progression.
- any unresolved low-impact technology refinements are deferred to implementation planning detail, not required to start Step-3.

## Stage-4 Step-2 Architecture Parts Checklist (For Next Branch Turns)

Use plain, implementation-friendly part names for technology-picking discussions:

1. `Source Puller` - gets NAICS + G2 source inputs into raw intake (`status: locked`)
2. `Dataset Shaper` - normalizes, deduplicates, and outputs canonical dataset (`status: in progress`)
3. `AI Scorer` - produces broad-pass scores, reasoning, confidence, and fit summary (`status: in progress`)
4. `Gate Keeper` - applies floor and shortlist logic, then routes manual approvals (`status: lightweight`)
5. `Research Runner` - auto-triggers deep-dive tasks only for approved candidates (`status: lightweight`)
6. `Decision Ledger` - stores approvals, reasons, and stage decisions (`status: pending`)

Implementation method lock:

- use strict sequence for every section: `write -> run -> assert correct / fix -> move to next`
- each next section must use outputs from the previous completed section
- no separate `Run Controller` planning track is needed

AI Scorer clarification (founder direction, draft before lock):

- per business, the model must first reason about the business as a whole candidate against the full metric lens
- only after this reasoning block should metric-level scores be assigned
- output should include short 1-2 line summary reasoning in addition to per-metric reasoning and confidence

## Stage-3 Shortlist Mode (Approved)

- shortlist sizing mode is `score-threshold` (not fixed-N, not hybrid).
- all candidates meeting the threshold are shortlisted; candidates below threshold are not shortlisted.

## Stage-3 Cutoff Model (Approved)

- cutoff model is `C`: two-part gate
  - part 1: candidate must pass floor metrics (`market_headroom`, `margin_quality`, `distribution_efficiency` >= `Solid`)
  - part 2: candidate must meet a minimum average score across non-floor metrics
- part 2 cutoff value is approved at `>= 1.9` average across non-floor metrics

## Stage-3 Human Approval Gate (Approved)

- shortlisted candidates with non-floor average `< 2.5` require manual founder approval before deep-dive.
- shortlisted candidates with non-floor average `>= 2.5` are auto-approved for deep-dive.

## Stage-2 Evidence Strategy (Simplified, Approved)

- broad pass: AI provides opinion-based scoring and reasoning for each business type using context and world knowledge
- no deep external research is required during broad pass
- narrowing rule: apply Stage-1 threshold floor (`market_headroom`, `margin_quality`, `distribution_efficiency` >= `Solid`)
- deep-dive rule: only shortlisted winners receive detailed evidence collection and deeper validation

## Stage-2 Broad-Pass Packet (Approved)

Required fields per business type:

- `business_type`
- `metric_scores` for all Stage-1 metrics (0-3)
- `metric_reasoning` per metric (1-2 sentences + verbal rank + confidence)
- `overall_fit_summary` (short AI paragraph)
- `passes_floor` boolean based on threshold metrics

## Stage Transition Note

- Stage 3 is started by founder direction to maintain momentum.
- Any remaining Stage-2 confidence-rubric refinement can be treated as a lightweight subtask inside Stage 3 execution.
- Stage 3 is treated as good-enough complete to avoid marginal over-design and keep planning momentum.

## Stage-1 Exit Checklist (Lean)

Stage 1 is complete enough when all are true:

- founder thesis and scope are stable
- scoring format is locked (`0-3` + `1-2 sentence reasoning` + `confidence` + overall business paragraph)
- metric schema is good enough to start comparative assessment (even if refinements remain)
- no unresolved blocker is preventing Stage 2 research design

## Efficient Plan Completion Path

Use this to finish the plan without over-expanding early stages:

1. Stage 1 closeout (now): approve "good enough" scorecard package
2. Stage 2: design research inputs and evidence requirements per metric
3. Stage 3: design prioritization method and shortlist review gates
4. Stage 4: finalize technical implementation plan and execution handoff package

Working cadence recommendation:

- one stage-level decision per turn
- defer deep edge-case optimization until the stage that owns it
