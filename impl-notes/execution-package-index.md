# Execution Package Index

## Canonical Execution Files

Use only the files listed below for implementation execution.

### Core Execution Context

1. `execution-master-context.md` — locked decisions, contracts, founder thesis, model strategy, and execution protocol
2. `execution-plan-overview.md` — high-level outcome, phases, manual vs automated split, and completion definition
3. `implementer-build-handoff.md` — implementer entry point with build order, execution protocol, and phase return requirements
4. `founder-final-plan-deliverable.md` — founder-facing plan summary for final directional approval

### Per-Phase Handoffs

5. `handoff-source-puller.md`
6. `handoff-dataset-shaper.md`
7. `handoff-ai-scorer.md`
8. `handoff-gate-keeper.md`
9. `handoff-research-runner.md`

## Strict Rule

- Implementation agents must execute from this package only.
- Do not depend on prior planning chat history.
- Do not require access to planning-system context artifacts to proceed.

## Execution Order

1. source-puller
2. dataset-shaper
3. ai-scorer
4. gate-keeper
5. research-runner

## Execution Loop (Mandatory)

For each phase:

1. plan: think through the implementation approach, identify sub-parts if the phase is complex, and get plan approved before writing any code
2. write: implement only the approved plan scope
3. run: execute and test
4. verify: confirm acceptance criteria are met
5. if pass -> advance to next phase
6. if fail -> fix and rerun until pass

If the plan step reveals the phase should be broken into sub-parts, execute each sub-part through its own write -> run -> verify cycle before moving to the next sub-part. Only advance to the next phase after all sub-parts pass.

No phase may start before previous phase has a verified pass package.
