# Business Discovery Engine - Technical Implementation Plan

## Status

- stage relevance: active once dataset planning is defined
- maturity: planning in progress (high-level only)

## Purpose

Capture implementation architecture after dataset planning is defined, then mature it into an implementer-ready coding plan.

## Prerequisites To Start

- stage-1 decision package approved
- dataset-gathering strategy defined
- research-backed decision design defined
- required artifacts and approval gates confirmed

## Planned Technical Sections (Placeholder)

- scoring and reasoning data schema
- agent workflow and handoff contracts
- context file lifecycle and storage layout
- validation checks and human-in-the-loop gates
- implementation milestones and test strategy

## Founder-Directed Planning Sequence

1. dataset planning first (inputs, update strategy, structure)
2. application architecture planning second (AI orchestration, outputs, technology)
3. deep-research workflow planning third (manual vs automatic split)
4. produce implementer-agent coding plan with explicit build handoff contract

## Current Note

This file is now active at high level. It will stay planning-focused until dataset and architecture decisions are locked, then it will be matured into an implementer-ready coding plan.

## Stage-4 Step-2 High-Level App Architecture (Branch Draft For Origin Approval)

### Recommended Pattern

- one orchestrator service runs the full stage flow
- specialized role modules execute each stage concern (source intake, shaping, scoring, gating, deep-dive triggering, approvals)
- origin-level approvals remain mandatory at defined checkpoints

### Agent Roles (Planning Level)

- `Source Puller`: gathers locked source data (NAICS + G2) into intake artifacts
- `Dataset Shaper`: normalization, dedupe, canonical record output, provenance continuity
- `AI Scorer`: broad-pass metric scoring with reasoning + confidence + overall fit summary
- `Gate Keeper`: floor checks, shortlist cutoffs, and manual-approval routing
- `Research Runner`: triggers deep research only for approved shortlist
- `Decision Ledger`: records approvals, rationale, and gate outcomes

### AI Orchestration Flow

1. intake and canonical dataset validation (`700+`, source coverage, provenance)
2. broad-pass scoring over canonical dataset
3. shortlist gate checks using approved Stage-3 rules
4. manual-approval queue for required borderline candidates
5. deep-dive trigger only after approval state is valid
6. final packaging into founder-facing and implementer-facing artifacts

### Output Contracts (Planning Level)

- `broad_pass_packet`: all metric scores, per-metric reasoning/confidence, overall fit summary, floor-pass boolean
- `shortlist_decision_packet`: gate result, cutoff details, manual-approval-required flag
- `deep_dive_trigger_packet`: approved candidate + deep-research task seed
- `approval_log`: checkpoint decision, approver, rationale, timestamp

## Candidate Technology Direction (Practical + Simple)

### Runtime / Backend Approach

- option A: Python service + CLI runner
  - pros: fastest for data and AI workflow development
  - cons: less compile-time strictness than strongly typed stacks
- option B: Node/TypeScript service
  - pros: alignment if future web/API depth grows quickly
  - cons: slower setup for this data-heavy and AI-heavy first run
- recommended for this run: option A (Python + CLI-first workflow)

### Data Store Approach

- option A: SQLite
  - pros: easiest setup, single file, easy to inspect/read directly
  - cons: limited concurrent write scaling
- option B: PostgreSQL
  - pros: stronger scale and concurrency profile
  - cons: higher setup overhead now
- recommended for this run: SQLite (upgrade path to PostgreSQL if concurrency pressure appears)

### Job Orchestration / Queue Approach

- option A: simple staged batch runner + lightweight queue/retry mechanism
  - pros: simple, effective, low operational overhead
  - cons: lower observability than heavyweight workflow platforms
- option B: Temporal/Airflow class orchestration
  - pros: advanced workflow controls and observability
  - cons: unnecessary complexity for this planning scope
- recommended for this run: option A (simple and effective by default)

### Interfaces (Planning Level)

- primary: `CLI` run and artifact output flow
- optional: `API` wrapper later if needed
- deferred/not needed now: web UI

### Source Puller Direction (Locked For Part 1)

- NAICS path for this run: use official machine-readable NAICS files as the implementation source of truth
- NAICS acquisition mode: download versioned NAICS files once, store them in-project, and read them locally from code
- NAICS runtime mode: avoid live NAICS API dependency and avoid PDF parsing dependency for core intake
- NAICS maintenance mode: optional manual refresh workflow can replace the local NAICS snapshot when a newer version is intentionally adopted
- G2 path: attempt official API access first for category hierarchy retrieval
- G2 fallback path: if API access is unavailable or insufficient, use deterministic hierarchy scraping from `https://www.g2.com/categories?view_hierarchy=true`
- G2 quality rule: preserve hierarchy relations (parent/child lineage) and source provenance in every extracted row

## Implementation Sequencing Policy (Locked)

- build method is strict: `write -> run -> assert correct / fix -> move to next step`
- each step uses previous-step output as its input
- no separate `Run Controller` component is required; this method is the controller
- sequence is strict:
  1. source scraping/intake
  2. canonical dataset shaping and acceptance checks
  3. AI metric scoring
  4. shortlist gating and manual-approval routing
  5. deep-research trigger for approved candidates
- handoff implication: implementation handoff package must include per-step acceptance checks and run evidence requirements

## Stage-4 Step-2 Architecture-Level Risks And Mitigations

- risk: step coupling creates hidden failures across stages
  - mitigation: enforce explicit per-step entry/exit contracts
- risk: premature optimization into heavy infra
  - mitigation: retain simple stack unless a measured blocker appears
- risk: approval bypass in borderline shortlist cases
  - mitigation: make manual-approval state a hard requirement before deep-dive triggering
- risk: low traceability across AI decisions
  - mitigation: persist contract outputs and approval ledger artifacts at every gate

## Step-2 Follow-On Technology-Picking Checklist (Next Conversations)

Use these simple labels for upcoming deep dives:

1. `Source Puller` tech choices - status: locked
2. `Dataset Shaper` tech choices - status: in progress
3. `AI Scorer` tech choices - status: in progress
4. `Gate Keeper` tech choices - status: lightweight (no deep planning needed)
5. `Research Runner` tech choices - status: lightweight (no deep planning needed)
6. `Decision Ledger` tech choices - status: pending

## Part 2 - Dataset Shaper Technology Direction (In Progress)

### Objective

- transform raw NAICS + G2 intake into one canonical dataset with stable naming, dedupe behavior, and provenance continuity

### Candidate Approaches

- option A: Python-first shaping (`pandas` + rule engine)
  - pros: flexible for text cleanup logic
  - cons: dedupe behavior can become opaque as rule count grows
- option B: SQL-first shaping (`DuckDB` for shaping steps, SQLite for persisted run artifacts)
  - pros: transparent transformation logic, easier auditing of merges and conflicts
  - cons: requires discipline in stepwise SQL contracts

### Working Recommendation

- use a SQL-first shaping pipeline for canonicalization and dedupe traceability
- keep deterministic normalization rules as the primary mechanism
- use similarity matching only as a secondary candidate generator, never as silent auto-merge

### Dedupe Model (Planning Level)

1. exact match tier (normalized text equality)
2. rule-based alias tier (maintained synonym/alias map)
3. similarity candidate tier (thresholded suggestions routed to review queue)

### Dataset Shaper Exit Gate (Before AI Scorer Starts)

- canonical dataset meets `700+` active records post-dedupe
- every record retains source provenance
- unresolved merge/conflict queue is below agreed threshold
- output contract is stable for `AI Scorer` input without schema changes

## Part 3 - AI Scorer Technology Direction (In Progress, Plain Language)

### What this part does

- reads each business type from the cleaned dataset
- first evaluates the business as a whole candidate against your thesis and metric intent
- gives 0-3 scores for all approved metrics
- writes short reasons and confidence for each metric
- writes one short overall fit paragraph per business

### Simple approach options

- option A: one business at a time
  - good: easiest to understand and debug
  - tradeoff: slower total run time
- option B: small batches (for example 10-30 businesses per batch)
  - good: faster while still manageable
  - tradeoff: slightly more complexity in retry logic

### Recommended path

- start with small-batch scoring so runs are practical but still easy to recover
- keep prompt and output format fixed so results are consistent
- save raw model output plus cleaned output so score decisions are traceable
- enforce "reason first, score second" inside one scoring call so metric values follow a coherent view of the business

### Proposed model choices by step (draft, pending lock)

- `Source Puller`
  - primary: no LLM required
  - optional: lightweight extraction helper model only for rare parsing fallback tasks
- `Dataset Shaper`
  - primary: no LLM required
  - optional: embedding model only for duplicate-candidate suggestions (never auto-merge)
- `AI Scorer`
  - primary: balanced reasoning model for full-batch scoring
  - escalation model: stronger reasoning model only for low-confidence, invalid, or borderline outputs
- `Gate Keeper`
  - primary: deterministic rules only (no LLM for gate decisions)
- `Research Runner`
  - primary: balanced reasoning model for generating deep-research briefs
  - escalation model: stronger reasoning model for ambiguous high-impact cases
- `Decision Ledger`
  - primary: no LLM required (recording/audit component)

### AI Scorer technical flow (draft, pending lock)

1. input packet per business is loaded from canonical dataset
2. model produces a short "whole-business reasoning block" first
3. model then outputs metric scores and per-metric reasons based on that reasoning block
4. model outputs 1-2 line overall summary and confidence fields
5. schema validator checks completeness and score ranges
6. failed or low-confidence records move to rerun/escalation queue

### AI Scorer output contract (easy names)

- `business_type`
- `metric_scores` (0-3 for each metric)
- `metric_reasoning` (1-2 short sentences + confidence)
- `overall_fit_summary` (short paragraph)
- `passes_floor` (true/false)

### Quality checks before moving to Gate Keeper

- every business has all metric scores filled
- every metric has a short reason and confidence
- no invalid scores outside 0-3
- rerun queue exists for failed or incomplete model responses

## Stage-4 Step-3 Research Runner Design (Branch Draft For Origin Approval)

### Research Runner Role

Produces deep-research briefs for every approved shortlist candidate. Runs after Gate Keeper approval and before founder manual review.

### Input Contract

Per candidate, Research Runner receives:
- canonical record from dataset (`record_id`, `business_type`, `definition`, `business_model_archetype`, `primary_customer_type`, `revenue_model`)
- AI Scorer broad-pass packet (`metric_scores`, `metric_reasoning`, `overall_fit_summary`, `passes_floor`)

### Automation Approach

- one structured prompt per candidate producing all 8 research sections in a single response
- prompt includes the full broad-pass packet as context so deep research can reference and challenge specific scores
- model must produce new/deeper content, not restate broad-pass reasoning
- per-section confidence labels (low / medium / high) are mandatory
- thesis stress test section must contain at least one counterargument per metric scored >= 2

### Model Selection

- primary: balanced reasoning model (same tier as AI Scorer primary)
- escalation trigger: when Research Runner self-reports low confidence on 3+ of 8 sections, rerun with stronger model
- failure handling: incomplete briefs enter rerun queue with adjusted prompting; persistent failures flagged for manual review

### Output Contract Per Candidate

- `candidate_id`: links to canonical `record_id`
- `market_landscape_brief`: TAM, growth, segments, geography (+ confidence)
- `competitive_intel_summary`: named players, structure, moats, gaps (+ confidence)
- `unit_economics_estimate`: pricing, margins, CAC, LTV (+ confidence)
- `regulatory_scan`: barriers, costs, risk level, variance flags (+ confidence)
- `operating_model_brief`: delivery, team, tech, dependencies, small-team fit (+ confidence)
- `thesis_stress_test`: per-metric supporting argument + counterargument + revised confidence
- `speed_to_revenue_assessment`: timeline, MVP, prerequisites, blockers (+ confidence)
- `risk_scan`: top risks with severity/likelihood + disqualifier flags (+ confidence)
- `research_completeness_pass`: boolean (true if all 8 sections pass validation)
- `escalation_triggered`: boolean

### Validation Rules

1. all 8 sections must be non-empty
2. each section must have a confidence label
3. thesis stress test must have counterarguments for metrics >= 2
4. risk scan must identify at least one risk
5. no section may be a near-duplicate of broad-pass reasoning (semantic check)

### No Live Web Research For This Run

Consistent with Stage-2 evidence strategy: AI world-knowledge provides the evidence base. Depth improvement over broad-pass comes from structured deep prompting, explicit counterarguments, and calibrated confidence — not real-time web scraping.

### Sequencing In Implementation Flow

Research Runner sits at position 5 in the implementation sequence:
1. source scraping/intake
2. canonical dataset shaping
3. AI metric scoring
4. shortlist gating and manual-approval routing
5. **deep-research trigger for approved candidates** ← Research Runner
6. founder manual review and final decision

## Stage-4 Step-4 Implementation Deliverables And Execution Protocol

### Deliverable Set For Build Agents

1. `founder-plan-deliverable`
- plain-language decision guide covering the full planning logic and approval gates
- includes what was decided, what is optional, and how final candidate decisions are made

2. `implementer-build-handoff`
- end-to-end technical plan for building the pipeline in phases
- includes component contracts, data artifacts, validation gates, and acceptance tests

3. `section-handoffs`
- focused implementation briefs per build section:
  - `source-puller`
  - `dataset-shaper`
  - `ai-scorer`
  - `gate-keeper`
  - `research-runner`
  - `decision-ledger`

### Agent Execution Method (Locked)

Every build section must follow this strict loop:

1. `write`: implement only the current section scope
2. `run`: execute section tests/run checks
3. `verify`: confirm section acceptance criteria are met
4. `advance_or_fix`:
- if pass -> freeze artifacts and move to next section
- if fail -> fix and rerun until pass

Rule: no section is allowed to proceed on "assumed correctness."

### Per-Section Acceptance Gate Contract

Each section handoff must define:
- input artifacts required from previous section
- output artifacts produced for next section
- run command(s) and expected outcome
- explicit pass/fail checks
- known failure modes and retry/fix guidance

### Context And Scope Management For Multi-Agent Execution

- assign one active context file per section agent chat
- each section agent is scoped to one section only; no cross-section redesign authority
- origin build coordinator agent is the only canonical integrator
- section agent return package must include:
  - what changed
  - what passed
  - unresolved blockers
  - exact artifacts produced
- when a section is complete, archive/close its context and open the next section context

### Suggested Build Order (Must Follow)

1. `source-puller`
2. `dataset-shaper`
3. `ai-scorer`
4. `gate-keeper`
5. `research-runner`
6. `decision-ledger`

This order is mandatory because each step consumes the previous step's verified outputs.

## Stage-4 Step-1 Dataset Prerequisites (Updated)

- run type: one-time initial dataset build for this decision cycle
- minimum canonical dataset size before scoring: `700+` business types
- intake objective: unify the two locked inputs into one canonical dataset with provenance
- scope note: no refresh policy is required for this run
- scope note: founder-thesis tags are deferred until after intake dataset is assembled
- scope note: a dedicated scoreability column is not required in initial dataset schema

## Stage-4 Step-1 Source-Unification Planning Requirements

- define canonicalization rules for naming and category boundaries
- define deduplication and normalization checks before scoring pipeline entry
- define dataset usefulness checks at planning level (completeness, variety, duplicate control)

## Stage-4 Step-1 Source Inputs Locked For This Run

- input A: `NAICS PDF` as broad taxonomy backbone
- input B: `G2 category hierarchy` as modern software/service category expansion

Input reference:

- `https://www.g2.com/categories?view_hierarchy=true`

## Stage-4 Step-1 Input-Specific Extraction and Unification Plan

- NAICS extraction: parse classification entries to structured category rows
- G2 extraction: crawl hierarchy categories and preserve parent-child context
- shared intake: write both sources into one raw intake structure with provenance
- normalization: apply naming standardization and synonym consolidation
- dedupe: merge near-identical concepts and preserve merge history
- canonical output: one normalized business-type record per unique opportunity concept

## Stage-4 Step-1 Acceptance Gate

- final canonical dataset includes `700+` active records post-dedupe
- each record includes source provenance
- both locked inputs (NAICS + G2) are represented in canonical output
- dataset is ready for downstream AI metric scoring without requiring schema changes

## Stage-4 Step-1 Initial Dataset Contract (Planning Level)

Required initial intake fields to support downstream scoring setup:

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

Constraint notes:

- do not include `founder_thesis_fit_tags` in the initial intake contract
- do not include a dedicated `scoreability` field in the initial intake contract
- maintain one-time-run assumption for this cycle (no refresh subsystem design required)

## Stage-4 Step-1 Working File References

Files explicitly in use for this knot:

- branch context: `planning-system/project-runs/business-discovery-engine/active-contexts/branch-stage4-step1-dataset-gathering-context.md`
- product plan linkage: `planning-system/project-runs/business-discovery-engine/plans/product-strategy-plan.md`
- technical plan (this file): `planning-system/project-runs/business-discovery-engine/plans/technical-implementation-plan.md`

Files expected to be updated when returning this knot to origin:

- `planning-system/project-runs/business-discovery-engine/active-contexts/master-memory.md`
- `planning-system/project-runs/business-discovery-engine/active-contexts/origin-chat-context.md`
