 # Iterative Planning System
 
 This folder is a reusable planning operating system for multi-week, multi-agent plan building.
 
 Use it when you want to:
 
 - build a plan conversationally with strong human intervention
 - split work across multiple agent chats without losing continuity
 - maintain semantic memory across long conversations
 - know exactly when to branch to a new agent and when to return
 - finish product/planning requirements before implementation planning
 
 ## Core Model
 
 One plan has:
 
 - one `master-memory` file
 - one active context file per live chat
 - optional stage briefs and handoff briefs
 - one origin chat that owns the canonical planning state
 - branch chats that explore subproblems and report back
 
## Template vs Project Run

Keep reusable system assets separate from each project run.

- reusable template assets live in: `guides/`, `prompts/`, `templates/`
- each real project plan lives in: `project-runs/<project-slug>/`
- each project run should contain its own `active-contexts/` and project seed file

This separation keeps the planning system reusable while each plan remains a single coherent implementation.

 ## Recommended Use Order
 
 1. Attach `prompts/01_start-planning-chat.md`
 2. Attach `seed-inputs/business-discovery-seed.md` or your new seed
 3. Create `active-contexts/origin-chat-context.md` from the template
 4. Create `active-contexts/master-memory.md` from the template
 5. Start the origin chat
 
 ## Required Attachment Rule
 
 Every message you send in a planning chat should include at least one attached context file.
 
 Make the file name obvious to the current chat, for example:
 
 - `origin-chat-context.md`
 - `requirements-stage-context.md`
 - `technical-planning-context.md`
 - `handoff-to-market-research-agent.md`
 
 The attached file should reflect the current purpose of the chat.

## Attachment Reminder Contract

Every planning-agent response should end with a short context reminder block:

- whether required context appears present or missing
- exact files to attach next
- exact files to send for any branch handoff or return-to-origin loop

## Context Hygiene Contract

The planning agent should actively prevent file bloat:

- merge duplicate decisions into canonical files
- remove stale or superseded open knots
- archive branch files when their return package is accepted
- keep only currently useful context in active files
 
 ## File Map
 
 - `prompts/01_start-planning-chat.md`
 - `prompts/02_handoff-to-new-agent.md`
 - `prompts/03_return-to-origin-agent.md`
 - `guides/agent-operating-system.md`
 - `guides/context-file-standard.md`
- `guides/file-routing-reference.md`
- `guides/context-hygiene-protocol.md`
 - `guides/plan-completion-criteria.md`
- `guides/system-self-test.md`
 - `templates/master-memory-template.md`
 - `templates/active-chat-context-template.md`
 - `templates/stage-brief-template.md`
 - `seed-inputs/business-discovery-seed.md`
