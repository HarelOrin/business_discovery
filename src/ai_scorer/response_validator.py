import logging

logger = logging.getLogger(__name__)

REQUIRED_METRICS = [
    "market_headroom", "margin_quality", "distribution_efficiency",
    "startup_capital_intensity", "speed_to_first_revenue", "team_model_fit",
    "recurring_revenue_potential", "owner_independence_potential",
    "demand_urgency", "non_commodity_differentiation", "ai_automation_leverage",
    "regulatory_liability_drag",
]

VERBAL_LABELS = {"Weak", "Emerging", "Solid", "Strong"}
CONFIDENCE_VALUES = {"low", "medium", "high"}


def validate_business(biz: dict) -> list[str]:
    """Validate a single scored business dict. Returns list of error strings (empty = valid)."""
    errors = []
    rid = biz.get("record_id", "UNKNOWN")

    metrics = biz.get("metrics")
    if not isinstance(metrics, dict):
        errors.append(f"[{rid}] 'metrics' missing or not a dict")
        return errors

    for m in REQUIRED_METRICS:
        entry = metrics.get(m)
        if not entry:
            errors.append(f"[{rid}] Missing metric: {m}")
            continue

        score = entry.get("score")
        if not isinstance(score, int) or score < 0 or score > 3:
            errors.append(f"[{rid}] {m}.score invalid: {score}")

        reasoning = entry.get("reasoning", "")
        if not reasoning:
            errors.append(f"[{rid}] {m}.reasoning is empty")
        elif not any(label in reasoning for label in VERBAL_LABELS):
            errors.append(f"[{rid}] {m}.reasoning missing verbal rank label")

        confidence = entry.get("confidence", "")
        if confidence not in CONFIDENCE_VALUES:
            errors.append(f"[{rid}] {m}.confidence invalid: '{confidence}'")

    if not biz.get("whole_business_reasoning"):
        errors.append(f"[{rid}] whole_business_reasoning is empty")

    if not biz.get("overall_fit_summary"):
        errors.append(f"[{rid}] overall_fit_summary is empty")

    for field in ("business_model_archetype", "primary_customer_type", "revenue_model"):
        if not biz.get(field):
            errors.append(f"[{rid}] {field} is empty")

    return errors
