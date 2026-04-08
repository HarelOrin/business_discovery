"""
OpenAI API client for the AI Scorer.

Supports both synchronous (real-time) and Batch API modes.
Synchronous mode is the primary path due to org-level Batch API token limits.
"""

import os
import json
import time
import logging
from pathlib import Path
from openai import OpenAI, RateLimitError, APITimeoutError, APIConnectionError, APIError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "o3"
MAX_COMPLETION_TOKENS = 16384


def _get_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------------------------
# Synchronous API (primary path)
# ---------------------------------------------------------------------------

def call_sync(system_prompt: str, user_prompt: str,
              max_retries: int = 5) -> tuple[dict, dict]:
    """Call o3 synchronously with JSON mode and retry on transient errors.

    Returns (parsed_json_response, usage_dict).
    usage_dict has keys: prompt_tokens, completion_tokens, reasoning_tokens.
    """
    client = _get_client()
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                response_format={"type": "json_object"},
                max_completion_tokens=MAX_COMPLETION_TOKENS,
                messages=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            usage = response.usage
            usage_dict = {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "reasoning_tokens": 0,
            }
            if usage and hasattr(usage, "completion_tokens_details") and usage.completion_tokens_details:
                usage_dict["reasoning_tokens"] = getattr(
                    usage.completion_tokens_details, "reasoning_tokens", 0
                ) or 0

            content = response.choices[0].message.content
            return json.loads(content), usage_dict

        except RateLimitError as e:
            last_error = e
            wait = min(2 ** attempt * 10, 120)
            logger.warning("Rate limited (attempt %d/%d). Waiting %ds...",
                           attempt, max_retries, wait)
            time.sleep(wait)

        except (APITimeoutError, APIConnectionError) as e:
            last_error = e
            wait = 2 ** attempt * 3
            logger.warning("Transient error (attempt %d/%d): %s. Waiting %ds...",
                           attempt, max_retries, e, wait)
            time.sleep(wait)

        except APIError as e:
            last_error = e
            if e.status_code and e.status_code >= 500:
                wait = 2 ** attempt * 3
                logger.warning("Server error %s (attempt %d/%d). Waiting %ds...",
                               e.status_code, attempt, max_retries, wait)
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"API call failed after {max_retries} attempts: {last_error}")


# ---------------------------------------------------------------------------
# Batch API helpers (kept for reference / future use)
# ---------------------------------------------------------------------------

def prepare_batch_jsonl(requests: list[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for req in requests:
            line = {
                "custom_id": req["custom_id"],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [
                        {"role": "developer", "content": req["system_prompt"]},
                        {"role": "user", "content": req["user_prompt"]},
                    ],
                    "response_format": {"type": "json_object"},
                    "max_completion_tokens": MAX_COMPLETION_TOKENS,
                },
            }
            f.write(json.dumps(line) + "\n")
    logger.info("Wrote %d requests to %s", len(requests), output_path)
    return output_path


def upload_batch_file(filepath: Path) -> str:
    client = _get_client()
    with open(filepath, "rb") as f:
        file_obj = client.files.create(file=f, purpose="batch")
    logger.info("Uploaded %s -> file id %s", filepath.name, file_obj.id)
    return file_obj.id


def create_batch(input_file_id: str) -> str:
    client = _get_client()
    batch = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Created batch %s (status: %s)", batch.id, batch.status)
    return batch.id


def check_batch_status(api_batch_id: str) -> dict:
    client = _get_client()
    batch = client.batches.retrieve(api_batch_id)
    counts = batch.request_counts
    error_code = None
    if batch.errors and batch.errors.data:
        error_code = batch.errors.data[0].code
    return {
        "id": batch.id, "status": batch.status,
        "total": counts.total if counts else 0,
        "completed": counts.completed if counts else 0,
        "failed": counts.failed if counts else 0,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
        "error_code": error_code,
    }


def download_batch_results(output_file_id: str) -> list[dict]:
    client = _get_client()
    content = client.files.content(output_file_id)
    lines = content.text.strip().split("\n")
    results = [json.loads(line) for line in lines if line.strip()]
    logger.info("Downloaded %d results from file %s", len(results), output_file_id)
    return results


def get_active_openai_batches() -> list[dict]:
    client = _get_client()
    batches = client.batches.list(limit=100)
    return [
        {"id": b.id, "status": b.status,
         "completed": b.request_counts.completed if b.request_counts else 0,
         "total": b.request_counts.total if b.request_counts else 0}
        for b in batches.data
        if b.status in ("in_progress", "validating", "finalizing")
    ]
