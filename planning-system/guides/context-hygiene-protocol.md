# Context Hygiene Protocol

## Purpose

Keep planning files useful, current, and compact so the plan does not become overpopulated.

## Hygiene Rules

- maintain one canonical location for each durable decision
- merge duplicates instead of repeating them across files
- remove stale open knots once resolved or superseded
- mark assumptions explicitly, then replace with decisions when approved
- archive branch files after their return package is accepted by origin chat

## Minimum Cleanup Cadence

Run a cleanup check at least:

- after each stage checkpoint
- after each branch return
- before any execution handoff decision

## Cleanup Checklist

1. remove duplicate decisions across active files
2. prune or rewrite vague open knots
3. verify current stage and next milestone are accurate
4. verify connected chats list only active or archived branches
5. ensure completion status matches actual blockers

## Safe Deletion Rule

Do not delete information that may still be needed.

When in doubt:

- move old content to an archive file under `project-runs/<project-slug>/archive/`
- leave a short pointer in the active file

## Hygiene Reporting Rule

To avoid polluting the chat with repetitive process text:

- run hygiene checks behind the scenes at the required cadence
- include an explicit `Hygiene check` block in chat only when:
  - a stage checkpoint is being closed now
  - a branch return is being integrated now
  - the user asks for a hygiene/status audit
