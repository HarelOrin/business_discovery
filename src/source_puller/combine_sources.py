"""
Combine raw intake from NAICS and G2 into a single raw_intake_combined.json
with source provenance metadata.

Reads:
  data/output/raw_intake_naics.json
  data/output/raw_intake_g2.json

Emits:
  data/output/raw_intake_combined.json
  data/output/source_provenance_metadata.json
"""

import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(BASE_DIR, "data", "output")


def load_json(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_record(record: dict, source: str) -> dict:
    """
    Normalize source-specific records into a common schema for the combined
    dataset. Preserves all original fields and adds a unified record_id.
    """
    if source == "naics":
        return {
            "record_id": f"naics_{record['naics_code']}",
            "business_type": record["title"],
            "definition": record.get("description"),
            "hierarchy_info": {
                "code": record["naics_code"],
                "level": record["hierarchy_level"],
                "level_label": record["hierarchy_label"],
                "parent_code": record["parent_code"],
            },
            "source_family": record["source_family"],
            "source_ref": record["source_ref"],
            "ingested_at": record["ingested_at"],
        }
    elif source == "g2":
        return {
            "record_id": f"g2_{record['slug']}",
            "business_type": record["category_name"],
            "definition": record.get("description"),
            "hierarchy_info": {
                "slug": record["slug"],
                "url": record["url"],
                "level": record["hierarchy_level"],
                "parent_category": record["parent_category"],
                "top_category": record["top_category"],
            },
            "source_family": record["source_family"],
            "source_ref": record["source_ref"],
            "ingested_at": record["ingested_at"],
        }
    else:
        raise ValueError(f"Unknown source: {source}")


def build_provenance(naics_records: list, g2_records: list) -> dict:
    """Build source provenance metadata."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "naics": {
                "source_family": "naics",
                "source_name": "2022 NAICS (North American Industry Classification System)",
                "source_authority": "U.S. Census Bureau",
                "source_url": "https://www.census.gov/naics/",
                "source_files": [
                    "2-6_digit_2022_Codes.xlsx",
                    "2022_NAICS_Descriptions.xlsx",
                ],
                "record_count": len(naics_records),
                "has_descriptions": True,
                "hierarchy_levels": "2-digit (sector) through 6-digit (national industry)",
                "notes": "Official machine-readable classification. One-time download, stored locally.",
            },
            "g2": {
                "source_family": "g2",
                "source_name": "G2 Software Category Hierarchy",
                "source_authority": "G2.com",
                "source_url": "https://www.g2.com/categories?view_hierarchy=true",
                "source_files": [
                    "categories_hierarchy.html",
                ],
                "record_count": len(g2_records),
                "has_descriptions": False,
                "hierarchy_levels": "top-category -> subcategory (up to 4 levels deep)",
                "notes": "Deterministic HTML scrape of hierarchy view. Descriptions unavailable "
                         "(API requires paid access). Category names are self-descriptive; "
                         "AI world knowledge can supplement.",
            },
        },
        "combined": {
            "total_records": len(naics_records) + len(g2_records),
            "sources_present": ["naics", "g2"],
        },
    }


def verify(combined: list[dict], provenance: dict) -> dict:
    """Run verification checks and return results."""
    checks = {}

    # Both sources present
    families = set(r["source_family"] for r in combined)
    checks["both_sources_present"] = {
        "pass": "naics" in families and "g2" in families,
        "detail": f"Sources found: {sorted(families)}",
    }

    # Row counts non-zero and sane
    naics_count = sum(1 for r in combined if r["source_family"] == "naics")
    g2_count = sum(1 for r in combined if r["source_family"] == "g2")
    checks["row_counts_sane"] = {
        "pass": naics_count > 100 and g2_count > 100,
        "detail": f"NAICS: {naics_count}, G2: {g2_count}, Total: {len(combined)}",
    }

    # Provenance fields populated
    missing_source_family = sum(1 for r in combined if not r.get("source_family"))
    missing_source_ref = sum(1 for r in combined if not r.get("source_ref"))
    missing_ingested = sum(1 for r in combined if not r.get("ingested_at"))
    checks["provenance_populated"] = {
        "pass": missing_source_family == 0 and missing_source_ref == 0 and missing_ingested == 0,
        "detail": (
            f"Missing source_family: {missing_source_family}, "
            f"Missing source_ref: {missing_source_ref}, "
            f"Missing ingested_at: {missing_ingested}"
        ),
    }

    # No schema-breaking nulls on required columns
    required_fields = ["record_id", "business_type", "source_family", "source_ref"]
    null_counts = {}
    for field in required_fields:
        count = sum(1 for r in combined if not r.get(field))
        null_counts[field] = count
    all_required_ok = all(v == 0 for v in null_counts.values())
    checks["no_null_required_fields"] = {
        "pass": all_required_ok,
        "detail": f"Null counts on required fields: {null_counts}",
    }

    # Unique record IDs
    ids = [r["record_id"] for r in combined]
    unique_ids = set(ids)
    checks["unique_record_ids"] = {
        "pass": len(ids) == len(unique_ids),
        "detail": f"Total: {len(ids)}, Unique: {len(unique_ids)}, Dupes: {len(ids) - len(unique_ids)}",
    }

    return checks


def main():
    naics_path = os.path.join(OUT_DIR, "raw_intake_naics.json")
    g2_path = os.path.join(OUT_DIR, "raw_intake_g2.json")

    print("Loading source files...")
    naics_records = load_json(naics_path)
    g2_records = load_json(g2_path)
    print(f"  NAICS: {len(naics_records)} records")
    print(f"  G2:    {len(g2_records)} records")

    print("\nNormalizing to common schema...")
    combined = []
    for r in naics_records:
        combined.append(normalize_record(r, "naics"))
    for r in g2_records:
        combined.append(normalize_record(r, "g2"))
    print(f"  Combined: {len(combined)} records")

    # Write combined
    combined_path = os.path.join(OUT_DIR, "raw_intake_combined.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"\nWritten combined to {combined_path}")
    print(f"  File size: {os.path.getsize(combined_path):,} bytes")

    # Write provenance
    provenance = build_provenance(naics_records, g2_records)
    prov_path = os.path.join(OUT_DIR, "source_provenance_metadata.json")
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, ensure_ascii=False)
    print(f"Written provenance to {prov_path}")

    # Verify
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    checks = verify(combined, provenance)
    all_pass = True
    for name, result in checks.items():
        status = "PASS" if result["pass"] else "FAIL"
        if not result["pass"]:
            all_pass = False
        print(f"  [{status}] {name}: {result['detail']}")

    print()
    if all_pass:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")

    # Write verification results
    verify_path = os.path.join(OUT_DIR, "verification_results.json")
    verify_output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_pass": all_pass,
        "checks": checks,
    }
    with open(verify_path, "w", encoding="utf-8") as f:
        json.dump(verify_output, f, indent=2)
    print(f"Written verification to {verify_path}")

    return all_pass


if __name__ == "__main__":
    passed = main()
    exit(0 if passed else 1)
