# Active Chat Context

## Chat Name

branch-stage4-step1-dataset-gathering-context

## Purpose

Design and close Stage-4 Step-1 dataset-gathering planning for the Business Discovery Engine, with practical decisions on canonical unit, schema, source breadth strategy, and dataset quality sufficiency for downstream scoring.

## Relationship To Origin Chat

- branch
- if branch, what knot does it own: Stage-4 Step-1 dataset-gathering plan only

## Current Stage

- stage: stage-4-technical-planning-and-handoff
- objective: finalize a one-time, decision-ready plan for assembling an initial large business-type dataset before architecture planning

## Scope Boundaries

- in scope: dataset unit definition, required initial schema, high-level source strategy, dedupe/normalization quality controls, variety/blindspot checks, and minimum volume target
- out of scope: application architecture details, implementation coding details, deep-research workflow design, and later-stage handoff packaging

## Current Knot

Lock the one-time initial dataset-gathering plan for 700+ business types, including a practical multi-source intake strategy, unification rules, and quality checks to reduce blindspots before Stage-2/3 scoring.

## Latest Relevant Decisions

- use one canonical record per business type as the dataset unit
- prioritize one-time dataset build for this run; no recurring refresh policy is required
- target at least 700 business types in the initial canonical dataset
- lock source inputs for this run to NAICS PDF + G2 category hierarchy
- defer founder-thesis tagging until after initial dataset collection
- simplify readiness treatment during collection; do not require a dedicated scoreability column at intake stage
- remain high-level planning only and avoid implementation detail

## Files To Update In This Branch

- `planning-system/project-runs/business-discovery-engine/plans/product-strategy-plan.md`
- `planning-system/project-runs/business-discovery-engine/plans/technical-implementation-plan.md`
- expected at return-to-origin integration: `planning-system/project-runs/business-discovery-engine/active-contexts/master-memory.md`
- expected at return-to-origin integration: `planning-system/project-runs/business-discovery-engine/active-contexts/origin-chat-context.md`

## Expected Output

A branch return package that provides:
- one recommended Stage-4 Step-1 dataset strategy
- practical source-family plan for 700+ initial business types
- required canonical schema fields for initial intake only
- quality controls for usefulness and variety coverage
- explicit yes/no decisions for origin approval

## Return Condition

Return to origin only after Stage-4 Step-1 is sufficiently planned as a complete decision package and no major open blocker remains for this knot.

## Progress Tracker

- status: complete - returned to origin
- completed:
  - branch active-context file created and activated
  - product and technical plan files updated with one-time `700+` dataset direction
  - initial source-family strategy and intake schema constraints documented
  - source lock finalized for this run: NAICS PDF + G2 hierarchy
  - input-specific extraction/unification strategy and closure gate finalized for origin approval
- remaining:
  - none

## File Routing Hints

- routing reference: `planning-system/guides/file-routing-reference.md`
- if uncertain about branching: consult `planning-system/guides/agent-operating-system.md`
- if uncertain about attachments: consult `planning-system/guides/context-file-standard.md`
