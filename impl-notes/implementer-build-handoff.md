# Implementer Build Handoff

## Purpose

Execution-focused technical handoff for build agents to implement the system in strict verified phases.

## Canonical Package Entry

Start from:

- `handoffs/execution-package-index.md`
- `handoffs/execution-master-context.md`

## Build Order (Mandatory)

1. source-puller
2. dataset-shaper
3. ai-scorer
4. gate-keeper
5. research-runner

Section handoffs:

- `handoffs/handoff-source-puller.md`
- `handoffs/handoff-dataset-shaper.md`
- `handoffs/handoff-ai-scorer.md`
- `handoffs/handoff-gate-keeper.md`
- `handoffs/handoff-research-runner.md`

## Execution Protocol (Mandatory)

For each phase:

1. plan: think through the implementation approach, identify sub-parts if the phase is complex, and get the plan approved before writing any code
2. write: implement only the approved plan scope
3. run: execute and test
4. verify: confirm acceptance criteria are met
5. if pass -> freeze outputs and move forward
6. if fail -> fix and rerun until pass

If the plan step reveals the phase should be broken into sub-parts, execute each sub-part through its own write → run → verify cycle before moving to the next sub-part. Only advance to the next phase after all sub-parts pass.

No phase may begin until previous phase has a verified pass package.

## Phase Return Package (Required)

- scope completed
- run commands executed
- verification evidence
- pass/fail status
- produced artifacts
- known issues (if any)
- recommendation: proceed or hold

## Integration Rule

Only the origin coordinator integrates phase outputs and authorizes progression.
