# Handoff — AI Scorer Sub-part A: Scoring Infrastructure

## Scope

Build the core scoring infrastructure: LLM client, batch manager, response parser, and validator. Produce a working test run of 1 batch (20 businesses) to confirm the pipeline works end-to-end before the full run.

## Inputs

- `data/output/canonical_dataset.json` — 3,606 canonical business type records
- `src/ai_scorer/prompts/scoring_system_prompt.txt` — locked system prompt
- `src/ai_scorer/prompts/scoring_user_prompt_template.txt` — locked user prompt template
- `impl-notes/execution-master-context.md` — locked metrics, scoring rules, founder thesis

## Pre-requisites

- OpenAI API key set as environment variable `OPENAI_API_KEY`
- `openai` Python package installed (add to `requirements.txt`)

## Required Work

### 1. LLM Client (`src/ai_scorer/llm_client.py`)

- OpenAI API wrapper using `gpt-4o` as primary model
- JSON mode enabled (`response_format={"type": "json_object"}`)
- Retry logic: exponential backoff, max 3 retries per API call
- Rate limit handling (respect 429 responses)
- Timeout handling (120s per call)
- Escalation model support: accept model name as parameter for rerun/escalation calls
- Log token usage per call for cost tracking

### 2. Batch Manager (`src/ai_scorer/batch_manager.py`)

- Load canonical dataset from JSON
- Split into batches of 20 records each
- SQLite tracking table (`data/output/scoring_progress.db`):
  - `batch_id`, `record_ids` (JSON array), `status` (pending/in_progress/completed/failed), `attempt_count`, `created_at`, `completed_at`
- Resume support: on restart, skip completed batches and retry failed/pending ones
- Per-record tracking table:
  - `record_id`, `batch_id`, `scoring_status` (pending/scored/failed/escalated), `attempt_count`

### 3. Response Parser (`src/ai_scorer/response_parser.py`)

- Parse JSON response from LLM
- Extract each scored business from the `scored_businesses` array
- Map back to original `record_id` to confirm all batch items are present
- Handle malformed JSON gracefully (log error, mark batch as failed)

### 4. Response Validator (`src/ai_scorer/response_validator.py`)

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

### 5. Main Orchestrator Entry Point (`src/ai_scorer/score_businesses.py`)

- CLI entry point
- Argument: `--test` flag to run only 1 batch (first 20 records) for validation
- Argument: `--batch-size` (default 20)
- Argument: `--model` (default "gpt-4o")
- Loads prompts from file system
- Coordinates: batch_manager → llm_client → response_parser → response_validator
- Writes validated results to SQLite as they complete (not just at the end)
- Progress logging: "Batch 3/181 complete — 60 records scored — 0 failures"

### 6. Test Run

- Execute `python src/ai_scorer/score_businesses.py --test`
- Confirm: API call succeeds, JSON parses, all 20 businesses validated, results written to SQLite
- Print sample scored record to console for visual inspection

## Output Artifacts

- `src/ai_scorer/llm_client.py`
- `src/ai_scorer/batch_manager.py`
- `src/ai_scorer/response_parser.py`
- `src/ai_scorer/response_validator.py`
- `src/ai_scorer/score_businesses.py`
- `src/ai_scorer/__init__.py`
- Updated `requirements.txt` (add `openai>=1.0.0`)
- Test run output in `data/output/scoring_progress.db`

## Verify

- `--test` run completes without error
- 20 businesses scored with all 12 metrics
- All scores in 0-3 range
- Verbal rank labels present in all reasoning
- Confidence labels present
- Overall summaries present
- Results persisted to SQLite
- Token usage logged

## Pass Gate

Sub-part A passes when the test batch (20 businesses) is fully scored, validated, and persisted. Only then proceed to Sub-part B (full batch execution).

## On Failure

- If API call fails: check API key, check billing credits, check model name
- If JSON parsing fails: inspect raw response, adjust prompt if needed
- If validation fails: inspect which fields are missing/malformed, adjust prompt or parser
- If rate limited: increase backoff intervals
