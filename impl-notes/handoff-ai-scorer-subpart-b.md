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

### 1. Full Primary Run

- Execute: `python src/ai_scorer/score_businesses.py`
- Processes all ~181 batches (3,606 records / 20 per batch)
- Progress logging every batch: batch number, cumulative scored count, failure count, elapsed time
- Periodic summary every 20 batches: success rate, average scores, cost estimate so far
- Resume-safe: if interrupted, restart picks up from last incomplete batch

### 2. Retry Pass

- After primary run completes, identify all failed/invalid records from SQLite
- Re-batch failed records (batch size 10 for retry — smaller batches for problem cases)
- Retry with primary model (gpt-4o), up to 2 additional attempts per record
- Log retry results

### 3. Escalation Pass

- After retry pass, any records still failed or with majority low-confidence metrics
- Re-batch these for escalation model (e.g., `gpt-4o` with temperature=0 for more deterministic output, or a stronger model if available)
- Mark escalated records in SQLite
- Maximum 1 escalation attempt per record

### 4. Progress Monitoring

- Track and log:
  - Total records: 3,606
  - Scored successfully: N
  - Failed after all retries: N
  - Escalated: N
  - Low-confidence (3+ metrics with "low" confidence): N
  - Average token usage per batch
  - Estimated total cost so far

## Execution Estimates

- ~181 batches for primary run
- At ~15-30 seconds per batch (API latency + rate limiting): ~45-90 minutes
- Retry + escalation: additional 5-15 minutes depending on failure count
- Total cost estimate: $5-15

## Output Artifacts

- `data/output/scoring_progress.db` — fully populated with all scoring results
- Console log with run summary

## Verify

- SQLite contains scored results for all 3,606 records (or documented failures)
- No batch left in "in_progress" state
- Retry queue processed
- Escalation queue processed (if any)
- Run summary printed: total scored, total failed, total escalated

## Pass Gate

Sub-part B passes when all batches are processed (primary + retry + escalation) and the scoring_progress.db contains results for 3,606 records (minus any documented permanent failures). Proceed to Sub-part C only after this.

## On Failure

- If many batches fail: inspect error patterns — likely a prompt issue or rate limiting
- If rate limited heavily: add longer delays between batches (e.g., 2-5 second sleep)
- If cost exceeds budget: pause, report to founder, get approval before continuing
- If API outage: resume later — SQLite tracking enables safe restart
