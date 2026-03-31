# File Routing Reference

## Purpose

Give the agent a deterministic map of which planning-system files to consult in each situation.

## Always-Consult Baseline

When available, read in this order:

1. active `master-memory.md` for durable continuity
2. active chat context file for current stage and knot
3. this routing reference for where to go next

## Situation -> File Lookup

- start or restart planning chat:
  - `prompts/01_start-planning-chat.md`
  - current seed input file
- decide branch vs stay in origin:
  - `guides/agent-operating-system.md`
- uncertain which context file to attach:
  - `guides/context-file-standard.md`
- context files feel bloated or stale:
  - `guides/context-hygiene-protocol.md`
- check if plan is ready for execution handoff:
  - `guides/plan-completion-criteria.md`
- validate system behavior before stage start:
  - `guides/system-self-test.md`
- send work to branch:
  - `prompts/02_handoff-to-new-agent.md`
  - `templates/branch-handoff-template.md` (or project-run branch brief)
- return branch work to origin:
  - `prompts/03_return-to-origin-agent.md`
- create or refresh canonical files:
  - `templates/master-memory-template.md`
  - `templates/active-chat-context-template.md`
  - `templates/stage-brief-template.md`
- initialize or refresh clean plan-only artifacts:
  - `templates/product-strategy-plan-template.md`
  - `templates/technical-implementation-plan-template.md`

## Full System Catalog (Current Tree)

- root:
  - `START_HERE.md`
- guides:
  - `guides/agent-operating-system.md`
  - `guides/context-file-standard.md`
  - `guides/context-hygiene-protocol.md`
  - `guides/file-routing-reference.md`
  - `guides/plan-completion-criteria.md`
  - `guides/system-self-test.md`
- prompts:
  - `prompts/01_start-planning-chat.md`
  - `prompts/02_handoff-to-new-agent.md`
  - `prompts/03_return-to-origin-agent.md`
- templates:
  - `templates/master-memory-template.md`
  - `templates/active-chat-context-template.md`
  - `templates/stage-brief-template.md`
  - `templates/branch-handoff-template.md`
  - `templates/product-strategy-plan-template.md`
  - `templates/technical-implementation-plan-template.md`
- seed inputs:
  - `seed-inputs/business-discovery-seed.md`

## Scope Rule

Treat `guides/`, `prompts/`, and `templates/` as reusable system assets.
Treat `project-runs/<project-slug>/` as project-specific implementation state.

## Behavioral Rule

If a relevant file is not attached, ask for it explicitly.
If the task can proceed safely without it, continue with clearly stated assumptions.
