"""
AI Scorer — Synchronous API orchestrator.

Scores all 3,606 canonical business types using sequential o3 API calls.
Each call scores 5 businesses. Progress tracked in SQLite with full resume support.

Usage:
    python -m src.ai_scorer.score_businesses run [--reset]
    python -m src.ai_scorer.score_businesses status
"""

import argparse
import json
import logging
import time
from pathlib import Path

from src.ai_scorer.llm_client import call_sync
from src.ai_scorer.batch_manager import (
    init_db, reset_db, load_dataset, register_records,
    get_pending_record_ids, get_failed_record_ids,
    create_request_groups, register_requests,
    save_record_result, mark_record_failed, reset_failed_to_pending,
    get_progress, get_records_for_ids,
)
from src.ai_scorer.response_parser import parse_response
from src.ai_scorer.response_validator import validate_business

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ai_scorer")

PROMPTS_DIR = Path("src/ai_scorer/prompts")
BATCH_SIZE = 5
MAX_RETRIES = 2
THROTTLE_S = 1  # pause between successful calls


def load_prompts() -> tuple[str, str]:
    system = (PROMPTS_DIR / "scoring_system_prompt.txt").read_text(encoding="utf-8")
    user_tpl = (PROMPTS_DIR / "scoring_user_prompt_template.txt").read_text(encoding="utf-8")
    return system, user_tpl


def build_batch_input(records: list[dict]) -> list[dict]:
    return [
        {
            "record_id": r["record_id"],
            "business_type": r["business_type"],
            "definition": r.get("definition"),
            "source_family": r.get("source_family"),
        }
        for r in records
    ]


def score_one_request(record_ids: list[str], dataset: list[dict],
                      system_prompt: str, user_tpl: str) -> tuple[int, int, dict]:
    """Score one group of 5 records via sync API. Returns (scored, failed, tokens)."""
    records = get_records_for_ids(record_ids, dataset)
    batch_input = build_batch_input(records)
    user_prompt = user_tpl.replace("{batch_json}", json.dumps(batch_input, indent=2))

    try:
        raw, usage = call_sync(system_prompt, user_prompt)
    except Exception as e:
        logger.error("API call failed for %s: %s", record_ids[0], e)
        for rid in record_ids:
            mark_record_failed(rid)
        return 0, len(record_ids), {"input": 0, "output": 0, "reasoning": 0}

    parsed, parse_errors = parse_response(raw, record_ids)
    for err in parse_errors:
        logger.warning("Parse: %s", err)

    n = max(len(record_ids), 1)
    per_in = usage["prompt_tokens"] // n
    per_out = usage["completion_tokens"] // n
    per_reason = usage["reasoning_tokens"] // n

    scored = 0
    failed = 0
    for biz in parsed:
        rid = biz.get("record_id", "UNKNOWN")
        errors = validate_business(biz)
        if errors:
            for ve in errors:
                logger.warning("Validation: %s", ve)
            mark_record_failed(rid)
            failed += 1
        else:
            save_record_result(rid, json.dumps(biz), "o3", per_in, per_out, per_reason)
            scored += 1

    unmatched = set(record_ids) - {b.get("record_id") for b in parsed}
    for rid in unmatched:
        mark_record_failed(rid)
        failed += 1

    tokens = {
        "input": usage["prompt_tokens"],
        "output": usage["completion_tokens"],
        "reasoning": usage["reasoning_tokens"],
    }
    return scored, failed, tokens


def cmd_run(reset: bool = False):
    if reset:
        reset_db()
    init_db()
    dataset = load_dataset()
    register_records(dataset)

    system_prompt, user_tpl = load_prompts()
    start_time = time.time()
    total_scored = 0
    total_failed = 0
    total_tokens = {"input": 0, "output": 0, "reasoning": 0}

    # --- primary pass ---
    pending_ids = get_pending_record_ids()
    groups = [pending_ids[i:i + BATCH_SIZE] for i in range(0, len(pending_ids), BATCH_SIZE)]
    total_groups = len(groups)

    if total_groups == 0:
        progress = get_progress()
        print(f"No pending records. {progress['scored']} already scored.")
        return

    logger.info("Starting scoring: %d records in %d requests", len(pending_ids), total_groups)

    for i, group in enumerate(groups, 1):
        req_start = time.time()
        scored, failed, tokens = score_one_request(group, dataset, system_prompt, user_tpl)
        req_elapsed = time.time() - req_start

        total_scored += scored
        total_failed += failed
        for k in total_tokens:
            total_tokens[k] += tokens[k]

        if i % 10 == 0 or i == total_groups:
            progress = get_progress()
            elapsed_min = (time.time() - start_time) / 60
            rate = i / elapsed_min if elapsed_min > 0 else 0
            eta_min = (total_groups - i) / rate if rate > 0 else 0
            logger.info(
                "[%d/%d] %.0fs | %d scored, %d failed | overall %d/%d | %.1f req/min | ETA %.0f min",
                i, total_groups, req_elapsed, scored, failed,
                progress["scored"], progress["total_records"], rate, eta_min,
            )

        time.sleep(THROTTLE_S)

    # --- retry passes ---
    for retry_pass in range(1, MAX_RETRIES + 1):
        failed_ids = get_failed_record_ids()
        if not failed_ids:
            break
        logger.info("=== Retry pass %d: %d records ===", retry_pass, len(failed_ids))
        reset_failed_to_pending(failed_ids)

        retry_groups = [failed_ids[i:i + BATCH_SIZE] for i in range(0, len(failed_ids), BATCH_SIZE)]
        for i, group in enumerate(retry_groups, 1):
            scored, failed, tokens = score_one_request(group, dataset, system_prompt, user_tpl)
            total_scored += scored
            for k in total_tokens:
                total_tokens[k] += tokens[k]
            if i % 10 == 0 or i == len(retry_groups):
                progress = get_progress()
                logger.info("[retry %d/%d] %d/%d scored", i, len(retry_groups),
                            progress["scored"], progress["total_records"])
            time.sleep(THROTTLE_S)

    elapsed = time.time() - start_time
    progress = get_progress()

    print(f"\n{'='*60}")
    print("SCORING RUN COMPLETE")
    print(f"{'='*60}")
    print(f"Wall time:     {elapsed/60:.1f} minutes")
    print(f"Records:       {progress['scored']} scored / {progress['failed']} failed / "
          f"{progress['total_records']} total")
    print(f"Tokens:        in={total_tokens['input']:,}  out={total_tokens['output']:,}  "
          f"reasoning={total_tokens['reasoning']:,}")
    est = (total_tokens["input"] * 10.0 + total_tokens["output"] * 40.0) / 1_000_000
    print(f"Est. cost:     ${est:.2f}")
    print(f"{'='*60}")

    if progress["failed"] > 0:
        print(f"\n{progress['failed']} records failed after {MAX_RETRIES} retry passes.")
    else:
        print("\nAll records scored. Run post-processing:")
        print("  python -m src.ai_scorer.post_process")
        print("  python -m src.ai_scorer.verify_scoring")

    _print_sample()


def _print_sample():
    import sqlite3 as _sql
    conn = _sql.connect(str(Path("data/output/scoring_progress.db")))
    row = conn.execute(
        "SELECT record_id, scoring_result FROM records "
        "WHERE scoring_status='scored' ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()
    if not row:
        return
    result = json.loads(row[1])
    print(f"\nSAMPLE — {row[0]}: {result.get('business_type', '?')}")
    print(f"  {result.get('overall_fit_summary', 'N/A')[:200]}")
    metrics = result.get("metrics", {})
    for m, data in metrics.items():
        print(f"  {m}: {data.get('score', '?')} ({data.get('confidence', '?')})")


def cmd_status():
    init_db()
    progress = get_progress()
    print(f"\n{'='*50}")
    print("SCORING PROGRESS")
    print(f"{'='*50}")
    print(f"Records: {progress['scored']} scored / {progress['failed']} failed / "
          f"{progress['pending']} pending / {progress['total_records']} total")
    print(f"Tokens:  in={progress['tokens_input']:,}  out={progress['tokens_output']:,}  "
          f"reasoning={progress['tokens_reasoning']:,}")
    pct = progress['scored'] / max(progress['total_records'], 1) * 100
    print(f"Progress: {pct:.1f}%")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="AI Scorer — score businesses against founder thesis")
    sub = parser.add_subparsers(dest="command", help="command to run")

    sp_run = sub.add_parser("run", help="Score all records (resumes if interrupted)")
    sp_run.add_argument("--reset", action="store_true", help="Reset database and start fresh")

    sub.add_parser("status", help="Show progress summary")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(reset=args.reset)
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
