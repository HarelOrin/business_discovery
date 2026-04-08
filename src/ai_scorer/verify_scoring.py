"""
AI Scorer — Standalone verification script.

Reads broad_pass_packet.json and confirms all acceptance criteria:
  - Record count matches canonical dataset
  - All 12 metrics present for every record
  - All scores in 0-3 range (integers)
  - All reasoning strings contain verbal rank labels
  - All confidence values are valid
  - All passes_floor flags match recomputed values
  - All non_floor_average values match recomputed values
  - overall_fit_summary present for every record

Usage:
    python -m src.ai_scorer.verify_scoring
"""

import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("verify_scoring")

PACKET_PATH = Path("data/output/broad_pass_packet.json")
DATASET_PATH = Path("data/output/canonical_dataset.json")

ALL_METRICS = [
    "market_headroom", "margin_quality", "distribution_efficiency",
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
    "regulatory_liability_drag",
]

FLOOR_METRICS = ["market_headroom", "margin_quality", "distribution_efficiency"]

NON_FLOOR_METRICS = [
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
]

VERBAL_LABELS = {"Weak", "Emerging", "Solid", "Strong"}
CONFIDENCE_VALUES = {"low", "medium", "high"}


def verify():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        canonical = json.load(f)
    canonical_ids = {r["record_id"] for r in canonical}

    with open(PACKET_PATH, "r", encoding="utf-8") as f:
        packet = json.load(f)
    packet_ids = {r["record_id"] for r in packet}

    errors = []
    warnings = []

    # --- Record count ---
    if len(packet) != len(canonical):
        if len(packet) < len(canonical):
            missing = canonical_ids - packet_ids
            errors.append(
                f"Record count mismatch: packet has {len(packet)}, "
                f"canonical has {len(canonical)}, missing {len(missing)}"
            )
        else:
            errors.append(f"Packet has MORE records ({len(packet)}) than canonical ({len(canonical)})")

    extra = packet_ids - canonical_ids
    if extra:
        errors.append(f"Packet contains {len(extra)} record_ids not in canonical dataset")

    # --- Per-record checks ---
    floor_mismatches = 0
    avg_mismatches = 0

    for entry in packet:
        rid = entry.get("record_id", "UNKNOWN")
        metrics = entry.get("metrics", {})

        # All 12 metrics present
        for m in ALL_METRICS:
            if m not in metrics:
                errors.append(f"[{rid}] Missing metric: {m}")
                continue

            data = metrics[m]
            score = data.get("score")

            # Score in 0-3
            if not isinstance(score, int) or score < 0 or score > 3:
                errors.append(f"[{rid}] {m}.score invalid: {score}")

            # Verbal rank label in reasoning
            reasoning = data.get("reasoning", "")
            if not reasoning:
                errors.append(f"[{rid}] {m}.reasoning is empty")
            elif not any(label in reasoning for label in VERBAL_LABELS):
                errors.append(f"[{rid}] {m}.reasoning missing verbal rank label")

            # Confidence
            conf = data.get("confidence", "")
            if conf not in CONFIDENCE_VALUES:
                errors.append(f"[{rid}] {m}.confidence invalid: '{conf}'")

        # Overall summary
        if not entry.get("overall_fit_summary"):
            errors.append(f"[{rid}] overall_fit_summary missing")

        # Recompute floor pass
        expected_floor = all(
            metrics.get(m, {}).get("score", 0) >= 2 for m in FLOOR_METRICS
        )
        if entry.get("passes_floor") != expected_floor:
            floor_mismatches += 1
            errors.append(
                f"[{rid}] passes_floor mismatch: stored={entry.get('passes_floor')}, "
                f"computed={expected_floor}"
            )

        # Recompute non-floor average
        nf_scores = [metrics.get(m, {}).get("score", 0) for m in NON_FLOOR_METRICS]
        expected_avg = round(sum(nf_scores) / len(nf_scores), 2) if nf_scores else 0.0
        if abs(entry.get("non_floor_average", 0) - expected_avg) > 0.005:
            avg_mismatches += 1
            errors.append(
                f"[{rid}] non_floor_average mismatch: stored={entry.get('non_floor_average')}, "
                f"computed={expected_avg}"
            )

    # --- Summary ---
    print(f"\n{'='*60}")
    print("SCORING VERIFICATION RESULTS")
    print(f"{'='*60}")
    print(f"Canonical records:     {len(canonical)}")
    print(f"Packet records:        {len(packet)}")
    print(f"Floor flag mismatches: {floor_mismatches}")
    print(f"Average mismatches:    {avg_mismatches}")
    print(f"Total errors:          {len(errors)}")
    print(f"Total warnings:        {len(warnings)}")

    if errors:
        print(f"\n--- ERRORS ({len(errors)}) ---")
        for e in errors[:50]:
            print(f"  {e}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")
        print(f"\nVERIFICATION: FAIL")
        return False
    else:
        print(f"\nVERIFICATION: PASS")
        print("All acceptance criteria met.")
        return True


if __name__ == "__main__":
    passed = verify()
    exit(0 if passed else 1)
