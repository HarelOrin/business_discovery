# Master Memory

## Mission

Build a plan conversationally, with strong human intervention, for a business-opportunity discovery system and only later for the AI-enabled implementation of that system.

## Core Directives

- do not generate the whole plan up front
- resolve one knot at a time with the user
- separate product/requirements planning from technical implementation planning
- preserve continuity through context files, not chat history alone
- use branch chats only when they clearly help
- always make handoffs and return loops explicit

## System File Routing
!! READ THESE FILES AS CONTEXT IF RELEVANT TO KNOW HOW TO WORK PROPERLY !!
- routing reference: `planning-system/guides/file-routing-reference.md`
- operating rules: `planning-system/guides/agent-operating-system.md`
- context attachment rules: `planning-system/guides/context-file-standard.md`
- hygiene protocol: `planning-system/guides/context-hygiene-protocol.md`
- completion criteria: `planning-system/guides/plan-completion-criteria.md`

## Origin Chat

- chat purpose: build the plan phase by phase
- canonical owner: origin planning chat

## Connected Chats

- `branch-stage4-step1-dataset-gathering-context` (stage-4 step-1 dataset gathering knot; return package delivered)
- `branch-stage4-step2-app-architecture-context` (stage-4 step-2 app architecture knot; return package delivered)
- `branch-stage4-step3-deep-research-context` (stage-4 step-3 deep-research knot; return package delivered)

## Current Stage

- stage name: stage-4-technical-planning-and-handoff
- stage goal: define a high-level technical planning package and clean execution handoff without diving into implementation-level detail

## Durable Decisions

- this planning system should be reusable for future plans
- each planning message should include at least one attached context file
- file names should clearly match the current chat purpose
- concept seed intake is complete for business discovery engine
- planning sequence is locked: product/requirements -> research-backed decision design -> technical planning -> execution handoff
- founder preference captured: prioritize opportunities with very large customer pools and room to scale despite incumbents
- founder preference captured: prefer no employees or a small team of skilled professionals, avoid low-skill labor-heavy operating models
- founder preference captured: target high-margin offerings and avoid commodity off-the-shelf product dependence
- founder preference captured: "boring" or crowded categories are acceptable when economics and demand are strong
- stage-1 lens expanded to include low starting investment and speed-to-scale as explicit fit dimensions
- stage-1 decision style: treat all candidate filters as valid tagging dimensions; assess each business individually across all filters instead of early elimination
- prioritization approach: capture broad candidate pool first, then prioritize in a later method/gate rather than using hard ranking as the first pass
- per-metric output requirement: every assessment must include (a) numeric score from 0-3 and (b) a short AI reasoning string that verbally ranks the metric and explains alignment with founder vision
- scoring output format locked: reasoning should be 1-2 sentences with a confidence label, plus one small overall AI paragraph per business summarizing full vision alignment
- documentation track locked: maintain clean plan-only artifacts in parallel with context artifacts (product/idea plan now, technical plan matured later)
- stage-1 draft schema created (v0.1): canonical metric set and shared 0-3 verbal-rank mapping added to product strategy plan for consistent profiling
- process decision: avoid Stage-1 rabbit-hole detail; use lean closure gate and move quickly to next stages once schema is good enough
- stage-1 closeout approved with strategic floor rules: `market_headroom`, `margin_quality`, and `distribution_efficiency` must be at least `Solid` (score >= 2)
- stage-2 simplification approved: use AI world-knowledge/context-based opinion scoring for broad pass; reserve detailed evidence research for shortlisted winners only
- stage-2 broad-pass packet approved with required fields: business type, all metric scores, per-metric reasoning+confidence, overall fit summary, and floor-pass boolean
- stage-3 started by founder direction to maintain planning momentum; remaining stage-2 confidence rubric details are treated as lightweight subordinate refinement
- stage-3 shortlist mode approved: `score-threshold` (all candidates above cutoff advance, no fixed-N cap)
- stage-3 cutoff model approved: two-part gate (`C`) = floor pass + non-floor average cutoff
- stage-3 numeric cutoff approved: non-floor metric average must be `>= 1.9` for shortlist advancement (in addition to floor pass)
- stage-3 human gate approved: shortlist candidates under `2.5` non-floor average require manual founder approval; `>= 2.5` auto-approve to deep-dive
- process direction reinforced: avoid marginal threshold debates; move forward with good-enough planning decisions
- stage-4 architecture style approved: `origin + specialized branch agents` with origin as canonical decision owner and branches for narrow scoped execution
- founder-defined stage-4 sequence locked: dataset planning -> app architecture planning -> deep-research workflow planning -> dual deliverables + explicit handoff contracts
- stage-4 step-1 dataset direction approved in branch package: one-time run (no refresh subsystem design) with `700+` canonical business types before scoring
- stage-4 step-1 source lock for this run: `NAICS PDF` + `G2 category hierarchy` (`https://www.g2.com/categories?view_hierarchy=true`)
- stage-4 step-1 unification model approved: shared intake for both sources, normalization, deduplication, provenance retention, and canonical output as one record per business-type concept
- stage-4 step-1 schema simplification approved: initial intake excludes `founder_thesis_fit_tags` and excludes a dedicated `scoreability` column
- stage-4 step-1 acceptance gate approved: `700+` active post-dedupe records, provenance coverage, representation from both locked sources, and low merge/conflict backlog
- stage-4 step-2 architecture direction approved in branch: one orchestrator flow with specialized stage-role modules
- stage-4 step-2 interface direction approved in branch: CLI-first; no web interface required for this run
- stage-4 step-2 data store direction approved in branch: favor easiest setup and readable storage for this run (SQLite-first path)
- stage-4 step-2 orchestration preference reinforced: simple and effective queue/batch orchestration over heavy platforms
- stage-4 step-2 is treated as good-enough complete for planning progression; unresolved technology refinements are implementation-phase details
- implementation policy approved: each major step must be implemented fully and run-validated before implementing the next step
- source puller decision approved in branch: NAICS intake should use official machine-readable files stored locally in-project as source-of-truth for implementation
- source puller decision approved in branch: NAICS intake should avoid live API dependency and avoid PDF parsing dependency for core extraction
- source puller decision approved in branch: G2 retrieval is API-first if access is available; deterministic hierarchy scraping is fallback
- step-2 checklist progress in branch: `Source Puller` locked; `Dataset Shaper` and `AI Scorer` technology directions are active in-progress knots
- AI scoring draft rule added in branch: per-business whole-candidate reasoning must precede metric scoring and short summary output
- architecture simplification approved in branch: no separate `Run Controller` component; use strict implementation method as control mechanism
- implementation method locked in branch: `write -> run -> assert correct / fix -> move to next`, with each step consuming prior-step output
- stage-4 step-3 deep-research package returned as complete and decision-ready
- stage-4 step-4 execution policy drafted: final handoffs include founder summary, implementer coding plan, and per-section handoff briefs with strict pass-before-advance enforcement
- execution handoff package prepared as standalone artifacts under `project-runs/business-discovery-engine/handoffs/` with canonical execution index and per-phase handoffs

## Open Knots

- important: confirm final planning closeout and authorize first execution kickoff (`source-puller`)
- important: run execution from standalone handoff package only and avoid dependency on planning-history artifacts
- optional: define preferred naming convention for future branch chats

## Handoff History

- branch handoff complete: `branch-stage4-step1-dataset-gathering-context` returned stage-4 step-1 package covering source lock (NAICS+G2), one-time 700+ dataset target, schema constraints, unification strategy, and acceptance gate
- branch active: `branch-stage4-step2-app-architecture-context` drafting stage-4 step-2 architecture package with explicit approvals and implementation sequencing policy

## Completion Status

- status: not ready
- blockers remaining: final origin authorization to start execution is pending
- next milestone: start implementation with `source-puller` using canonical execution package


