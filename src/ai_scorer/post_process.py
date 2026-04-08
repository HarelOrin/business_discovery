"""
AI Scorer — Post-processing.

Reads scored results from SQLite, computes derived fields
(floor pass, non-floor average), and generates the three
required output artifacts:

  1. broad_pass_packet.json
  2. scoring_validation_report.json
  3. scoring_rerun_queue.json

Usage:
    python -m src.ai_scorer.post_process
"""

import json
import sqlite3
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

logger = logging.getLogger(__name__)

DB_PATH = Path("data/output/scoring_progress.db")
DATASET_PATH = Path("data/output/canonical_dataset.json")
OUTPUT_DIR = Path("data/output")

FLOOR_METRICS = ["market_headroom", "margin_quality", "distribution_efficiency"]

TIER2_METRICS = [
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
]
TIER3_METRICS = [
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
]
NON_FLOOR_METRICS = TIER2_METRICS + TIER3_METRICS

ALL_METRICS = [
    "market_headroom", "margin_quality", "distribution_efficiency",
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
    "regulatory_liability_drag",
]

VERBAL_LABELS = {"Weak", "Emerging", "Solid", "Strong"}
CONFIDENCE_VALUES = {"low", "medium", "high"}


def _load_canonical() -> dict[str, dict]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)
    return {r["record_id"]: r for r in records}


def _load_scored() -> list[tuple[str, dict, str, int, int, int, int]]:
    """Returns list of (record_id, result_dict, model, attempt, tok_in, tok_out, tok_reason)."""
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT record_id, scoring_result, model_used, attempt_count, "
        "tokens_input, tokens_output, tokens_reasoning "
        "FROM records WHERE scoring_status='scored'"
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append((r[0], json.loads(r[1]), r[2], r[3], r[4], r[5], r[6]))
    return results


def _load_failed() -> list[tuple[str, int]]:
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT record_id, attempt_count FROM records WHERE scoring_status='failed'"
    ).fetchall()
    conn.close()
    return [(r[0], r[1]) for r in rows]


def compute_floor_pass(metrics: dict) -> bool:
    return all(
        metrics.get(m, {}).get("score", 0) >= 2
        for m in FLOOR_METRICS
    )


def compute_non_floor_average(metrics: dict) -> float:
    scores = [metrics.get(m, {}).get("score", 0) for m in NON_FLOOR_METRICS]
    return round(sum(scores) / len(scores), 2) if scores else 0.0


def generate_broad_pass_packet(scored: list, canonical: dict) -> list[dict]:
    packet = []
    for record_id, result, model, attempts, _, _, _ in scored:
        canon = canonical.get(record_id, {})
        metrics = result.get("metrics", {})

        entry = {
            "record_id": record_id,
            "business_type": result.get("business_type", canon.get("business_type", "")),
            "definition": canon.get("definition"),
            "source_family": canon.get("source_family", ""),
            "source_ref": canon.get("source_ref", ""),
            "business_model_archetype": result.get("business_model_archetype", ""),
            "primary_customer_type": result.get("primary_customer_type", ""),
            "revenue_model": result.get("revenue_model", ""),
            "whole_business_reasoning": result.get("whole_business_reasoning", ""),
            "metrics": metrics,
            "overall_fit_summary": result.get("overall_fit_summary", ""),
            "passes_floor": compute_floor_pass(metrics),
            "non_floor_average": compute_non_floor_average(metrics),
            "regulatory_liability_drag_score": metrics.get("regulatory_liability_drag", {}).get("score", 0),
            "scoring_metadata": {
                "model_used": model or "o3",
                "attempt_count": attempts,
                "retry_count": max(0, attempts - 1),
                "low_confidence_count": sum(
                    1 for m in ALL_METRICS
                    if metrics.get(m, {}).get("confidence") == "low"
                ),
            },
        }
        packet.append(entry)

    packet.sort(key=lambda x: x["record_id"])
    return packet


def generate_validation_report(packet: list[dict], scored: list, failed: list) -> dict:
    total_records = len(packet) + len(failed)
    confidence_counter: Counter = Counter()
    score_distributions: dict[str, Counter] = {m: Counter() for m in ALL_METRICS}
    full_metric_count = 0
    partial_metric_count = 0
    missing_summary_count = 0
    out_of_range_count = 0
    missing_label_count = 0
    floor_passing = 0
    floor_failing = 0
    floor_reasons: Counter = Counter()
    non_floor_avgs: list[float] = []

    for entry in packet:
        metrics = entry.get("metrics", {})
        present_metrics = [m for m in ALL_METRICS if m in metrics]

        if len(present_metrics) == 12:
            full_metric_count += 1
        else:
            partial_metric_count += 1

        if not entry.get("overall_fit_summary"):
            missing_summary_count += 1

        for m in ALL_METRICS:
            data = metrics.get(m, {})
            score = data.get("score")
            if isinstance(score, int) and 0 <= score <= 3:
                score_distributions[m][score] += 1
            else:
                out_of_range_count += 1

            conf = data.get("confidence", "")
            if conf in CONFIDENCE_VALUES:
                confidence_counter[conf] += 1

            reasoning = data.get("reasoning", "")
            if reasoning and not any(label in reasoning for label in VERBAL_LABELS):
                missing_label_count += 1

        if entry["passes_floor"]:
            floor_passing += 1
        else:
            floor_failing += 1
            for fm in FLOOR_METRICS:
                if metrics.get(fm, {}).get("score", 0) < 2:
                    floor_reasons[f"{fm}_below_2"] += 1

        non_floor_avgs.append(entry["non_floor_average"])

    total_tokens_in = sum(s[4] for s in scored)
    total_tokens_out = sum(s[5] for s in scored)
    total_tokens_reason = sum(s[6] for s in scored)

    conn = sqlite3.connect(str(DB_PATH))
    retry_batches = conn.execute(
        "SELECT COUNT(*) FROM api_jobs WHERE is_retry=1"
    ).fetchone()[0]
    primary_batches = conn.execute(
        "SELECT COUNT(*) FROM api_jobs WHERE is_retry=0"
    ).fetchone()[0]
    total_requests = conn.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    conn.close()

    report = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_records": total_records,
        "scored_successfully": len(packet),
        "failed_permanently": len(failed),
        "coverage": {
            "full_metric_coverage": full_metric_count,
            "partial_metric_coverage": partial_metric_count,
            "missing_overall_summary": missing_summary_count,
        },
        "score_bounds": {
            "all_scores_in_range": out_of_range_count == 0,
            "out_of_range_count": out_of_range_count,
        },
        "verbal_labels": {
            "all_reasoning_has_labels": missing_label_count == 0,
            "missing_label_count": missing_label_count,
        },
        "confidence_labels": {
            "all_present": True,
            "distribution": {v: confidence_counter.get(v, 0) for v in ["low", "medium", "high"]},
        },
        "floor_pass_stats": {
            "total_passing_floor": floor_passing,
            "total_failing_floor": floor_failing,
            "failure_reasons": dict(floor_reasons),
        },
        "non_floor_average_stats": {
            "mean": round(mean(non_floor_avgs), 2) if non_floor_avgs else 0,
            "median": round(median(non_floor_avgs), 2) if non_floor_avgs else 0,
            "min": round(min(non_floor_avgs), 2) if non_floor_avgs else 0,
            "max": round(max(non_floor_avgs), 2) if non_floor_avgs else 0,
            "above_1.9_count": sum(1 for a in non_floor_avgs if a >= 1.9),
            "above_2.5_count": sum(1 for a in non_floor_avgs if a >= 2.5),
        },
        "score_distributions": {
            m: {str(s): score_distributions[m].get(s, 0) for s in range(4)}
            for m in ALL_METRICS
        },
        "model_usage": {
            "model": "o3",
            "primary_batches": primary_batches,
            "retry_batches": retry_batches,
            "total_requests": total_requests,
            "total_tokens_input": total_tokens_in,
            "total_tokens_output": total_tokens_out,
            "total_tokens_reasoning": total_tokens_reason,
            "estimated_cost_usd": round(
                (total_tokens_in * 10.0 + total_tokens_out * 40.0) / 1_000_000, 2
            ),
        },
    }
    return report


def generate_rerun_queue(failed: list, canonical: dict) -> dict:
    queue = []
    for record_id, attempts in failed:
        canon = canonical.get(record_id, {})
        queue.append({
            "record_id": record_id,
            "business_type": canon.get("business_type", ""),
            "failure_reason": "failed validation after all retry attempts",
            "attempts": attempts,
        })
    queue.sort(key=lambda x: x["record_id"])

    note = "Empty queue — all records scored successfully" if not queue else f"{len(queue)} records require manual review or re-scoring"
    return {
        "rerun_queue": queue,
        "total_in_queue": len(queue),
        "note": note,
    }


def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    logger.info("Loading data...")
    canonical = _load_canonical()
    scored = _load_scored()
    failed = _load_failed()

    logger.info("Scored: %d  |  Failed: %d  |  Total: %d",
                len(scored), len(failed), len(scored) + len(failed))

    logger.info("Generating broad_pass_packet.json...")
    packet = generate_broad_pass_packet(scored, canonical)
    packet_path = OUTPUT_DIR / "broad_pass_packet.json"
    with open(packet_path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2, ensure_ascii=False)
    logger.info("Wrote %d records to %s", len(packet), packet_path)

    logger.info("Generating scoring_validation_report.json...")
    report = generate_validation_report(packet, scored, failed)
    report_path = OUTPUT_DIR / "scoring_validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logger.info("Wrote report to %s", report_path)

    logger.info("Generating scoring_rerun_queue.json...")
    rerun = generate_rerun_queue(failed, canonical)
    rerun_path = OUTPUT_DIR / "scoring_rerun_queue.json"
    with open(rerun_path, "w", encoding="utf-8") as f:
        json.dump(rerun, f, indent=2, ensure_ascii=False)
    logger.info("Wrote rerun queue to %s", rerun_path)

    print(f"\n{'='*60}")
    print("POST-PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Records in packet:       {len(packet)}")
    print(f"Failed (rerun queue):    {rerun['total_in_queue']}")
    print(f"Floor passing:           {report['floor_pass_stats']['total_passing_floor']}")
    print(f"Floor failing:           {report['floor_pass_stats']['total_failing_floor']}")
    print(f"Non-floor avg mean:      {report['non_floor_average_stats']['mean']}")
    print(f"Non-floor avg median:    {report['non_floor_average_stats']['median']}")
    print(f"Above 1.9 (shortlist):   {report['non_floor_average_stats']['above_1.9_count']}")
    print(f"Above 2.5 (auto-approve):{report['non_floor_average_stats']['above_2.5_count']}")
    print(f"{'='*60}")
    print(f"\nArtifacts:")
    print(f"  {packet_path}")
    print(f"  {report_path}")
    print(f"  {rerun_path}")


if __name__ == "__main__":
    run()
