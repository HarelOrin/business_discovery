# Handoff — AI Scorer Sub-part B: Batch Execution

## Scope

Execute the full scoring run across all 3,606 canonical business types using the infrastructure built in Sub-part A. Handle retries, escalation, and progress tracking.

## Pre-requisites

- Sub-part A passed: test batch of 20 businesses scored and validated successfully
- OpenAI API key active with sufficient credits (~$10-20 loaded)
- All Sub-part A code modules working

## Inputs

- `data/output/canonical_dataset.json` — 3,606 records
- `data/output/scoring_progress.db` — SQLite tracking from Sub-part A test run
- All `src/ai_scorer/` modules from Sub-part A

## Required Work

### 1. Full Primary Run (Batch API)

- Prepare JSONL batch file with all 722 requests (3,606 records / 5 per batch)
- Each line: `{"custom_id": "batch_001", "method": "POST", "url": "/v1/chat/completions", "body": {...}}`
- Primary model: `o3` (reasoning model — use `role: "developer"` instead of `role: "system"`)
- Upload batch file and submit batch job via `client.batches.create()`
- Poll for completion via `client.batches.retrieve()` (or check back manually)
- Download results file when status is "completed"
- Parse results, validate each response, persist to SQLite

### 2. Retry Pass

- After primary batch completes, identify all failed/invalid records
- Re-batch failed records (batch size 5 for retry — same structure)
- Submit as a new Batch API job with `o3`
- Up to 2 retry passes total

### 3. Results Collection

- Track and log (from batch results):
  - Total records: 3,606
  - Scored successfully: N
  - Failed after all retries: N
  - Low-confidence (3+ metrics with "low" confidence): N
  - Total token usage (input, output, reasoning/thinking)
  - Actual cost from token counts

## Execution Estimates

- ~722 batches for primary run (5 records per batch)
- Batch API processes asynchronously — results within 24 hours
- No machine uptime required during processing
- Retry passes: additional Batch API jobs if needed (hours, not minutes)
- Total cost estimate: ~$18 (Batch API pricing for o3)

## Output Artifacts

- `data/output/scoring_progress.db` — fully populated with all scoring results
- Console log with run summary

## Verify

- SQLite contains scored results for all 3,606 records (or documented failures)
- No batch left in "in_progress" state
- Retry queue processed
- Run summary printed: total scored, total failed

## Pass Gate

Sub-part B passes when all batches are processed (primary + retry) and the scoring_progress.db contains results for 3,606 records (minus any documented permanent failures). Proceed to Sub-part C only after this.

## On Failure

- If batch job fails entirely: check batch status error message, re-upload and resubmit
- If many individual requests fail within batch: inspect error patterns in result file — likely a prompt issue
- If cost exceeds budget: pause, report to founder, get approval before continuing
- Batch API handles rate limiting automatically — no manual throttling needed
