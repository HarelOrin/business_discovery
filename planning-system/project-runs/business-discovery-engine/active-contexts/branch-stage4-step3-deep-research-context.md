# Active Chat Context

## Chat Name

branch-stage4-step3-deep-research-context

## Purpose

Design and close Stage-4 Step-3 deep-research planning for top candidates: what must be researched, what is manual vs automatable, and practical operating guidance for each path.

## Relationship To Origin Chat

- branch
- if branch, what knot does it own: Stage-4 Step-3 deep-research workflow planning only

## Current Stage

- stage: stage-4-technical-planning-and-handoff
- objective: produce a decision-ready deep-research workflow package before final handoff packaging

## Scope Boundaries

- in scope: research scope definition for top candidates, manual vs automatic split, practical how-to guidance, automation approach at planning level, and quality gates
- out of scope: changing Stage-1/2/3 decisions, reworking Step-1 dataset lock, deep implementation coding details, final Step-4 handoff package drafting

## Current Knot

Define a complete, practical research playbook for top candidates that clearly separates manual work from automatable work and explains how each should run.

## Latest Relevant Decisions

- Stage-4 Step-1 dataset plan is complete and approved as one-time run with 700+ canonical records
- source lock for this run is NAICS PDF plus G2 category hierarchy
- Stage-4 Step-2 app architecture package is treated as good enough for progression
- workflow stays planning-level and practical, avoiding low-level implementation detail

## Files To Update In This Branch

- `planning-system/project-runs/business-discovery-engine/plans/product-strategy-plan.md`
- `planning-system/project-runs/business-discovery-engine/plans/technical-implementation-plan.md`
- expected at return-to-origin integration: `planning-system/project-runs/business-discovery-engine/active-contexts/master-memory.md`
- expected at return-to-origin integration: `planning-system/project-runs/business-discovery-engine/active-contexts/origin-chat-context.md`

## Expected Output

A branch return package that provides:
- complete list of what must be researched for top candidates
- manual vs automatic research split with rationale
- practical manual how-to instructions per manual research category
- practical automation approach per automatable research category
- explicit yes/no decisions for origin approval

## Return Condition

Return to origin only after Stage-4 Step-3 is sufficiently planned as a complete decision package with no major blocker for Step-4 final handoffs.

## Progress Tracker

- status: complete — ready for return to origin
- completed:
  - branch context created
  - research scope defined (8 dimensions: R1-R8)
  - manual research track defined (5 tasks: M1-M5 with how-to)
  - automated research track defined (8 tasks: A1-A8 with automation approach)
  - quality gate defined (10-point completeness criteria)
  - approval checklist prepared (8 yes/no decisions for origin)
  - product-strategy-plan.md updated with Step-3 research scope
  - technical-implementation-plan.md updated with Research Runner design
  - return package prepared
- remaining: none — awaiting origin approval

## File Routing Hints

- routing reference: `planning-system/guides/file-routing-reference.md`
- if uncertain about branching: consult `planning-system/guides/agent-operating-system.md`
- if uncertain about attachments: consult `planning-system/guides/context-file-standard.md`
