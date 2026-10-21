#!/usr/bin/env python3
"""
pipeline/purge_fake_records.py
Purges all synthetic placeholder records from errors_db.json and cleans model_series.
"""

import os
import re
import json
import urllib.parse
from pathlib import Path

AMAZON_TAG = "amazinrevie0a-20"
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATHS = [
    BASE_DIR / "data" / "errors_db.json",
    BASE_DIR / "site" / "src" / "data" / "errors_db.json",
]

FAKE_HVAC_RE = re.compile(r"^(HP|TH|LP|IPM|COM|MOT|EEV|REL|HS|BRD|TR|NUT|CBL|OPT|HAR)-\d{3}$", re.I)
FAKE_OBD_RE = re.compile(r"^(MAF|IAT|STAT|O2|FPR|HPFP|IGN|SPK|INJ|WR|KS|CKP|CMP|CAT|VENT|CAP|VSS|IAC|OPS|ALT|TCM|TCC|WSS|CAN|EBCM)-\d{2}$", re.I)
FAKE_OEM_RE = re.compile(r"^(OEM|PART)-\d+$", re.I)
FAKE_PART_NAME_RE = re.compile(r"(Module|Sensor)\s+\d+$", re.I)

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
    # Strip parenthetical descriptions like (VANOS Solenoid, ...)
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

    # Enforce maximum 8 words without cutting off part name
    words = query.split()
    if len(words) > 8:
        query = " ".join(words[:8])
    
    url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}&tag={AMAZON_TAG}"
    return url, query

def purge_and_clean():
    src_path = DB_PATHS[0]
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

        # Build clean 8-word Amazon part search URL
        part_url, part_query = build_part_search_url(
            item.get("brand", ""),
            item.get("oem_part_number", ""),
            item.get("primary_part_name", ""),
            item.get("model_series", ""),
        )
        item["part_affiliate_url"] = part_url
        item["primary_part_affiliate_url"] = part_url
        item["primary_part_search_query"] = part_query

        surviving.append(item)

    print(f"Total before purge: {total_before}")
    print(f"Purged synthetic records: {purged_count}")
    print(f"Surviving authentic records: {len(surviving)}")

    for path in DB_PATHS:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(surviving, f, indent=2, ensure_ascii=False)
        print(f"Saved clean records to {path}")

if __name__ == "__main__":
    purge_and_clean()
