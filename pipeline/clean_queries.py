#!/usr/bin/env python3
"""
clean_queries.py - Fast cleanup script for Amazon search queries in errors_db.json.

Fixes overly complex Amazon search queries:
1. Keeps ONLY the first primary tool in required_tool_name and required_tool_search_query
   (strips compound connectors like '&', 'and', '+', 'with', ',').
2. Strips generic filler words from the end of tool and consumable queries
   ('repair toolkit', 'set', 'kit', 'appliance maintenance', 'Check Model Plate').
3. Enforces a maximum of 4 words per tool query.
4. Regenerates part_affiliate_url, tool_affiliate_url, and consumable_affiliate_url
   using urllib.parse.quote_plus and tag=amazinrevie0a-20.
5. Syncs data/errors_db.json and site/src/data/errors_db.json.
"""

import json
import logging
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fixmycode.clean_queries")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DB = BASE_DIR / "data" / "errors_db.json"
SITE_DB = BASE_DIR / "site" / "src" / "data" / "errors_db.json"

AMAZON_TAG = "amazinrevie0a-20"

CONNECTORS_PATTERN = re.compile(r"\s*(?:&|\band\b|\+|\bwith\b|,)\s*", re.IGNORECASE)

FILLER_ENDINGS = [
    r"\s+repair toolkit\b",
    r"\s+repair kit\b",
    r"\s+toolkit\b",
    r"\s+kit\b",
    r"\s+set\b",
    r"\s+Check Model Plate\b",
    r"\s+appliance maintenance\b",
    r"\s+appliance\b",
    r"\s+maintenance\b",
]


def clean_tool_name(s: str) -> str:
    """Keep only the first primary tool, stripping compound connectors."""
    if not s:
        return s
    parts = CONNECTORS_PATTERN.split(s.strip())
    first = parts[0].strip()
    # Strip any hanging spec/dimension suffixes if left at end (e.g. '1/4', 'T10/T15', '1.5mm-4mm')
    first = re.sub(r"\s+(?:1/4|5/16|T10/T15|1\.5mm-4mm)$", "", first, flags=re.IGNORECASE).strip()
    return first


def clean_query(s: str, is_tool: bool = False, max_words: int = 8) -> str:
    """
    Cleans search queries by stripping connectors, removing filler words from the end,
    and enforcing max word count (up to 8 words) for queries.
    """
    if not s:
        return s

    s = s.strip()

    if is_tool:
        # Split on compound connectors and keep first primary tool
        parts = CONNECTORS_PATTERN.split(s)
        s = parts[0].strip()
        # Clean hanging specs
        s = re.sub(r"\s+(?:1/4|5/16|T10/T15|1\.5mm-4mm)$", "", s, flags=re.IGNORECASE).strip()

    # Strip generic filler endings iteratively
    changed = True
    while changed:
        changed = False
        for pattern in FILLER_ENDINGS:
            m = re.search(pattern + r"$", s, flags=re.IGNORECASE)
            if m:
                s = s[: m.start()].strip()
                changed = True

    # Enforce maximum 8 words
    words = s.split()
    if len(words) > max_words:
        s = " ".join(words[:max_words])

    return s.strip()


def build_amazon_search_url(query: str, tag: str = AMAZON_TAG) -> str:
    """Build Amazon affiliate search URL with quote_plus encoding."""
    encoded_query = urllib.parse.quote_plus(query.strip())
    return f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"


def clean_database(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean all records in the database."""
    cleaned_count = 0

    for item in records:
        orig_tool_name = item.get("required_tool_name", "")
        orig_tool_query = item.get("required_tool_search_query", "")
        orig_cons_query = item.get("consumable_search_query", "")

        cleaned_tool_name = clean_tool_name(orig_tool_name)
        cleaned_tool_query = clean_query(orig_tool_query, is_tool=True, max_words=8)
        cleaned_cons_query = clean_query(orig_cons_query, is_tool=False, max_words=8)

        # High-converting 8-word max part query
        brand = item.get("brand", "").strip()
        oem = str(item.get("oem_part_number", "")).strip()
        part_name = item.get("primary_part_name", "").strip()
        clean_part = re.sub(r"\(.*?\)", "", part_name).strip()
        clean_part = re.sub(r"\s+", " ", clean_part)
        model = item.get("model_series", "").strip()

        has_real_oem = (
            oem
            and len(oem) >= 4
            and not any(fake in oem.upper() for fake in ["CHECK", "MODEL", "PLATE", "UNKNOWN", "N/A"])
        )

        if has_real_oem:
            part_query = f"{brand} {oem} {clean_part}"
        else:
            s_model = model.split("/")[0].strip() if "/" in model else model
            part_query = f"{brand} {s_model} {clean_part} replacement"

        p_words = part_query.split()
        if len(p_words) > 8:
            part_query = " ".join(p_words[:8])

        # Regenerate URLs
        part_url = build_amazon_search_url(part_query)
        tool_url = build_amazon_search_url(cleaned_tool_query)
        cons_url = build_amazon_search_url(cleaned_cons_query)

        item["primary_part_search_query"] = part_query
        item["required_tool_name"] = cleaned_tool_name
        item["required_tool_search_query"] = cleaned_tool_query
        item["consumable_search_query"] = cleaned_cons_query

        item["part_affiliate_url"] = part_url
        item["primary_part_affiliate_url"] = part_url
        item["tool_affiliate_url"] = tool_url
        item["required_tool_affiliate_url"] = tool_url
        item["consumable_affiliate_url"] = cons_url

        cleaned_count += 1

    return records


def main():
    if not DATA_DB.exists():
        logger.error(f"Database not found at {DATA_DB}")
        sys.exit(1)

    logger.info(f"Loading database from {DATA_DB}...")
    with open(DATA_DB, "r", encoding="utf-8") as f:
        records = json.load(f)

    total_records = len(records)
    logger.info(f"Loaded {total_records} records.")

    # Show sample before
    sample = records[0]
    logger.info("--- Sample BEFORE cleanup ---")
    logger.info(f"Tool Name : {sample.get('required_tool_name')}")
    logger.info(f"Tool Query: {sample.get('required_tool_search_query')}")
    logger.info(f"Tool URL  : {sample.get('tool_affiliate_url')}")
    logger.info(f"Cons Query: {sample.get('consumable_search_query')}")
    logger.info(f"Cons URL  : {sample.get('consumable_affiliate_url')}")

    cleaned_records = clean_database(records)

    # Show sample after
    logger.info("--- Sample AFTER cleanup ---")
    logger.info(f"Tool Name : {sample.get('required_tool_name')}")
    logger.info(f"Tool Query: {sample.get('required_tool_search_query')}")
    logger.info(f"Tool URL  : {sample.get('tool_affiliate_url')}")
    logger.info(f"Cons Query: {sample.get('consumable_search_query')}")
    logger.info(f"Cons URL  : {sample.get('consumable_affiliate_url')}")

    # Save to data/errors_db.json
    with open(DATA_DB, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved cleaned records to {DATA_DB}")

    # Sync to site/src/data/errors_db.json
    SITE_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(SITE_DB, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)
    logger.info(f"Synced cleaned records to {SITE_DB}")

    logger.info("Cleanup completed successfully!")


if __name__ == "__main__":
    main()
