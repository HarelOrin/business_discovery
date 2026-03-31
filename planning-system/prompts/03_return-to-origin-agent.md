 # Return To Origin Agent Prompt
 
 Attach this file plus:
 
 - `master-memory.md`
 - the origin chat context file
 - the branch result file or copied branch result
 
 Use this prompt:
 
 ```text
 We are returning from a branch planning chat to the origin planning chat.
 
 Rules:
 - Treat the origin chat as the canonical coordinator of the plan.
 - Incorporate the attached branch result into the main planning process.
 - Update persistent memory and active context to reflect what was learned.
 - Distinguish between:
   1. new decisions
   2. new options
   3. new risks
   4. unresolved questions
 - If the branch result is insufficient, say exactly what is missing and whether to re-branch.
 - If the branch result resolves the intended knot, move the plan forward conversationally.
- Keep the origin chat meta-level and decision-focused; recommend new branching if detail load is becoming noisy.
- Include a context footer only when required files are missing/mismatched or when you are explicitly instructing a new branch.
 
 Start by:
 1. summarizing what came back from the branch
 2. stating what changed in the main plan
 3. identifying the next knot to resolve
 ```
