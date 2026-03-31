 # Context File Standard
 
 ## Goal
 
 Make it obvious which file should be attached to which chat, while preserving semantic continuity.
 
 ## Required File Types
 
 ### 1. Master Memory
 
 Suggested file name:
 
 - `active-contexts/master-memory.md`
 
 This file stores:
 
 - mission
 - core directives
 - durable decisions
 - connected chats
 - open knots
 - completion status
 
 ### 2. Active Chat Context
 
 Suggested file names:
 
 - `active-contexts/origin-chat-context.md`
 - `active-contexts/requirements-stage-context.md`
 - `active-contexts/technical-planning-context.md`
 - `active-contexts/branch-market-research-context.md`
 
 This file stores:
 
 - why this chat exists
 - current stage
 - scope boundaries
 - immediate next knot
 - recent decisions relevant to this chat
 
 ### 3. Stage Brief
 
 Suggested file names:
 
 - `handoffs/stage-01-brief.md`
 - `handoffs/stage-02-brief.md`
 
 Use when a chat is focused on a stage or milestone.
 
 ### 4. Branch Handoff Brief
 
 Suggested file names:
 
 - `handoffs/branch-pricing-research.md`
 - `handoffs/branch-agent-architecture.md`
 
 Use when sending work to another agent chat.

### 5. Plan-Only Artifacts (Separate Track)

Suggested file names:

- `plans/product-strategy-plan.md`
- `plans/technical-implementation-plan.md`

These files are not chat-context memory. They store clean, execution-facing plan content:

- product/strategy intent, requirements, decision model, stage gates, and approved outcomes
- technical architecture, agent roles, data/context flows, and implementation sequencing

Maintain these in parallel with context files so execution handoff does not depend on reconstructing chat history.
 
 ## Attachment Rule
 
 Every user message in a planning workflow should include at least one attached context file.
 
 Best practice:
 
 - always attach `master-memory.md`
 - always attach the current active chat context file
 - attach a stage brief or branch brief when relevant

If required files are missing, the agent should explicitly request them and continue with bounded assumptions.

## Conditional End-Of-Reply Attachment Reminder

Planning replies should include an attachment reminder only when:

- required context is missing or likely mismatched
- a branch handoff is being proposed now
- a return-to-origin action is being proposed now

When shown, include only the relevant items for that specific situation.
 
 ## Naming Rule
 
 File names should reveal the chat purpose immediately without opening the file.
