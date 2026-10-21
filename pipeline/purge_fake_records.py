#!/usr/bin/env python3
"""
pipeline/purge_fake_records.py
Loads data/errors_db.json, filters out synthetic junk/placeholder records,
and saves the cleaned list back to disk and syncs it to site/src/data/errors_db.json.
"""

import os
import re
import json
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATHS = [
    BASE_DIR / "data" / "errors_db.json",
    BASE_DIR / "site" / "src" / "data" / "errors_db.json",
]

# Strict synthetic patterns
FAKE_HVAC_RE = re.compile(r"^(HP|TH|LP|IPM|COM|MOT|EEV|REL|HS|BRD|TR|NUT|CBL|OPT|HAR)-\d{3}$", re.I)
FAKE_OBD_RE = re.compile(r"^(MAF|IAT|STAT|O2|FPR|HPFP|IGN|SPK|INJ|WR|KS|CKP|CMP|CAT|VENT|CAP|VSS|IAC|OPS|ALT|TCM|TCC|WSS|CAN|EBCM)-\d{2}$", re.I)
FAKE_OEM_RE = re.compile(r"^(OEM|PART)-\d+$", re.I)
FAKE_PART_NAME_RE = re.compile(r"(Module|Sensor)\s+\d+", re.I)

def is_fake_record(item: dict) -> bool:
    oem = str(item.get("oem_part_number", "")).strip()
    part = str(item.get("primary_part_name", "")).strip()

    if FAKE_HVAC_RE.match(oem):
        return True
    if FAKE_OBD_RE.match(oem):
        return True
    if FAKE_OEM_RE.match(oem):
        return True
    if FAKE_PART_NAME_RE.search(part):
        return True
    return False

def clean_model_series(model: str) -> str:
    cleaned = re.sub(r"\(.*?\)", "", model).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def clean_part_name(part: str) -> str:
    cleaned = re.sub(r"\(.*?\)", "", part).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def build_part_search_url(brand: str, oem: str, part: str, model: str) -> tuple[str, str]:
    c_part = clean_part_name(part)
    has_real_oem = (
        oem
        and len(oem) >= 4
        and not any(fake in oem.upper() for fake in ["CHECK", "MODEL", "PLATE", "UNKNOWN", "N/A"])
        and not FAKE_HVAC_RE.match(oem)
        and not FAKE_OBD_RE.match(oem)
        and not FAKE_OEM_RE.match(oem)
    )

    if has_real_oem:
        query = f"{brand} {oem} {c_part}"
    else:
        s_model = model.split("/")[0].strip() if "/" in model else model
        query = f"{brand} {s_model} {c_part} replacement"

    # Enforce generous limit of 8-10 words max
    words = query.split()
    if len(words) > 8:
        query = " ".join(words[:8])

    url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}&tag=amazinrevie0a-20"
    return url, query

def purge_and_clean():
    src_path = DB_PATHS[0]
    if not src_path.exists():
        src_path = BASE_DIR / "fixmycode" / "data" / "errors_db.json"

    with open(src_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    total_before = len(records)
    surviving = []
    purged_count = 0

    for item in records:
        if is_fake_record(item):
            purged_count += 1
            continue

        # Clean model_series
        orig_model = item.get("model_series", "")
        item["model_series"] = clean_model_series(orig_model)

        # Build clean Amazon search query (8 words max, no truncation of real names)
        part_url, part_query = build_part_search_url(
            item.get("brand", ""),
            item.get("oem_part_number", ""),
            item.get("primary_part_name", ""),
            item.get("model_series", ""),
        )
        item["part_affiliate_url"] = part_url
        item["primary_part_affiliate_url"] = part_url
        item["primary_part_search_query"] = part_query

        # Ensure no hallucinated ASINs or cart bundle links
        item["asin_part"] = None
        item["asin_tool"] = None
        item["asin_consumable"] = None
        item["has_asin_bundle"] = False
        item["bundle_cart_url"] = None

        surviving.append(item)

    print(f"Purged {purged_count} fake records. Remaining verified records: {len(surviving)}")

    for path in DB_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(surviving, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(surviving)} verified records to {path}")

if __name__ == "__main__":
    purge_and_clean()
