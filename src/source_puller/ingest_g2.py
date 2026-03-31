"""
G2 Source Puller — Ingest G2 category hierarchy from saved HTML
into raw_intake_g2.json.

Reads:
  data/raw/g2/categories_hierarchy.html

Emits:
  data/output/raw_intake_g2.json

Hierarchy is encoded in the HTML via nested <div class="ml-2"> wrappers.
Each additional ml-2 nesting level represents one level deeper in the
category tree. H2 elements mark top-level parent categories.
"""

import json
import os
from datetime import datetime, timezone

from bs4 import BeautifulSoup, Tag

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "g2")
OUT_DIR = os.path.join(BASE_DIR, "data", "output")

G2_BASE = "https://www.g2.com"


def measure_nesting_depth(element: Tag) -> int:
    """Count ml-2 ancestor divs to determine hierarchy depth within a section."""
    depth = 0
    parent = element.parent
    while parent:
        if isinstance(parent, Tag) and parent.name == "div":
            classes = parent.get("class", [])
            if "ml-2" in classes:
                depth += 1
        parent = parent.parent
    return depth


def extract_hierarchy(html_path: str) -> list[dict]:
    """
    Parse G2 hierarchy HTML and extract category records with parent/child
    relationships.

    Strategy:
    - Find all <h2> elements: these are top-level parent categories
    - Find all <a class="link"> elements with /categories/ hrefs: these are
      the actual categories
    - Determine each category's nesting depth via ml-2 class counting
    - Walk through categories in document order, tracking a depth stack
      to assign parent at each level
    """
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # Collect all H2s and category links in document order
    # We'll use soup.descendants to walk in order
    ingested_at = datetime.now(timezone.utc).isoformat()
    records = []
    seen_slugs = set()

    current_top_category = None

    # Collect all relevant elements in document order
    elements = []
    for el in soup.descendants:
        if not isinstance(el, Tag):
            continue
        if el.name == "h2":
            text = el.get_text(strip=True)
            if text and text not in ("All Categories",):
                elements.append(("h2", text, el))
        elif el.name == "a":
            classes = el.get("class", [])
            href = el.get("href", "")
            if "link" in classes and "/categories/" in href:
                name = el.get_text(strip=True)
                if name:
                    elements.append(("link", name, el))

    # Process elements to build hierarchy
    # depth_stack tracks the parent at each nesting depth
    # depth_stack[0] = top-level category (H2), depth_stack[1] = first subcategory, etc.
    depth_stack: dict[int, str] = {}

    for kind, text, el in elements:
        if kind == "h2":
            current_top_category = text
            depth_stack = {0: text}
            continue

        if current_top_category is None:
            continue

        href = el.get("href", "")
        slug = href.split("/categories/")[-1].strip("/") if "/categories/" in href else ""

        # Skip duplicates (navbar links, mobile menu, etc.)
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        nesting = measure_nesting_depth(el)

        # Update depth stack: this category sits at 'nesting' depth
        depth_stack[nesting] = text
        # Clear deeper levels
        keys_to_remove = [k for k in depth_stack if k > nesting]
        for k in keys_to_remove:
            del depth_stack[k]

        # Parent is the entry one level up, or the top category
        if nesting > 1 and (nesting - 1) in depth_stack:
            parent_name = depth_stack[nesting - 1]
        else:
            parent_name = current_top_category

        # Don't set parent to self
        if parent_name == text:
            parent_name = current_top_category if current_top_category != text else None

        url = f"{G2_BASE}/categories/{slug}" if slug else href

        record = {
            "category_name": text,
            "slug": slug,
            "url": url,
            "description": None,
            "parent_category": parent_name,
            "top_category": current_top_category,
            "hierarchy_level": nesting,
            "source_family": "g2",
            "source_ref": f"g2.com/categories/{slug}",
            "ingested_at": ingested_at,
        }
        records.append(record)

    return records


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    html_path = os.path.join(RAW_DIR, "categories_hierarchy.html")
    print(f"Parsing G2 hierarchy from {html_path}")

    records = extract_hierarchy(html_path)
    print(f"  -> {len(records)} unique categories extracted")

    # Hierarchy stats
    from collections import Counter
    level_counts = Counter(r["hierarchy_level"] for r in records)
    for level in sorted(level_counts):
        print(f"     Depth {level}: {level_counts[level]} categories")

    top_cats = Counter(r["top_category"] for r in records)
    print(f"  -> {len(top_cats)} top-level categories")

    with_parent = sum(1 for r in records if r["parent_category"])
    print(f"  -> {with_parent}/{len(records)} have parent_category set")

    null_names = sum(1 for r in records if not r["category_name"])
    print(f"  -> {null_names} records with null/empty name")

    out_path = os.path.join(OUT_DIR, "raw_intake_g2.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {out_path}")
    print(f"File size: {os.path.getsize(out_path):,} bytes")

    # Print sample records showing hierarchy
    print("\nSample records (various depths):")
    shown = set()
    for r in records:
        depth = r["hierarchy_level"]
        if depth not in shown and len(shown) < 5:
            shown.add(depth)
            print(json.dumps(r, indent=2))
            print("---")

    # Show a parent/child chain example
    print("\nHierarchy chain example:")
    for r in records:
        if r["hierarchy_level"] >= 3:
            chain = [r["category_name"]]
            parent = r["parent_category"]
            visited = set()
            while parent and parent not in visited:
                visited.add(parent)
                chain.append(parent)
                parent_rec = next((x for x in records if x["category_name"] == parent), None)
                parent = parent_rec["parent_category"] if parent_rec else None
            chain.append(r["top_category"])
            # dedupe while preserving order
            seen = set()
            unique_chain = []
            for c in chain:
                if c and c not in seen:
                    seen.add(c)
                    unique_chain.append(c)
            print(f"  {' -> '.join(reversed(unique_chain))}")
            break

    return records


if __name__ == "__main__":
    main()
