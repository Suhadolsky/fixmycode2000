#!/usr/bin/env python3
"""
pipeline/catalog_niche_5_generators_grills.py
Re-exports Home Standby Generators & Smart Pellet Grills catalog data for Wave 1 & Wave 2.
"""

from catalog_niche_5_generators import NICHE_5_DATA
from catalog_niche_5_generators_grills_wave2 import NICHE_5_WAVE2_DATA

NICHE_5_COMBINED_DATA = NICHE_5_DATA + NICHE_5_WAVE2_DATA
