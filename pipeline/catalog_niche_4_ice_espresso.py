#!/usr/bin/env python3
"""
pipeline/catalog_niche_4_ice_espresso.py
Re-exports Commercial Ice Machines & Prosumer Espresso catalog data for Wave 1 & Wave 2.
"""

from catalog_niche_4_commercial import NICHE_4_DATA
from catalog_niche_4_ice_espresso_wave2 import NICHE_4_WAVE2_DATA

NICHE_4_COMBINED_DATA = NICHE_4_DATA + NICHE_4_WAVE2_DATA
