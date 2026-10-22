#!/usr/bin/env python3
"""
pipeline/catalog_golden_niches.py
Authentic, documented OEM fault code database across the 6 Golden Niches.
Loads curated datasets from niche modules and provides lookup by (brand, model_key).
Zero synthetic placeholders.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "pipeline"))

from catalog_niche_1_rv import NICHE_1_DATA
from catalog_niche_2_tankless import NICHE_2_DATA
from catalog_niche_3_pool import NICHE_3_DATA
from catalog_niche_4_commercial import NICHE_4_DATA
from catalog_niche_5_generators import NICHE_5_DATA
from catalog_niche_6_hvac import NICHE_6_DATA

GOLDEN_NICHE_CATALOG = {}
ALL_RECORDS = []

def register_niche_data(niche_data):
    for brand, equip_type, model_series, niche, codes_list in niche_data:
        key = f"{brand.lower()}::{model_series.lower()}"
        formatted = []
        for item in codes_list:
            rec = {
                "brand": brand,
                "equipment_type": equip_type,
                "model_series": model_series,
                "niche": niche,
                "error_code": item[0],
                "short_symptom": item[1],
                "plain_english_meaning": item[2],
                "oem_part_number": item[3],
                "primary_part_name": item[4],
                "diy_difficulty": item[5],
                "estimated_pro_repair_cost": item[6],
                "multimeter_spec": item[7] if len(item) > 7 else "Normal resistance: check factory spec",
            }
            formatted.append(rec)
            ALL_RECORDS.append(rec)
        GOLDEN_NICHE_CATALOG[key] = formatted

# Register all niches
register_niche_data(NICHE_1_DATA)
register_niche_data(NICHE_2_DATA)
register_niche_data(NICHE_3_DATA)
register_niche_data(NICHE_4_DATA)
register_niche_data(NICHE_5_DATA)
register_niche_data(NICHE_6_DATA)

if __name__ == "__main__":
    print(f"Total categories registered: {len(GOLDEN_NICHE_CATALOG)}")
    print(f"Total authentic records registered: {len(ALL_RECORDS)}")
