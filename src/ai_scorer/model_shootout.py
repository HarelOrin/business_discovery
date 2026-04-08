"""
Head-to-head model comparison on 5 diverse business types.
Tests: gpt-4.1, o3, o4-mini, gpt-4o — all at batch_size=5.
Captures: quality, calibration, reasoning depth, token usage (including thinking tokens), cost.
"""

import json
import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PROMPTS_DIR = Path("src/ai_scorer/prompts")
DATASET_PATH = Path("data/output/canonical_dataset.json")

MODELS = [
    {"name": "o3",           "is_reasoning": True,  "input_price": 2.00, "output_price": 8.00,   "batch_in": 1.00, "batch_out": 4.00},
    {"name": "o3-pro",       "is_reasoning": True,  "input_price": 20.00,"output_price": 80.00,  "batch_in": 10.00,"batch_out": 40.00},
    {"name": "o1",           "is_reasoning": True,  "input_price": 15.00,"output_price": 60.00,  "batch_in": 7.50, "batch_out": 30.00},
    {"name": "gpt-4.1",     "is_reasoning": False, "input_price": 2.00, "output_price": 8.00,   "batch_in": 1.00, "batch_out": 4.00},
]

VERBAL_LABELS = {"Weak", "Emerging", "Solid", "Strong"}
REQUIRED_METRICS = [
    "market_headroom", "margin_quality", "distribution_efficiency",
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
    "regulatory_liability_drag",
]

# Pick 5 diverse business types from dataset for a fair test
SAMPLE_INDICES = [0, 50, 200, 500, 1000]


def load_test_records():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = [data[i] for i in SAMPLE_INDICES if i < len(data)]
    print(f"Test businesses: {[r['business_type'] for r in records]}")
    return records


def load_prompts():
    system = (PROMPTS_DIR / "scoring_system_prompt.txt").read_text(encoding="utf-8")
    user_template = (PROMPTS_DIR / "scoring_user_prompt_template.txt").read_text(encoding="utf-8")
    return system, user_template


def build_batch_input(records):
    return [{"record_id": r["record_id"], "business_type": r["business_type"],
             "definition": r.get("definition"), "source_family": r.get("source_family")}
            for r in records]


def run_model_test(model_info, records, system_prompt, user_template):
    model = model_info["name"]
    is_reasoning = model_info["is_reasoning"]

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=300, max_retries=1)
    batch_input = build_batch_input(records)
    user_prompt = user_template.replace("{batch_json}", json.dumps(batch_input, indent=2))

    messages = [
        {"role": "system" if not is_reasoning else "developer", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }
    if not is_reasoning:
        kwargs["temperature"] = 0.3

    start = time.time()
    try:
        response = client.chat.completions.create(**kwargs)
    except Exception as e:
        return {"model": model, "error": str(e), "latency_s": round(time.time() - start, 1)}

    latency = time.time() - start
    usage = response.usage

    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0
    reasoning_tokens = 0
    if usage and hasattr(usage, "completion_tokens_details") and usage.completion_tokens_details:
        reasoning_tokens = getattr(usage.completion_tokens_details, "reasoning_tokens", 0) or 0

    visible_output_tokens = output_tokens - reasoning_tokens

    try:
        raw = json.loads(response.choices[0].message.content)
        scored = raw.get("scored_businesses", [])
    except Exception as e:
        return {"model": model, "error": f"JSON parse: {e}", "latency_s": round(latency, 1)}

    # Quality analysis per business
    results_per_biz = []
    valid_count = 0
    for biz in scored:
        rid = biz.get("record_id", "?")
        bt = biz.get("business_type", "?")
        errors = []
        metrics = biz.get("metrics", {})

        missing_metrics = [m for m in REQUIRED_METRICS if m not in metrics]
        if missing_metrics:
            errors.append(f"missing: {missing_metrics}")

        scores = {}
        for m in REQUIRED_METRICS:
            entry = metrics.get(m, {})
            s = entry.get("score")
            scores[m] = s
            if not isinstance(s, int) or s < 0 or s > 3:
                errors.append(f"{m}.score={s}")
            reasoning = entry.get("reasoning", "")
            if not any(lbl in reasoning for lbl in VERBAL_LABELS):
                errors.append(f"{m} no verbal label")
            if entry.get("confidence") not in ("low", "medium", "high"):
                errors.append(f"{m}.confidence={entry.get('confidence')}")

        if not biz.get("whole_business_reasoning"):
            errors.append("no whole_business_reasoning")
        if not biz.get("overall_fit_summary"):
            errors.append("no overall_fit_summary")

        is_valid = len(errors) == 0
        if is_valid:
            valid_count += 1

        results_per_biz.append({
            "record_id": rid,
            "business_type": bt,
            "valid": is_valid,
            "errors": errors,
            "scores": scores,
            "whole_reasoning_len": len(biz.get("whole_business_reasoning", "")),
            "summary": biz.get("overall_fit_summary", "")[:200],
        })

    # Cost projection for full 3606 records at batch_size=5
    total_batches = 722
    proj_in = input_tokens * total_batches
    proj_out = output_tokens * total_batches
    proj_std = (proj_in * model_info["input_price"] / 1e6) + (proj_out * model_info["output_price"] / 1e6)
    proj_batch = (proj_in * model_info["batch_in"] / 1e6) + (proj_out * model_info["batch_out"] / 1e6)

    return {
        "model": model,
        "is_reasoning": is_reasoning,
        "latency_s": round(latency, 1),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "visible_output_tokens": visible_output_tokens,
        "valid": valid_count,
        "total": len(records),
        "results": results_per_biz,
        "proj_cost_standard": round(proj_std, 2),
        "proj_cost_batch": round(proj_batch, 2),
    }


def print_comparison(all_results, records):
    print("\n" + "=" * 100)
    print("MODEL SHOOTOUT — SAME 5 BUSINESSES")
    print("=" * 100)

    # Summary table
    print(f"\n{'Model':<14} {'Valid':>6} {'Time':>7} {'InTok':>7} {'OutTok':>8} {'Think':>7} "
          f"{'$Std':>8} {'$Batch':>8}")
    print("-" * 80)
    for r in all_results:
        if "error" in r:
            print(f"{r['model']:<14} {'ERR':>6} {r['latency_s']:>6.1f}s  {r['error'][:50]}")
        else:
            print(f"{r['model']:<14} {r['valid']}/{r['total']:>3} {r['latency_s']:>6.1f}s "
                  f"{r['input_tokens']:>7,} {r['output_tokens']:>8,} {r['reasoning_tokens']:>7,} "
                  f"${r['proj_cost_standard']:>7.2f} ${r['proj_cost_batch']:>7.2f}")

    # Score comparison per business
    business_types = [r["business_type"] for r in records]
    for bt in business_types:
        print(f"\n--- {bt} ---")
        print(f"  {'Model':<14} {'mkt':>4} {'mrg':>4} {'dis':>4} {'cap':>4} {'spd':>4} "
              f"{'team':>4} {'rec':>4} {'own':>4} {'dem':>4} {'dif':>4} {'ai':>5} {'reg':>4} "
              f"{'AVG':>5} {'Reasoning':>5}")
        print("  " + "-" * 90)
        for r in all_results:
            if "error" in r:
                continue
            for biz in r["results"]:
                if biz["business_type"] == bt:
                    s = biz["scores"]
                    avg_scores = [v for v in s.values() if isinstance(v, (int, float))]
                    avg = sum(avg_scores) / len(avg_scores) if avg_scores else 0
                    print(f"  {r['model']:<14} "
                          f"{s.get('market_headroom','?'):>4} {s.get('margin_quality','?'):>4} "
                          f"{s.get('distribution_efficiency','?'):>4} {s.get('startup_capital_intensity','?'):>4} "
                          f"{s.get('speed_to_first_revenue','?'):>4} {s.get('team_model_fit','?'):>4} "
                          f"{s.get('recurring_revenue_potential','?'):>4} {s.get('owner_independence_potential','?'):>4} "
                          f"{s.get('demand_urgency','?'):>4} {s.get('non_commodity_differentiation','?'):>4} "
                          f"{s.get('ai_automation_leverage','?'):>5} {s.get('regulatory_liability_drag','?'):>4} "
                          f"{avg:>5.1f} {biz['whole_reasoning_len']:>5}c")

    # Quality details
    print("\n\nVALIDATION ISSUES:")
    for r in all_results:
        if "error" in r:
            print(f"\n  {r['model']}: FAILED — {r['error']}")
            continue
        issues = [(b["record_id"], b["errors"]) for b in r["results"] if not b["valid"]]
        if issues:
            print(f"\n  {r['model']}:")
            for rid, errs in issues:
                print(f"    [{rid}] {'; '.join(errs[:3])}")
        else:
            print(f"\n  {r['model']}: ALL VALID")


def main():
    system_prompt, user_template = load_prompts()
    records = load_test_records()

    all_results = []
    for model_info in MODELS:
        print(f"\nTesting {model_info['name']}...")
        result = run_model_test(model_info, records, system_prompt, user_template)
        all_results.append(result)
        if "error" not in result:
            print(f"  Done: {result['valid']}/{result['total']} valid, {result['latency_s']}s, "
                  f"thinking={result['reasoning_tokens']} tokens")
        else:
            print(f"  FAILED: {result['error'][:80]}")
        time.sleep(3)

    print_comparison(all_results, records)

    out_path = Path("data/output/model_shootout_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nFull results saved to {out_path}")


if __name__ == "__main__":
    main()
