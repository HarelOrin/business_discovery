"""Quick side-by-side reasoning quality comparison: gpt-4.1 vs gpt-4.1-nano on 2 records."""

import json
import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

system = Path("src/ai_scorer/prompts/scoring_system_prompt.txt").read_text(encoding="utf-8")
user_tpl = Path("src/ai_scorer/prompts/scoring_user_prompt_template.txt").read_text(encoding="utf-8")
data = json.load(open("data/output/canonical_dataset.json"))

sample = [
    {"record_id": r["record_id"], "business_type": r["business_type"],
     "definition": r.get("definition"), "source_family": r.get("source_family")}
    for r in data[:2]
]
user_prompt = user_tpl.replace("{batch_json}", json.dumps(sample, indent=2))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=120, max_retries=0)

for model in ["gpt-4.1", "gpt-4.1-nano"]:
    print(f"\n{'='*70}")
    print(f"MODEL: {model}")
    print(f"{'='*70}")
    resp = client.chat.completions.create(
        model=model, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
        temperature=0.3,
    )
    result = json.loads(resp.choices[0].message.content)
    biz = result["scored_businesses"][0]

    print(f"Business: {biz['business_type']}")
    print(f"\nWhole reasoning:\n  {biz['whole_business_reasoning'][:500]}")
    print(f"\nmarket_headroom: score={biz['metrics']['market_headroom']['score']}")
    print(f"  {biz['metrics']['market_headroom']['reasoning']}")
    print(f"\nmargin_quality: score={biz['metrics']['margin_quality']['score']}")
    print(f"  {biz['metrics']['margin_quality']['reasoning']}")
    print(f"\nowner_independence: score={biz['metrics']['owner_independence_potential']['score']}")
    print(f"  {biz['metrics']['owner_independence_potential']['reasoning']}")
    print(f"\nSummary: {biz['overall_fit_summary']}")
    print(f"\nArchetype: {biz.get('business_model_archetype')} | Customer: {biz.get('primary_customer_type')} | Revenue: {biz.get('revenue_model')}")
    time.sleep(2)
