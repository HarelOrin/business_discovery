"""
Benchmark script — tests different models and batch sizes against real records.
Measures: quality, token usage, latency, and projects full-run cost.

Usage: python -m src.ai_scorer.benchmark
"""

import json
import os
import time
import logging
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("benchmark")

PROMPTS_DIR = Path("src/ai_scorer/prompts")
DATASET_PATH = Path("data/output/canonical_dataset.json")
TOTAL_RECORDS = 3606

MODELS = ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]
BATCH_SIZES = [5, 10, 20]

PRICING = {
    "gpt-4.1":      {"input": 2.00, "output": 8.00,  "batch_input": 1.00, "batch_output": 4.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60,  "batch_input": 0.20, "batch_output": 0.80},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40,  "batch_input": 0.05, "batch_output": 0.20},
    "gpt-4o":       {"input": 2.50, "output": 10.00, "batch_input": 1.25, "batch_output": 5.00},
    "gpt-4o-mini":  {"input": 0.15, "output": 0.60,  "batch_input": 0.075,"batch_output": 0.30},
}

VERBAL_LABELS = {"Weak", "Emerging", "Solid", "Strong"}
REQUIRED_METRICS = [
    "market_headroom", "margin_quality", "distribution_efficiency",
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
    "regulatory_liability_drag",
]


def load_prompts():
    system = (PROMPTS_DIR / "scoring_system_prompt.txt").read_text(encoding="utf-8")
    user_template = (PROMPTS_DIR / "scoring_user_prompt_template.txt").read_text(encoding="utf-8")
    return system, user_template


def load_sample_records(n: int) -> list[dict]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[:n]


def build_batch_input(records):
    return [{"record_id": r["record_id"], "business_type": r["business_type"],
             "definition": r.get("definition"), "source_family": r.get("source_family")}
            for r in records]


def quality_check(scored_businesses: list[dict], expected_ids: list[str]) -> dict:
    """Quick quality assessment of scored output."""
    result = {"total": len(expected_ids), "returned": len(scored_businesses),
              "valid": 0, "issues": []}

    returned_ids = {b.get("record_id") for b in scored_businesses}
    missing = set(expected_ids) - returned_ids
    if missing:
        result["issues"].append(f"Missing {len(missing)} records: {sorted(missing)}")

    for biz in scored_businesses:
        rid = biz.get("record_id", "?")
        errors = []
        metrics = biz.get("metrics", {})

        missing_metrics = [m for m in REQUIRED_METRICS if m not in metrics]
        if missing_metrics:
            errors.append(f"missing metrics: {missing_metrics}")

        for m in REQUIRED_METRICS:
            entry = metrics.get(m, {})
            score = entry.get("score")
            if not isinstance(score, int) or score < 0 or score > 3:
                errors.append(f"{m}.score={score}")
            reasoning = entry.get("reasoning", "")
            if not any(lbl in reasoning for lbl in VERBAL_LABELS):
                errors.append(f"{m} missing verbal label")
            if entry.get("confidence") not in ("low", "medium", "high"):
                errors.append(f"{m}.confidence={entry.get('confidence')}")

        if not biz.get("whole_business_reasoning"):
            errors.append("no whole_business_reasoning")
        if not biz.get("overall_fit_summary"):
            errors.append("no overall_fit_summary")

        if errors:
            result["issues"].append(f"[{rid}] {'; '.join(errors)}")
        else:
            result["valid"] += 1

    return result


def run_single_test(model: str, batch_size: int, records: list[dict],
                    system_prompt: str, user_template: str) -> dict:
    """Run one scoring call and measure everything."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=300, max_retries=0)
    batch_input = build_batch_input(records[:batch_size])
    expected_ids = [r["record_id"] for r in records[:batch_size]]
    user_prompt = user_template.replace("{batch_json}", json.dumps(batch_input, indent=2))

    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
    except Exception as e:
        return {"model": model, "batch_size": batch_size, "error": str(e),
                "latency_s": time.time() - start}

    latency = time.time() - start
    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0

    try:
        raw = json.loads(response.choices[0].message.content)
        scored = raw.get("scored_businesses", [])
        quality = quality_check(scored, expected_ids)
    except (json.JSONDecodeError, Exception) as e:
        quality = {"total": batch_size, "returned": 0, "valid": 0,
                   "issues": [f"JSON parse error: {e}"]}
        scored = []

    prices = PRICING.get(model, PRICING["gpt-4o"])
    call_cost = (input_tokens * prices["input"] / 1_000_000) + (output_tokens * prices["output"] / 1_000_000)

    total_batches = (TOTAL_RECORDS + batch_size - 1) // batch_size
    proj_input = input_tokens * total_batches
    proj_output = output_tokens * total_batches
    proj_cost_std = (proj_input * prices["input"] / 1_000_000) + (proj_output * prices["output"] / 1_000_000)
    proj_cost_batch = (proj_input * prices["batch_input"] / 1_000_000) + (proj_output * prices["batch_output"] / 1_000_000)
    proj_time_min = (latency * total_batches) / 60

    return {
        "model": model,
        "batch_size": batch_size,
        "latency_s": round(latency, 1),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_per_record": round(output_tokens / batch_size) if batch_size else 0,
        "call_cost_usd": round(call_cost, 4),
        "quality_valid": quality["valid"],
        "quality_total": quality["total"],
        "quality_issues": quality["issues"],
        "proj_total_batches": total_batches,
        "proj_input_tokens": proj_input,
        "proj_output_tokens": proj_output,
        "proj_cost_standard_usd": round(proj_cost_std, 2),
        "proj_cost_batch_api_usd": round(proj_cost_batch, 2),
        "proj_runtime_min": round(proj_time_min, 1),
    }


def main():
    system_prompt, user_template = load_prompts()
    max_batch = max(BATCH_SIZES)
    records = load_sample_records(max_batch)
    logger.info("Loaded %d sample records for benchmarking.", len(records))

    results = []

    for model in MODELS:
        for bs in BATCH_SIZES:
            logger.info("Testing: model=%s  batch_size=%d ...", model, bs)
            r = run_single_test(model, bs, records, system_prompt, user_template)
            results.append(r)

            if "error" in r:
                logger.error("  FAILED: %s", r["error"])
            else:
                logger.info("  OK: %.1fs | %d/%d valid | $%.4f this call | "
                            "Projected: $%.2f standard / $%.2f batch API / %.0f min",
                            r["latency_s"], r["quality_valid"], r["quality_total"],
                            r["call_cost_usd"], r["proj_cost_standard_usd"],
                            r["proj_cost_batch_api_usd"], r["proj_runtime_min"])

            time.sleep(2)

    print("\n" + "=" * 100)
    print("BENCHMARK RESULTS")
    print("=" * 100)
    print(f"{'Model':<18} {'Batch':>5} {'Time':>6} {'In Tok':>8} {'Out Tok':>9} {'Tok/Rec':>8} "
          f"{'Valid':>6} {'$Call':>7} {'$Std':>7} {'$Batch':>7} {'~Min':>6}")
    print("-" * 100)
    for r in results:
        if "error" in r:
            print(f"{r['model']:<18} {r['batch_size']:>5} {'ERROR':>6}  {r['error'][:60]}")
        else:
            print(f"{r['model']:<18} {r['batch_size']:>5} {r['latency_s']:>5.1f}s "
                  f"{r['input_tokens']:>8,} {r['output_tokens']:>9,} {r['tokens_per_record']:>8,} "
                  f"{r['quality_valid']}/{r['quality_total']:>3} "
                  f"${r['call_cost_usd']:>6.4f} ${r['proj_cost_standard_usd']:>6.2f} "
                  f"${r['proj_cost_batch_api_usd']:>6.2f} {r['proj_runtime_min']:>5.1f}")
    print("=" * 100)

    out_path = Path("data/output/benchmark_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info("Full results saved to %s", out_path)

    if any(r.get("quality_issues") for r in results):
        print("\nQUALITY ISSUES:")
        for r in results:
            if r.get("quality_issues"):
                print(f"\n  {r['model']} (batch={r['batch_size']}):")
                for issue in r["quality_issues"][:5]:
                    print(f"    - {issue}")


if __name__ == "__main__":
    main()
