# Handoff — AI Scorer Sub-part A: Scoring Infrastructure

## Scope

Build the core scoring infrastructure: LLM client, batch manager, response parser, and validator. Produce a working test run of 1 batch (20 businesses) to confirm the pipeline works end-to-end before the full run.

## Inputs

- `data/output/canonical_dataset.json` — 3,606 canonical business type records
- `src/ai_scorer/prompts/scoring_system_prompt.txt` — locked system prompt
- `src/ai_scorer/prompts/scoring_user_prompt_template.txt` — locked user prompt template
- `impl-notes/execution-master-context.md` — locked metrics, scoring rules, founder thesis

## Pre-requisites

- OpenAI API key in `.env` file at project root (`OPENAI_API_KEY=...`), loaded via `python-dotenv`
- `openai` and `python-dotenv` packages installed (already in `requirements.txt`)

## Required Work

### 1. LLM Client (`src/ai_scorer/llm_client.py`) — PARTIALLY BUILT

Existing implementation at `src/ai_scorer/llm_client.py` (standard API mode).
Must be refactored/extended to support OpenAI Batch API workflow:

- Batch API file preparation (JSONL format with custom_id per request)
- Batch job submission via `client.batches.create()`
- Batch status polling via `client.batches.retrieve()`
- Result file download and parsing
- Model: `o3` (reasoning model — use `role: "developer"` instead of `role: "system"`)
- JSON mode enabled (`response_format={"type": "json_object"}`)
- Log token usage from batch results for cost tracking

### 2. Batch Manager (`src/ai_scorer/batch_manager.py`) — PARTIALLY BUILT

Existing implementation handles dataset loading, batching, SQLite tracking, and resume.
Review and adapt for Batch API workflow (tracking batch job IDs instead of real-time status).

- Load canonical dataset from JSON
- Split into batches of 5 records each
- SQLite tracking table (`data/output/scoring_progress.db`):
  - `batch_id`, `record_ids` (JSON array), `status` (pending/in_progress/completed/failed), `attempt_count`, `created_at`, `completed_at`
- Resume support: on restart, skip completed batches and retry failed/pending ones
- Per-record tracking table:
  - `record_id`, `batch_id`, `scoring_status` (pending/scored/failed/escalated), `attempt_count`

### 3. Response Parser (`src/ai_scorer/response_parser.py`) — PARTIALLY BUILT

Existing implementation handles JSON parsing and record mapping. Review for compatibility with Batch API result format.

- Parse JSON response from LLM
- Extract each scored business from the `scored_businesses` array
- Map back to original `record_id` to confirm all batch items are present
- Handle malformed JSON gracefully (log error, mark batch as failed)

### 4. Response Validator (`src/ai_scorer/response_validator.py`) — BUILT

Existing implementation is complete and tested. Validates all 12 metrics, scores, labels, confidence, summaries.

- Per-business validation:
  - All 12 metrics present
  - All scores are integers in 0-3
  - All reasoning strings are non-empty and contain a verbal rank label (Weak/Emerging/Solid/Strong)
  - All confidence values are one of: low, medium, high
  - `whole_business_reasoning` is non-empty
  - `overall_fit_summary` is non-empty
  - `business_model_archetype`, `primary_customer_type`, `revenue_model` are non-empty
- Return: list of validation errors per record, or empty list if valid
- Records with validation errors → flagged for rerun queue

### 5. Main Orchestrator Entry Point (`src/ai_scorer/score_businesses.py`) — NEEDS REFACTOR

Existing implementation uses real-time sequential API calls. Must be refactored for Batch API workflow:

- CLI commands: `prepare` (build + upload JSONL batch), `check` (poll status), `download` (fetch + parse + validate results)
- Or a single `submit` command that prepares and uploads, and a `collect` command that downloads and processes
- Model: `o3` only (no escalation model)
- Batch size: 5 records per request
- Loads prompts from file system
- Coordinates: batch_manager → llm_client → response_parser → response_validator
- Writes validated results to SQLite after downloading batch results

### 6. Test Run

- Submit a small test batch (1 request = 5 records) via Batch API
- Wait for completion (or poll)
- Download and validate results
- Confirm: 5 businesses scored, validated, persisted to SQLite
- Print sample scored record to console for visual inspection

## Output Artifacts

- `src/ai_scorer/llm_client.py`
- `src/ai_scorer/batch_manager.py`
- `src/ai_scorer/response_parser.py`
- `src/ai_scorer/response_validator.py`
- `src/ai_scorer/score_businesses.py`
- `src/ai_scorer/__init__.py`
- `requirements.txt` already updated (`openai>=1.0.0`, `python-dotenv>=1.0.0`)
- Test run output in `data/output/scoring_progress.db`

## Verify

- Test batch submitted, completed, downloaded, and validated without error
- 5 businesses scored with all 12 metrics
- All scores in 0-3 range
- Verbal rank labels present in all reasoning
- Confidence labels present
- Overall summaries present
- Results persisted to SQLite
- Token usage logged

## Pass Gate

Sub-part A passes when a test batch (5 businesses) is fully scored via Batch API, validated, and persisted. Only then proceed to Sub-part B (full batch execution).

## On Failure

- If API call fails: check API key, check billing credits, check model name
- If JSON parsing fails: inspect raw response, adjust prompt if needed
- If validation fails: inspect which fields are missing/malformed, adjust prompt or parser
- If rate limited: increase backoff intervals
