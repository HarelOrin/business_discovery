import json
import logging

logger = logging.getLogger(__name__)


def parse_response(raw: dict, expected_record_ids: list[str]) -> tuple[list[dict], list[str]]:
    """
    Parse the LLM JSON response.
    Returns (parsed_businesses, errors).
    Each parsed business is the dict from scored_businesses with record_id confirmed.
    """
    errors = []

    scored = raw.get("scored_businesses")
    if not isinstance(scored, list):
        return [], [f"Response missing 'scored_businesses' array. Got keys: {list(raw.keys())}"]

    parsed = []
    returned_ids = set()

    for item in scored:
        rid = item.get("record_id")
        if not rid:
            errors.append("Scored business missing record_id")
            continue
        returned_ids.add(rid)
        parsed.append(item)

    missing = set(expected_record_ids) - returned_ids
    if missing:
        errors.append(f"Missing record_ids in response: {sorted(missing)}")

    extra = returned_ids - set(expected_record_ids)
    if extra:
        errors.append(f"Unexpected record_ids in response: {sorted(extra)}")

    return parsed, errors
