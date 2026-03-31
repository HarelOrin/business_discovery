# Planning System Self-Test

## Goal

Verify the planning system behaves correctly before starting a new stage.

## Test 1: File Routing Awareness

Ask the agent: "Which files should you consult for branching, hygiene, and completion readiness?"

Pass condition:

- names `file-routing-reference.md`
- correctly points to `agent-operating-system.md`, `context-hygiene-protocol.md`, and `plan-completion-criteria.md`

## Test 2: Conditional Attachment Reminder

Send one message with correct required context attached.

Pass condition:

- no generic "attach next" block appears

Then send one message without required context.

Pass condition:

- agent asks for missing files and provides exact attach instructions

## Test 3: Branch Trigger Autonomy

Give the agent a deliberately overloaded subproblem in origin chat.

Pass condition:

- agent proposes branching without explicit user request
- includes exact branch prompt and required file pack

## Test 4: Return Trigger Autonomy

Simulate a branch result that resolves its knot.

Pass condition:

- branch recommends return-to-origin with exact return pack
- origin incorporates result and updates open knots

## Test 5: Context Hygiene

Create duplicate decisions and stale knots in active files.

Pass condition:

- agent proposes merge/prune/archive actions
- active files become cleaner without losing essential traceability

## Test 6: Stage Intro Behavior

Start a fresh stage prompt.

Pass condition:

- agent introduces purpose and considerations first
- avoids immediate lock-in language

## Release Gate

Proceed to new stage only when all tests pass or accepted gaps are explicitly documented.
