#!/usr/bin/env python3
"""
Dataset Shaper — Phase 2 of the Discovery Engine pipeline.

Transforms 4,331 raw intake records (NAICS + G2) into a canonical dataset
ready for AI scoring. Deterministic normalization and three-tier dedup.
SQLite-first persistence for full audit trail.
"""

import json
import sqlite3
import re
from datetime import datetime, timezone
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_OUTPUT = PROJECT_ROOT / "data" / "output"
RAW_INTAKE_PATH = DATA_OUTPUT / "raw_intake_combined.json"
DB_PATH = DATA_OUTPUT / "dataset_shaper.db"

CANONICAL_DATASET_PATH = DATA_OUTPUT / "canonical_dataset.json"
MERGE_LOG_PATH = DATA_OUTPUT / "merge_log.json"
CONFLICT_QUEUE_PATH = DATA_OUTPUT / "conflict_queue.json"
VALIDATION_REPORT_PATH = DATA_OUTPUT / "dataset_validation_report.json"

SIMILARITY_THRESHOLD = 0.88
CONFLICT_QUEUE_MAX = 500

# Alias groups for Tier 2 dedup — names within a group are treated as equivalent.
ALIAS_GROUPS = [
    ["e-commerce", "ecommerce", "electronic shopping"],
    ["customer relationship management", "crm software"],
    ["enterprise resource planning", "erp software"],
    ["cybersecurity", "cyber security", "information security"],
    ["data center", "datacenter"],
    ["help desk", "helpdesk"],
    ["web hosting", "website hosting"],
    ["email marketing", "e-mail marketing"],
    ["point of sale", "point-of-sale"],
    ["search engine optimization", "seo tools"],
    ["internet of things", "iot"],
    ["voice over internet protocol", "voip"],
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_name(name):
    """Deterministic name normalization for dedup comparison."""
    n = name.strip().lower()
    n = n.rstrip(".")
    n = re.sub(r"\s+", " ", n)
    n = n.replace("\u2013", "-").replace("\u2014", "-")
    n = n.replace("\u2018", "'").replace("\u2019", "'")
    n = n.replace(" & ", " and ")
    return n.strip()


def has_real_definition(definition):
    """True if the definition is substantive (not a cross-ref stub)."""
    if not definition:
        return False
    d = definition.strip()
    if d.lower().startswith("see industry description for"):
        return False
    if d.lower().startswith("see ") and len(d) < 50:
        return False
    return len(d) >= 20


def select_winner(records):
    """Pick the best record from a duplicate group.

    Preference order: real definition > NAICS source > longer definition.
    Returns (winner_index, winner_record).
    """
    scored = []
    for i, rec in enumerate(records):
        has_def = 1 if has_real_definition(rec.get("definition")) else 0
        is_naics = 1 if rec["source_family"] == "naics" else 0
        def_len = len(rec.get("definition") or "")
        scored.append((has_def, is_naics, def_len, i))
    scored.sort(reverse=True)
    best = scored[0][3]
    return best, records[best]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline():
    print("=" * 60)
    print("Dataset Shaper — Phase 2")
    print("=" * 60)
    DATA_OUTPUT.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # LOAD
    # ------------------------------------------------------------------
    with open(RAW_INTAKE_PATH, "r", encoding="utf-8") as f:
        raw_records = json.load(f)
    print(f"\nLoaded {len(raw_records)} raw records")

    # ------------------------------------------------------------------
    # NORMALIZE
    # ------------------------------------------------------------------
    print("\n--- Normalizing ---")
    for rec in raw_records:
        rec["normalized_name"] = normalize_name(rec["business_type"])
    print(f"  Normalized {len(raw_records)} records")

    # ------------------------------------------------------------------
    # TIER 1 — exact match on normalized name
    # ------------------------------------------------------------------
    print("\n--- Tier 1: Exact-Match Dedup ---")
    name_groups = defaultdict(list)
    for rec in raw_records:
        name_groups[rec["normalized_name"]].append(rec)

    dup_group_count = sum(1 for g in name_groups.values() if len(g) > 1)
    print(f"  {len(name_groups)} unique normalized names ({dup_group_count} dup groups)")

    merge_info = defaultdict(list)       # winner_id -> [{record, tier, reason}]
    surviving = {}                       # normalized_name -> winner record
    tier1_merge_count = 0

    for norm_name, group in name_groups.items():
        if len(group) == 1:
            surviving[norm_name] = group[0]
        else:
            widx, winner = select_winner(group)
            surviving[norm_name] = winner
            for i, rec in enumerate(group):
                if i != widx:
                    merge_info[winner["record_id"]].append({
                        "record": rec,
                        "tier": "tier1_exact",
                        "reason": f"Exact normalized match: '{norm_name}'",
                    })
                    tier1_merge_count += 1

    print(f"  Merged {tier1_merge_count} records")
    print(f"  {len(surviving)} surviving after Tier 1")

    # ------------------------------------------------------------------
    # TIER 2 — rule-based alias matching
    # ------------------------------------------------------------------
    print("\n--- Tier 2: Alias Dedup ---")
    alias_to_gidx = {}
    for gidx, group in enumerate(ALIAS_GROUPS):
        for alias in group:
            alias_to_gidx[alias] = gidx

    alias_hits = defaultdict(list)       # group_idx -> [(norm_name, record)]
    for norm_name, rec in surviving.items():
        for alias, gidx in alias_to_gidx.items():
            if alias in norm_name and len(alias) >= max(3, len(norm_name) * 0.3):
                alias_hits[gidx].append((norm_name, rec))
                break

    tier2_merge_count = 0
    for gidx, hits in alias_hits.items():
        if len(hits) <= 1:
            continue
        recs = [h[1] for h in hits]
        widx, winner = select_winner(recs)
        for i, (nm, rec) in enumerate(hits):
            if i == widx:
                continue
            merge_info[winner["record_id"]].append({
                "record": rec,
                "tier": "tier2_alias",
                "reason": f"Alias match: '{nm}' ~ '{hits[widx][0]}'",
            })
            if rec["record_id"] in merge_info:
                merge_info[winner["record_id"]].extend(
                    merge_info.pop(rec["record_id"])
                )
            del surviving[nm]
            tier2_merge_count += 1

    print(f"  Merged {tier2_merge_count} records")
    print(f"  {len(surviving)} surviving after Tier 2")

    # ------------------------------------------------------------------
    # TIER 3 — similarity candidate generation (review queue, NO merges)
    # ------------------------------------------------------------------
    print("\n--- Tier 3: Similarity Candidates ---")
    survivor_list = sorted(surviving.items())   # deterministic order

    stop_words = frozenset([
        "and", "the", "for", "with", "other", "all", "not", "except",
        "including", "services", "service", "software", "management",
        "system", "systems", "activities", "related", "based",
    ])
    token_index = defaultdict(set)
    for idx, (nm, _) in enumerate(survivor_list):
        for tok in re.split(r"[\s\-/,()]+", nm):
            if len(tok) >= 4 and tok not in stop_words:
                token_index[tok].add(idx)

    candidate_pairs = set()
    for tok, indices in token_index.items():
        if len(indices) > 100:
            continue
        ixs = sorted(indices)
        for i in range(len(ixs)):
            for j in range(i + 1, len(ixs)):
                candidate_pairs.add((ixs[i], ixs[j]))
    print(f"  {len(candidate_pairs)} blocked pairs to check")

    conflict_queue_raw = []
    for ia, ib in candidate_pairs:
        na = survivor_list[ia][0]
        nb = survivor_list[ib][0]
        if na == nb:
            continue
        ratio = SequenceMatcher(None, na, nb).ratio()
        if ratio >= SIMILARITY_THRESHOLD:
            conflict_queue_raw.append({
                "src_a": survivor_list[ia][1]["record_id"],
                "src_b": survivor_list[ib][1]["record_id"],
                "name_a": survivor_list[ia][1]["business_type"],
                "name_b": survivor_list[ib][1]["business_type"],
                "similarity": round(ratio, 4),
            })
    conflict_queue_raw.sort(key=lambda c: c["similarity"], reverse=True)
    print(f"  {len(conflict_queue_raw)} candidates above {SIMILARITY_THRESHOLD} threshold")

    # ------------------------------------------------------------------
    # GENERATE CANONICAL RECORDS
    # ------------------------------------------------------------------
    print("\n--- Generating Canonical Records ---")
    canonical_records = []
    final_merge_log = []
    source_to_canonical = {}
    now = datetime.now(timezone.utc).isoformat()

    for idx, (norm_name, rec) in enumerate(survivor_list, 1):
        cid = f"canon_{idx:04d}"
        source_to_canonical[rec["record_id"]] = cid

        merged = merge_info.get(rec["record_id"], [])
        all_sources = [rec] + [m["record"] for m in merged]
        for m in merged:
            source_to_canonical[m["record"]["record_id"]] = cid

        best_def = rec.get("definition")
        best_name = rec["business_type"]
        if not has_real_definition(best_def):
            for src in all_sources:
                if has_real_definition(src.get("definition")):
                    best_def = src["definition"]
                    best_name = src["business_type"]
                    break

        families = sorted(set(s["source_family"] for s in all_sources))
        refs = [s["source_ref"] for s in all_sources]

        canonical_records.append({
            "record_id": cid,
            "business_type": best_name,
            "definition": best_def,
            "business_model_archetype": "unclassified",
            "primary_customer_type": "unclassified",
            "revenue_model": "unclassified",
            "source_family": ",".join(families),
            "source_ref": ";".join(refs),
            "normalization_status": "normalized",
            "record_status": "active",
        })

        final_merge_log.append({
            "canonical_id": cid,
            "source_record_id": rec["record_id"],
            "role": "primary",
            "merge_tier": "none",
            "merge_reason": f"Primary source for {cid}",
            "merged_at": now,
        })
        for m in merged:
            final_merge_log.append({
                "canonical_id": cid,
                "source_record_id": m["record"]["record_id"],
                "role": "merged",
                "merge_tier": m["tier"],
                "merge_reason": m["reason"],
                "merged_at": now,
            })

    print(f"  {len(canonical_records)} canonical records")

    # Remap conflict queue to canonical IDs
    conflict_queue = []
    for c in conflict_queue_raw:
        ca = source_to_canonical.get(c["src_a"])
        cb = source_to_canonical.get(c["src_b"])
        if ca and cb and ca != cb:
            conflict_queue.append({
                "canonical_a_id": ca,
                "canonical_b_id": cb,
                "name_a": c["name_a"],
                "name_b": c["name_b"],
                "similarity_score": c["similarity"],
                "resolution_status": "pending",
            })
    print(f"  {len(conflict_queue)} conflict-queue entries (canonical IDs)")

    # ------------------------------------------------------------------
    # PERSIST TO SQLite
    # ------------------------------------------------------------------
    print("\n--- Persisting to SQLite ---")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript("""
        CREATE TABLE raw_records (
            record_id        TEXT PRIMARY KEY,
            business_type    TEXT NOT NULL,
            definition       TEXT,
            normalized_name  TEXT,
            hierarchy_info   TEXT,
            source_family    TEXT NOT NULL,
            source_ref       TEXT NOT NULL,
            ingested_at      TEXT
        );
        CREATE TABLE canonical_records (
            record_id                TEXT PRIMARY KEY,
            business_type            TEXT NOT NULL,
            definition               TEXT,
            business_model_archetype TEXT NOT NULL,
            primary_customer_type    TEXT NOT NULL,
            revenue_model            TEXT NOT NULL,
            source_family            TEXT NOT NULL,
            source_ref               TEXT NOT NULL,
            normalization_status     TEXT NOT NULL,
            record_status            TEXT NOT NULL
        );
        CREATE TABLE merge_log (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_id     TEXT NOT NULL,
            source_record_id TEXT NOT NULL,
            role             TEXT NOT NULL,
            merge_tier       TEXT NOT NULL,
            merge_reason     TEXT NOT NULL,
            merged_at        TEXT NOT NULL
        );
        CREATE TABLE conflict_queue (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_a_id    TEXT NOT NULL,
            canonical_b_id    TEXT NOT NULL,
            name_a            TEXT NOT NULL,
            name_b            TEXT NOT NULL,
            similarity_score  REAL NOT NULL,
            resolution_status TEXT NOT NULL DEFAULT 'pending'
        );
        CREATE INDEX idx_canon_status ON canonical_records(record_status);
        CREATE INDEX idx_merge_canonical ON merge_log(canonical_id);
    """)

    for rec in raw_records:
        conn.execute(
            "INSERT INTO raw_records VALUES (?,?,?,?,?,?,?,?)",
            (
                rec["record_id"],
                rec["business_type"],
                rec.get("definition"),
                rec.get("normalized_name"),
                json.dumps(rec.get("hierarchy_info", {})),
                rec["source_family"],
                rec["source_ref"],
                rec.get("ingested_at"),
            ),
        )
    for rec in canonical_records:
        conn.execute(
            "INSERT INTO canonical_records VALUES (?,?,?,?,?,?,?,?,?,?)",
            tuple(rec.values()),
        )
    for e in final_merge_log:
        conn.execute(
            "INSERT INTO merge_log (canonical_id,source_record_id,role,merge_tier,merge_reason,merged_at) VALUES (?,?,?,?,?,?)",
            (e["canonical_id"], e["source_record_id"], e["role"],
             e["merge_tier"], e["merge_reason"], e["merged_at"]),
        )
    for c in conflict_queue:
        conn.execute(
            "INSERT INTO conflict_queue (canonical_a_id,canonical_b_id,name_a,name_b,similarity_score,resolution_status) VALUES (?,?,?,?,?,?)",
            (c["canonical_a_id"], c["canonical_b_id"], c["name_a"],
             c["name_b"], c["similarity_score"], c["resolution_status"]),
        )
    conn.commit()
    conn.close()
    print(f"  Saved {DB_PATH.name}")

    # ------------------------------------------------------------------
    # EXPORT JSON artifacts
    # ------------------------------------------------------------------
    print("\n--- Exporting JSON ---")
    with open(CANONICAL_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(canonical_records, f, indent=2, ensure_ascii=False)
    print(f"  {CANONICAL_DATASET_PATH.name}: {len(canonical_records)} records")

    with open(MERGE_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(final_merge_log, f, indent=2, ensure_ascii=False)
    print(f"  {MERGE_LOG_PATH.name}: {len(final_merge_log)} entries")

    with open(CONFLICT_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(conflict_queue, f, indent=2, ensure_ascii=False)
    print(f"  {CONFLICT_QUEUE_PATH.name}: {len(conflict_queue)} entries")

    # ------------------------------------------------------------------
    # VALIDATION GATE
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("VALIDATION GATE")
    print("=" * 60)

    REQUIRED_FIELDS = [
        "record_id", "business_type", "definition",
        "business_model_archetype", "primary_customer_type", "revenue_model",
        "source_family", "source_ref", "normalization_status", "record_status",
    ]
    NON_NULLABLE = [f for f in REQUIRED_FIELDS if f != "definition"]

    active = [r for r in canonical_records if r["record_status"] == "active"]
    checks = []

    # 1) active count >= 700
    c1 = len(active) >= 700
    checks.append({"check": "active_record_count", "threshold": ">= 700",
                    "actual": len(active), "pass": c1})
    print(f"\n  [{'PASS' if c1 else 'FAIL'}] Active records: {len(active)} (need >= 700)")

    # 2) all required fields present
    missing = []
    for r in active:
        for f in REQUIRED_FIELDS:
            if f not in r:
                missing.append(f"{r['record_id']}: {f}")
    c2 = len(missing) == 0
    checks.append({"check": "required_fields", "missing": len(missing), "pass": c2})
    print(f"  [{'PASS' if c2 else 'FAIL'}] Required fields: {len(missing)} missing")

    # 3) non-nullable fields
    nulls = []
    for r in active:
        for f in NON_NULLABLE:
            if r.get(f) is None:
                nulls.append(f"{r['record_id']}: {f}")
    c3 = len(nulls) == 0
    checks.append({"check": "non_nullable", "violations": len(nulls), "pass": c3})
    print(f"  [{'PASS' if c3 else 'FAIL'}] Non-nullable fields: {len(nulls)} violations")

    # 4) provenance
    no_prov = [r["record_id"] for r in active
               if not r["source_family"] or not r["source_ref"]]
    c4 = len(no_prov) == 0
    checks.append({"check": "provenance", "missing": len(no_prov), "pass": c4})
    print(f"  [{'PASS' if c4 else 'FAIL'}] Provenance: {len(no_prov)} without")

    # 5) conflict queue size
    cq_limit = max(CONFLICT_QUEUE_MAX, int(len(active) * 0.15))
    c5 = len(conflict_queue) <= cq_limit
    checks.append({"check": "conflict_queue", "limit": cq_limit,
                    "actual": len(conflict_queue), "pass": c5})
    print(f"  [{'PASS' if c5 else 'FAIL'}] Conflict queue: {len(conflict_queue)} (limit {cq_limit})")

    # 6) schema contract stability
    field_set = set(canonical_records[0].keys()) if canonical_records else set()
    c6 = set(REQUIRED_FIELDS).issubset(field_set)
    checks.append({"check": "schema_contract", "pass": c6})
    print(f"  [{'PASS' if c6 else 'FAIL'}] Schema contract stable")

    overall = all(c["pass"] for c in checks)

    naics_only = len([r for r in active if r["source_family"] == "naics"])
    g2_only = len([r for r in active if r["source_family"] == "g2"])
    cross = len([r for r in active if "," in r["source_family"]])
    with_def = len([r for r in active if r["definition"] is not None])
    wo_def = len([r for r in active if r["definition"] is None])

    summary = {
        "raw_input_records": len(raw_records),
        "canonical_active_records": len(active),
        "from_naics": naics_only,
        "from_g2": g2_only,
        "cross_source": cross,
        "with_definition": with_def,
        "without_definition": wo_def,
        "tier1_merges": tier1_merge_count,
        "tier2_merges": tier2_merge_count,
        "tier3_candidates": len(conflict_queue),
        "merge_log_entries": len(final_merge_log),
    }

    report = {
        "generated_at": now,
        "overall_pass": overall,
        "checks": checks,
        "summary": summary,
        "sample_records": canonical_records[:5],
    }
    with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
    print(f"\n  Summary:")
    for k, v in summary.items():
        print(f"    {k}: {v}")
    print("=" * 60)

    return overall


if __name__ == "__main__":
    success = run_pipeline()
    raise SystemExit(0 if success else 1)
