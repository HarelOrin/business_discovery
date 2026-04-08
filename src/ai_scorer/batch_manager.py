"""
SQLite-backed tracking for Batch API scoring workflow.

Tables:
  api_jobs  — OpenAI Batch API job metadata
  requests  — individual API requests (each scores 5 businesses)
  records   — per-business scoring status and results
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DB_PATH = Path("data/output/scoring_progress.db")
DATASET_PATH = Path("data/output/canonical_dataset.json")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS api_jobs (
            api_batch_id    TEXT PRIMARY KEY,
            input_file_id   TEXT,
            output_file_id  TEXT,
            error_file_id   TEXT,
            status          TEXT NOT NULL DEFAULT 'submitted',
            request_count   INTEGER NOT NULL DEFAULT 0,
            is_retry        INTEGER NOT NULL DEFAULT 0,
            collected       INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT NOT NULL,
            completed_at    TEXT
        );
        CREATE TABLE IF NOT EXISTS requests (
            custom_id       TEXT PRIMARY KEY,
            record_ids      TEXT NOT NULL,
            api_batch_id    TEXT,
            status          TEXT NOT NULL DEFAULT 'pending',
            attempt_count   INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS records (
            record_id        TEXT PRIMARY KEY,
            scoring_status   TEXT NOT NULL DEFAULT 'pending',
            scoring_result   TEXT,
            model_used       TEXT,
            attempt_count    INTEGER NOT NULL DEFAULT 0,
            tokens_input     INTEGER NOT NULL DEFAULT 0,
            tokens_output    INTEGER NOT NULL DEFAULT 0,
            tokens_reasoning INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


def reset_db():
    conn = _get_conn()
    conn.executescript("""
        DROP TABLE IF EXISTS api_jobs;
        DROP TABLE IF EXISTS requests;
        DROP TABLE IF EXISTS records;
    """)
    conn.commit()
    conn.close()
    init_db()
    logger.info("Database reset complete.")


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

def load_dataset() -> list[dict]:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_records_for_ids(record_ids: list[str], dataset: list[dict]) -> list[dict]:
    id_set = set(record_ids)
    return [r for r in dataset if r["record_id"] in id_set]


# ---------------------------------------------------------------------------
# Record tracking
# ---------------------------------------------------------------------------

def register_records(records: list[dict]):
    conn = _get_conn()
    for r in records:
        conn.execute(
            "INSERT OR IGNORE INTO records (record_id, scoring_status) VALUES (?, 'pending')",
            (r["record_id"],),
        )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    logger.info("Registered records. Total in DB: %d", count)
    conn.close()


def get_pending_record_ids() -> list[str]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT record_id FROM records WHERE scoring_status='pending' ORDER BY record_id"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_failed_record_ids() -> list[str]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT record_id FROM records WHERE scoring_status='failed' ORDER BY record_id"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def save_record_result(record_id: str, result_json: str, model: str,
                       tokens_in: int = 0, tokens_out: int = 0,
                       tokens_reasoning: int = 0):
    conn = _get_conn()
    conn.execute(
        """UPDATE records
           SET scoring_status='scored', scoring_result=?, model_used=?,
               tokens_input=?, tokens_output=?, tokens_reasoning=?,
               attempt_count=attempt_count+1
           WHERE record_id=?""",
        (result_json, model, tokens_in, tokens_out, tokens_reasoning, record_id),
    )
    conn.commit()
    conn.close()


def mark_record_failed(record_id: str):
    conn = _get_conn()
    conn.execute(
        "UPDATE records SET scoring_status='failed', attempt_count=attempt_count+1 WHERE record_id=?",
        (record_id,),
    )
    conn.commit()
    conn.close()


def reset_failed_to_pending(record_ids: list[str]):
    conn = _get_conn()
    for rid in record_ids:
        conn.execute(
            "UPDATE records SET scoring_status='pending', scoring_result=NULL WHERE record_id=?",
            (rid,),
        )
    conn.commit()
    logger.info("Reset %d failed records to pending.", len(record_ids))
    conn.close()


# ---------------------------------------------------------------------------
# Request tracking
# ---------------------------------------------------------------------------

def create_request_groups(record_ids: list[str], batch_size: int = 5,
                          prefix: str = "req") -> list[dict]:
    groups = []
    for i in range(0, len(record_ids), batch_size):
        chunk = record_ids[i:i + batch_size]
        idx = (i // batch_size) + 1
        groups.append({
            "custom_id": f"{prefix}_{idx:06d}",
            "record_ids": chunk,
        })
    return groups


def register_requests(groups: list[dict], api_batch_id: str | None = None):
    conn = _get_conn()
    for g in groups:
        conn.execute(
            "INSERT OR REPLACE INTO requests (custom_id, record_ids, api_batch_id, status, attempt_count) "
            "VALUES (?, ?, ?, 'pending', 0)",
            (g["custom_id"], json.dumps(g["record_ids"]), api_batch_id),
        )
    conn.commit()
    logger.info("Registered %d requests.", len(groups))
    conn.close()


def link_requests_to_job(custom_ids: list[str], api_batch_id: str):
    conn = _get_conn()
    for cid in custom_ids:
        conn.execute(
            "UPDATE requests SET api_batch_id=? WHERE custom_id=?",
            (api_batch_id, cid),
        )
    conn.commit()
    conn.close()


def get_request_record_ids(custom_id: str) -> list[str]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT record_ids FROM requests WHERE custom_id=?", (custom_id,)
    ).fetchone()
    conn.close()
    return json.loads(row[0]) if row else []


def mark_request_completed(custom_id: str):
    conn = _get_conn()
    conn.execute(
        "UPDATE requests SET status='completed', attempt_count=attempt_count+1 WHERE custom_id=?",
        (custom_id,),
    )
    conn.commit()
    conn.close()


def mark_request_failed(custom_id: str):
    conn = _get_conn()
    conn.execute(
        "UPDATE requests SET status='failed', attempt_count=attempt_count+1 WHERE custom_id=?",
        (custom_id,),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# API job tracking
# ---------------------------------------------------------------------------

def register_api_job(api_batch_id: str, input_file_id: str,
                     request_count: int, is_retry: bool = False):
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO api_jobs (api_batch_id, input_file_id, status, request_count, is_retry, created_at) "
        "VALUES (?, ?, 'submitted', ?, ?, ?)",
        (api_batch_id, input_file_id, request_count, int(is_retry), now),
    )
    conn.commit()
    conn.close()


def update_api_job(api_batch_id: str, status: str,
                   output_file_id: str | None = None,
                   error_file_id: str | None = None):
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    sets = ["status=?"]
    params: list = [status]

    if output_file_id:
        sets.append("output_file_id=?")
        params.append(output_file_id)
    if error_file_id:
        sets.append("error_file_id=?")
        params.append(error_file_id)
    if status in ("completed", "failed", "expired", "cancelled"):
        sets.append("completed_at=?")
        params.append(now)

    params.append(api_batch_id)
    conn.execute(f"UPDATE api_jobs SET {', '.join(sets)} WHERE api_batch_id=?", params)
    conn.commit()
    conn.close()


def mark_job_collected(api_batch_id: str):
    conn = _get_conn()
    conn.execute("UPDATE api_jobs SET collected=1 WHERE api_batch_id=?", (api_batch_id,))
    conn.commit()
    conn.close()


def get_latest_api_job() -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM api_jobs ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_uncollected_completed_job() -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM api_jobs WHERE status='completed' AND collected=0 "
        "ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_active_api_jobs() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM api_jobs WHERE status NOT IN "
        "('completed', 'failed', 'expired', 'cancelled') ORDER BY created_at"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_retry_count() -> int:
    conn = _get_conn()
    count = conn.execute("SELECT COUNT(*) FROM api_jobs WHERE is_retry=1").fetchone()[0]
    conn.close()
    return count


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

def get_progress() -> dict:
    conn = _get_conn()
    total = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    scored = conn.execute("SELECT COUNT(*) FROM records WHERE scoring_status='scored'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM records WHERE scoring_status='failed'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM records WHERE scoring_status='pending'").fetchone()[0]

    tok_in = conn.execute("SELECT COALESCE(SUM(tokens_input),0) FROM records WHERE scoring_status='scored'").fetchone()[0]
    tok_out = conn.execute("SELECT COALESCE(SUM(tokens_output),0) FROM records WHERE scoring_status='scored'").fetchone()[0]
    tok_reason = conn.execute("SELECT COALESCE(SUM(tokens_reasoning),0) FROM records WHERE scoring_status='scored'").fetchone()[0]

    jobs = conn.execute("SELECT COUNT(*) FROM api_jobs").fetchone()[0]
    active = conn.execute(
        "SELECT COUNT(*) FROM api_jobs WHERE status NOT IN "
        "('completed','failed','expired','cancelled')"
    ).fetchone()[0]

    conn.close()
    return {
        "total_records": total, "scored": scored, "failed": failed, "pending": pending,
        "tokens_input": tok_in, "tokens_output": tok_out, "tokens_reasoning": tok_reason,
        "total_jobs": jobs, "active_jobs": active,
    }
