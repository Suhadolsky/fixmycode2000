#!/usr/bin/env python3
"""
2_extractor.py - Smart PDF Filtering, Gemini Structured Output, and Affiliate Link Generation
Processes raw PDF service manuals, filters error/troubleshooting pages via PyMuPDF,
extracts structured error codes and troubleshooting kits via Gemini 2.5 Flash,
and generates SEO slugs and Amazon affiliate links.
"""

import argparse
import datetime
import hashlib
import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote_plus, urlencode

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import pymupdf  # PyMuPDF
from slugify import slugify
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fixmycode.extractor")

# Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_PDFS_DIR = DATA_DIR / "raw_pdfs"
PROCESSED_HASHES_FILE = DATA_DIR / "processed_hashes.json"
ERRORS_DB_FILE = DATA_DIR / "errors_db.json"
SITE_DATA_DIR = BASE_DIR / "site" / "src" / "data"
SITE_ERRORS_DB_FILE = SITE_DATA_DIR / "errors_db.json"

# Trigger keywords for token-saving page filter
TRIGGER_KEYWORDS = [
    "error",
    "fault",
    "code",
    "troubleshoot",
    "symptom",
    "cause",
    "remedy",
    "alarm",
    "blink",
    "flashing",
    "led",
    "replace",
    "ohm",
    "sensor",
]


class ErrorFixItem(BaseModel):
    brand: str = Field(description="Normalized brand name, e.g., 'Bosch'")
    equipment_type: str = Field(description="e.g., 'Dishwasher', 'Pool Heater'")
    model_series: str = Field(description="Specific model or series, e.g., 'SHPM65Z55N / 500 Series'")
    error_code: str = Field(description="Exact code, e.g., 'E24', 'ERR 03', 'Flashing Red LED x3'")
    short_symptom: str = Field(description="e.g., 'Water Not Draining / Drain Fault'")
    plain_english_meaning: str = Field(
        description="2-3 sentences explaining the root technical cause without fluff"
    )
    diy_difficulty: str = Field(
        description="Strictly one of: 'Easy (15 mins)', 'Medium (30-45 mins)', 'Hard (Pro Recommended)'"
    )
    estimated_pro_repair_cost: str = Field(
        description="Realistic range in USD, e.g., '$180 - $260'"
    )
    diagnostic_and_fix_steps: List[str] = Field(
        description="3 to 5 concrete technical steps (include safety/unplug step first, multimeter/inspection checks, and part swap)"
    )
    primary_part_name: str = Field(description="e.g., 'Drain Pump Assembly'")
    oem_part_number: str = Field(
        description="Extracted OEM number if present in text, otherwise 'Check Model Plate'"
    )
    primary_part_search_query: str = Field(
        description="Ultra-specific Amazon search query: '{brand} {model_series} {oem_part_number} {primary_part_name} replacement'"
    )
    required_tool_name: str = Field(description="e.g., 'Torx T20 Screwdriver & Hose Clamp Pliers'")
    required_tool_search_query: str = Field(description="Amazon search query for the specific tool")
    consumable_name: str = Field(description="e.g., 'Food-Grade Silicone O-Ring Grease'")
    consumable_search_query: str = Field(description="Amazon search query for the maintenance consumable")
    asin_part: Optional[str] = Field(
        default=None, description="Amazon ASIN for the replacement part if identifiable"
    )
    asin_tool: Optional[str] = Field(
        default=None, description="Amazon ASIN for the required tool if identifiable"
    )
    asin_consumable: Optional[str] = Field(
        default=None, description="Amazon ASIN for the consumable if identifiable"
    )
    faq_questions: List[Dict[str, str]] = Field(
        description="2 common follow-up Q&As (keys: 'question', 'answer') for Google FAQ schema"
    )


class ExtractedManualData(BaseModel):
    items: List[ErrorFixItem] = Field(
        default_factory=list,
        description="List of all distinct error codes and troubleshooting fixes found in the manual",
    )


def load_environment() -> tuple[str, str]:
    """Load and validate required environment variables."""
    load_dotenv(BASE_DIR / ".env")
    gemini_key = os.getenv("GEMINI_API_KEY")
    amazon_tag = os.getenv("AMAZON_TAG", "fixmycode-20")

    if not gemini_key:
        logger.warning(
            "GEMINI_API_KEY environment variable is missing or empty. "
            "Please configure it in fixmycode/.env"
        )
    return gemini_key or "", amazon_tag


def calculate_file_md5(file_path: Path) -> str:
    """Calculate the MD5 checksum of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_processed_hashes() -> Dict[str, Any]:
    """Load the dictionary of already-processed file hashes."""
    if not PROCESSED_HASHES_FILE.exists():
        return {}
    try:
        with open(PROCESSED_HASHES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.error(f"Error reading {PROCESSED_HASHES_FILE}: {e}")
        return {}


def save_processed_hashes(hashes_dict: Dict[str, Any]) -> None:
    """Safely persist processed hashes to disk using atomic write."""
    PROCESSED_HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=PROCESSED_HASHES_FILE.parent,
        delete=False,
    )
    try:
        json.dump(hashes_dict, temp_file, indent=2, ensure_ascii=False)
        temp_file.flush()
        temp_file.close()
        Path(temp_file.name).replace(PROCESSED_HASHES_FILE)
    except Exception as e:
        logger.error(f"Failed to write {PROCESSED_HASHES_FILE}: {e}")
        if Path(temp_file.name).exists():
            Path(temp_file.name).unlink(missing_ok=True)


def load_errors_db() -> List[Dict[str, Any]]:
    """Load existing error records from errors_db.json."""
    if not ERRORS_DB_FILE.exists():
        return []
    try:
        with open(ERRORS_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Error reading {ERRORS_DB_FILE}: {e}")
        return []


def save_errors_db(errors: List[Dict[str, Any]]) -> None:
    """Safely persist error records using atomic write and sync to site/src/data/."""
    ERRORS_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=ERRORS_DB_FILE.parent,
        delete=False,
    )
    try:
        json.dump(errors, temp_file, indent=2, ensure_ascii=False)
        temp_file.flush()
        temp_file.close()
        Path(temp_file.name).replace(ERRORS_DB_FILE)

        # Sync to site/src/data/errors_db.json for Astro build
        SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ERRORS_DB_FILE, SITE_ERRORS_DB_FILE)
        logger.debug(f"Synced {ERRORS_DB_FILE.name} to {SITE_ERRORS_DB_FILE}")
    except Exception as e:
        logger.error(f"Failed to write {ERRORS_DB_FILE}: {e}")
        if Path(temp_file.name).exists():
            Path(temp_file.name).unlink(missing_ok=True)


def filter_pdf_pages(pdf_path: Path) -> tuple[str, int, int]:
    """
    Step 3.1: Token-saving local filter using PyMuPDF.
    Keeps only pages containing at least 2 distinct trigger keywords.
    Returns: (concatenated_text, matched_pages_count, total_pages_count)
    """
    kept_chunks: List[str] = []
    total_pages = 0

    try:
        doc = pymupdf.open(str(pdf_path))
        total_pages = len(doc)

        for page_index, page in enumerate(doc):
            text = page.get_text() or ""
            text_lower = text.lower()

            matched_keywords = {kw for kw in TRIGGER_KEYWORDS if kw in text_lower}
            if len(matched_keywords) >= 2:
                page_header = f"--- PAGE {page_index + 1} ---"
                kept_chunks.append(f"{page_header}\n{text.strip()}")

        doc.close()
    except Exception as e:
        logger.warning(f"Failed to read PDF '{pdf_path.name}': {e}")
        return "", 0, total_pages

    concatenated = "\n\n".join(kept_chunks)
    return concatenated, len(kept_chunks), total_pages


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=3, max=15),
    reraise=True,
)
def call_gemini_extractor(client: genai.Client, manual_text: str) -> ExtractedManualData:
    """
    Step 3.2: Call Gemini 2.5 Flash with structured output schema.
    Extracts all distinct error codes and repair solutions.
    """
    prompt = (
        "You are an expert appliance and equipment repair engineer analyzing technician service manual pages.\n"
        "Your task is to identify and extract EVERY specific error code, fault code, diagnostic blink pattern, "
        "or troubleshooting symptom described in the text below.\n\n"
        "Guidelines:\n"
        "1. For each error code, determine the exact code (e.g., 'E24', 'F01', '3 Blinks').\n"
        "2. Provide plain_english_meaning with exact technical cause without filler.\n"
        "3. Provide diy_difficulty strictly matching one of: 'Easy (15 mins)', 'Medium (30-45 mins)', 'Hard (Pro Recommended)'.\n"
        "4. Provide estimated_pro_repair_cost as a realistic USD range like '$180 - $260'.\n"
        "5. Provide diagnostic_and_fix_steps as 3 to 5 clear, sequential steps (first step should cover power safety/unplugging, then multimeter or visual check, then replacement).\n"
        "6. Provide specific replacement part, tools, and maintenance consumable with actionable Amazon search queries. NEVER include price in search queries.\n"
        "7. Provide 2 common follow-up FAQs for SEO schema.\n\n"
        "MANUAL PAGES CONTENT:\n"
        f"{manual_text}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedManualData,
            temperature=0.1,
        ),
    )

    if response.parsed and isinstance(response.parsed, ExtractedManualData):
        return response.parsed

    # Fallback to json parsing from text
    raw_text = response.text or "{}"
    return ExtractedManualData.model_validate_json(raw_text)


def build_amazon_search_url(query: str, tag: str) -> str:
    """Construct an Amazon Associates affiliate search URL."""
    encoded_query = quote_plus(query.strip())
    return f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"


def make_cart_injection_url(
    asin_part: Optional[str],
    asin_tool: Optional[str],
    asin_consumable: Optional[str],
    tag: str,
    fallback_query: Optional[str] = None,
) -> str:
    """
    Creates a link for instant addition of the complete repair kit
    (Part + Tool + Consumable) into the Amazon cart.
    Extends the affiliate attribution cookie window to 90 days.
    If ASINs are not yet defined, smoothly falls back to a verified search query.
    """
    base_url = "https://www.amazon.com/gp/aws/cart/add.html"
    params: Dict[str, str] = {
        "AssociateTag": tag,
    }

    item_idx = 1
    if asin_part and asin_part.strip():
        params[f"ASIN.{item_idx}"] = asin_part.strip()
        params[f"Quantity.{item_idx}"] = "1"
        item_idx += 1
    if asin_tool and asin_tool.strip():
        params[f"ASIN.{item_idx}"] = asin_tool.strip()
        params[f"Quantity.{item_idx}"] = "1"
        item_idx += 1
    if asin_consumable and asin_consumable.strip():
        params[f"ASIN.{item_idx}"] = asin_consumable.strip()
        params[f"Quantity.{item_idx}"] = "1"
        item_idx += 1

    if item_idx > 1:
        # At least one ASIN is available for cart injection
        query_string = urlencode(params)
        return f"{base_url}?{query_string}"

    # Smooth fallback to search query
    fallback = fallback_query or "appliance replacement parts"
    encoded = quote_plus(fallback.strip())
    return f"https://www.amazon.com/s?k={encoded}&tag={tag}"


def generate_unique_slug(
    brand: str,
    model_series: str,
    error_code: str,
    existing_slugs: Set[str],
) -> str:
    """
    Generate a deterministic, SEO-friendly URL slug using python-slugify:
    {brand}-{model_series}-error-code-{error_code}-fix
    Deduplicates slugs by appending an identifier if needed.
    """
    clean_brand = slugify(brand) or "general"
    clean_model = slugify(model_series)[:35] or "series"
    clean_code = slugify(error_code) or "code"

    base_slug = f"{clean_brand}-{clean_model}-error-code-{clean_code}-fix"
    candidate = base_slug

    counter = 2
    while candidate in existing_slugs:
        candidate = f"{base_slug}-{counter}"
        counter += 1

    return candidate


def enrich_item(
    item: ErrorFixItem,
    amazon_tag: str,
    existing_slugs: Set[str],
    source_filename: str = "manual.pdf",
    source_md5: str = "manual_hash",
) -> Dict[str, Any]:
    """
    Step 3.3: Post-Processing & Affiliate URL Generation
    Generates SEO slug and Amazon affiliate links.
    """
    slug = generate_unique_slug(item.brand, item.model_series, item.error_code, existing_slugs)
    existing_slugs.add(slug)

    brand_slug = slugify(item.brand) or "general"
    equip_slug = slugify(item.equipment_type) or "appliance"

    part_url = build_amazon_search_url(item.primary_part_search_query, amazon_tag)
    tool_url = build_amazon_search_url(item.required_tool_search_query, amazon_tag)
    consumable_url = build_amazon_search_url(item.consumable_search_query, amazon_tag)

    bundle_fallback_query = f"{item.brand} {item.model_series} {item.primary_part_name} repair kit"
    bundle_cart_url = make_cart_injection_url(
        item.asin_part,
        item.asin_tool,
        item.asin_consumable,
        amazon_tag,
        fallback_query=bundle_fallback_query,
    )
    has_asin_bundle = bool(
        (item.asin_part and item.asin_part.strip())
        or (item.asin_tool and item.asin_tool.strip())
        or (item.asin_consumable and item.asin_consumable.strip())
    )

    data = item.model_dump()
    data.update(
        {
            "slug": slug,
            "brand_slug": brand_slug,
            "equipment_slug": equip_slug,
            # Exact field names specified:
            "part_affiliate_url": part_url,
            "tool_affiliate_url": tool_url,
            "consumable_affiliate_url": consumable_url,
            "bundle_cart_url": bundle_cart_url,
            "has_asin_bundle": has_asin_bundle,
            "asin_part": item.asin_part,
            "asin_tool": item.asin_tool,
            "asin_consumable": item.asin_consumable,
            # Aliases for template convenience
            "primary_part_affiliate_url": part_url,
            "required_tool_affiliate_url": tool_url,
            "source_file": source_filename,
            "source_hash": source_md5,
            "extracted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )
    return data


def seed_demo_data(amazon_tag: str) -> None:
    """Generate 10 realistic sample records across target brands and equipment types."""
    logger.info("Generating 10 realistic demo records for immediate frontend development...")

    sample_items: List[ErrorFixItem] = [
        ErrorFixItem(
            brand="Bosch",
            equipment_type="Dishwasher",
            model_series="800 Series / SHPM78Z55N",
            error_code="E24",
            short_symptom="Drain System Fault / Water Will Not Pump Out",
            plain_english_meaning="The controller detected that water remains in the sump after the timed drain cycle. Usually caused by a jammed drain pump impeller, clogged sink air gap, or stuck check valve flap.",
            diy_difficulty="Medium (30-45 mins)",
            estimated_pro_repair_cost="$190 - $270",
            diagnostic_and_fix_steps=[
                "Turn off main circuit breaker or unplug the dishwasher from the under-sink outlet.",
                "Remove the lower dish rack, unscrew the cylindrical fine filter, and soak up standing sump water with a sponge.",
                "Pry off the white plastic drain pump impeller cover using a blunt butter knife or spoon; inspect for chicken bones, fruit pits, or broken glass.",
                "Verify the impeller spins freely by hand with magnetic resistance every 90 degrees; if seized, replace the pump motor.",
                "Inspect the sink garbage disposal knockout plug and drain hose high loop for grease blockages."
            ],
            primary_part_name="Drain Pump Motor Assembly",
            oem_part_number="00631200",
            primary_part_search_query="Bosch 800 Series 00631200 Drain Pump Motor Assembly replacement",
            required_tool_name="Torx T20 Screwdriver & Curved Needle-Nose Pliers",
            required_tool_search_query="Torx T20 Screwdriver and Needle Nose Pliers set",
            consumable_name="Food-Grade Silicone Lubricant Grease",
            consumable_search_query="Food Grade Silicone O-Ring Lubricant Grease",
            asin_part="B07987G65M",
            asin_tool="B00002X29G",
            asin_consumable="B000DZFUPC",
            faq_questions=[
                {
                    "question": "Can I reset the Bosch E24 error by unplugging the unit?",
                    "answer": "A power cycle can clear the micro-controller buffer, but if physical debris remains locked in the pump impeller cavity, E24 will trigger again within 2 minutes of the next wash cycle."
                },
                {
                    "question": "Why did E24 appear right after installing a new garbage disposal?",
                    "answer": "This almost always occurs because the plastic drain knockout plug inside the new disposal inlet port was not punched out before attaching the dishwasher drain hose."
                }
            ]
        ),
        ErrorFixItem(
            brand="Bosch",
            equipment_type="Dishwasher",
            model_series="500 Series / SHP865ZD5N",
            error_code="E15",
            short_symptom="Water Protection System Active / Base Float Triggered",
            plain_english_meaning="Water has leaked into the safety condensation pan beneath the wash tub, lifting the polystyrene emergency float switch and locking the drain pump on continuously.",
            diy_difficulty="Easy (15 mins)",
            estimated_pro_repair_cost="$160 - $240",
            diagnostic_and_fix_steps=[
                "Disconnect the dishwasher from wall power immediately to stop the safety drain pump.",
                "Turn off the under-sink hot water supply shutoff valve.",
                "Carefully remove the bottom toe-kick kickplate with a T20 screwdriver and inspect the plastic drip tray.",
                "Soak up water in the base pan with microfiber towels or tilt the appliance backward at a 45-degree angle to drain onto a towel.",
                "Inspect the sump perimeter silicone gasket and door perimeter seal for tears or soap residue leaks."
            ],
            primary_part_name="Sump Basin Silicone Seal Repair Kit",
            oem_part_number="12005744",
            primary_part_search_query="Bosch 500 Series 12005744 Sump Basin Silicone Seal Repair Kit",
            required_tool_name="Torx T20 Driver & Inspection Flashlight",
            required_tool_search_query="Torx T20 Driver and LED Mechanic Inspection Light",
            consumable_name="Dishwasher Gasket Sealant Paste",
            consumable_search_query="High Temp Waterproof Appliance Gasket Sealant",
            asin_part="B08N5MDFG4",
            asin_tool="B07KMR9T1H",
            asin_consumable="B0002UEPVI",
            faq_questions=[
                {
                    "question": "Will tilting the dishwasher permanently fix error E15?",
                    "answer": "Tilting drains the tray and temporarily lowers the float switch, but unless you seal the weeping sump bowl gasket, the leak will recur within 3 to 10 wash cycles."
                },
                {
                    "question": "Why won't my Bosch dishwasher turn off during an E15 error?",
                    "answer": "The safety flood switch bypasses the front control panel to run the drain pump non-stop to prevent residential flooring flood damage."
                }
            ]
        ),
        ErrorFixItem(
            brand="Pentair",
            equipment_type="Pool Heater",
            model_series="MasterTemp 400 / 250",
            error_code="SFS",
            short_symptom="Stack Flue Sensor Fault / High Exhaust Temperature",
            plain_english_meaning="The stack flue exhaust sensor detected temperatures exceeding 480°F (249°C) or open circuit resistance, indicating low thermal heat exchange efficiency or thermal regulator failure.",
            diy_difficulty="Medium (30-45 mins)",
            estimated_pro_repair_cost="$220 - $350",
            diagnostic_and_fix_steps=[
                "Shut down both 240V pool equipment circuit breakers and close the manual gas cock valve.",
                "Unscrew the side access panel to locate the stainless steel exhaust flue elbow.",
                "Disconnect the two yellow sensor leads and test cold resistance with a digital multimeter (normal reading is 3.5 to 4.2 mega-ohms at 75°F).",
                "If reading reads open circuit (infinite resistance) or shorted, unthread the 1/2-inch brass sensor from the exhaust manifold.",
                "Inspect the thermal regulator valve located behind the water header to ensure proper cold bypass mixing."
            ],
            primary_part_name="Stack Flue Sensor (SFS) Probe",
            oem_part_number="42002-0024S",
            primary_part_search_query="Pentair MasterTemp 42002-0024S Stack Flue Sensor replacement",
            required_tool_name="Digital Multimeter & 1/2-inch Deep Well Socket",
            required_tool_search_query="Digital Multimeter and Deep Well Socket Wrench Set",
            consumable_name="High-Temperature Anti-Seize Thread Lubricant",
            consumable_search_query="High Temperature Anti-Seize Thread Lubricant 1600F",
            asin_part="B004W4TUG4",
            asin_tool="B0002STR36",
            asin_consumable="B0002UEPVI",
            faq_questions=[
                {
                    "question": "Can I bypass the Pentair SFS sensor with a resistor?",
                    "answer": "Never bypass the stack flue sensor. It protects against melting the internal composite header and causing a catastrophic combustion box fire."
                },
                {
                    "question": "What causes the SFS code besides a bad sensor probe?",
                    "answer": "A calcified thermal regulator that remains stuck open, restricting cool pool water flow through the heat exchanger tubes."
                }
            ]
        ),
        ErrorFixItem(
            brand="Pentair",
            equipment_type="Pool Heater",
            model_series="MasterTemp / Max-E-Therm",
            error_code="HLS",
            short_symptom="High Limit Switch Opened / Overheating Exchanger",
            plain_english_meaning="The internal water temperature inside the heat exchanger manifold exceeded 135°F (57°C), tripping the bi-metallic high limit safety switch.",
            diy_difficulty="Medium (30-45 mins)",
            estimated_pro_repair_cost="$180 - $290",
            diagnostic_and_fix_steps=[
                "Switch off electrical power to the heater at the subpanel breaker.",
                "Check that the pool filter pump is primed and operating at full RPM with clean cartridge filters.",
                "Remove the water header manifold cover and check continuity across both high limit switch terminals.",
                "Replace the 135°F or 150°F thermal high limit switch if continuity fails to restore once the unit cools.",
                "Clean the internal bypass valve spring mechanism to restore correct water velocity through copper tubes."
            ],
            primary_part_name="High Limit Switch 135°F Assembly",
            oem_part_number="42001-0063S",
            primary_part_search_query="Pentair MasterTemp 42001-0063S High Limit Switch 135F replacement",
            required_tool_name="Nut Driver 5/16-inch & Multimeter",
            required_tool_search_query="Nut Driver Set 5/16 and Electrical Continuity Tester",
            consumable_name="Heat Transfer Compound Paste",
            consumable_search_query="Thermal Heatsink Grease Compound Paste",
            asin_part="B002FS38DY",
            asin_tool="B00009WNTK",
            asin_consumable="B0795DP122",
            faq_questions=[
                {
                    "question": "Why does HLS trip only when the pool pump turns off?",
                    "answer": "If the heater fires right as the filtration timer cuts pump power, residual heat boils standing water in the tubes, instantly opening the high limit switch."
                },
                {
                    "question": "How do I verify if the HLS switch is genuinely defective?",
                    "answer": "After the heater is completely cold, use an ohmmeter across the two brass terminals. It must read 0 ohms (closed circuit)."
                }
            ]
        ),
        ErrorFixItem(
            brand="Breville",
            equipment_type="Espresso Machine",
            model_series="Barista Touch / Oracle Touch (BES880 / BES990)",
            error_code="ER03",
            short_symptom="Steam Boiler Overheating / NTC Thermistor Open Circuit",
            plain_english_meaning="The microcontroller detected abnormal voltage or open circuit on the dedicated steam boiler NTC temperature probe, disabling heating to prevent thermal runaway.",
            diy_difficulty="Hard (Pro Recommended)",
            estimated_pro_repair_cost="$210 - $320",
            diagnostic_and_fix_steps=[
                "Unplug the espresso machine and allow dual boilers to depressurize and cool completely for 4 hours.",
                "Remove the top bean hopper, rear water reservoir, and 5 perimeter Torx screws to slide off the stainless steel casing.",
                "Locate the steam boiler on the right side and inspect the NTC temperature sensor wire clip for mineral corrosion or steam leak burns.",
                "Measure resistance across the two sensor pins; it should read approximately 50k to 100k ohms at room temperature (25°C).",
                "Unthread the brass thermal sensor probe, replace the O-ring, and insert the new replacement sensor harness."
            ],
            primary_part_name="Boiler NTC Temperature Sensor Probe",
            oem_part_number="SP0001815",
            primary_part_search_query="Breville Barista Oracle Touch NTC Temperature Sensor replacement",
            required_tool_name="Torx T10 / T15 Security Drivers & Needle Nose Pliers",
            required_tool_search_query="Precision Torx Security Screwdriver Set T10 T15",
            consumable_name="Food-Grade EPDM High Temp O-Rings #008",
            consumable_search_query="Food Grade High Temp Silicone EPDM O-Ring Assortment Breville",
            asin_part="B0874W4FGT",
            asin_tool="B07BMMXFLC",
            asin_consumable="B01G1DFJNK",
            faq_questions=[
                {
                    "question": "Can severe scale buildup trigger Breville ER03?",
                    "answer": "Yes, dense calcium scale insulating the heating element wall creates localized hot spots that disrupt thermistor resistance readings."
                },
                {
                    "question": "Can I continue pulling espresso shots with an ER03 fault?",
                    "answer": "No, the firmware initiates an emergency safety lockout on both group head and steam thermoblocks until the circuit is repaired."
                }
            ]
        ),
        ErrorFixItem(
            brand="Breville",
            equipment_type="Espresso Machine",
            model_series="Dual Boiler (BES920XL)",
            error_code="ER01",
            short_symptom="Group Head Flow Meter Signal Failure",
            plain_english_meaning="The volumetric flow meter is not sending pulse signals to the PCB while the vibration pump is energized, indicating an air lock, scale blockage, or damaged impeller hall sensor.",
            diy_difficulty="Medium (30-45 mins)",
            estimated_pro_repair_cost="$175 - $250",
            diagnostic_and_fix_steps=[
                "Unplug the machine from mains electrical supply.",
                "Remove the rear access panel to expose the cold water tubing harness.",
                "Disconnect the flow meter inlet and outlet silicon tubes; inspect the 1mm internal orifice for lime scale flakes.",
                "Open the plastic flow meter housing and verify the internal miniature magnetic impeller spins freely on its ceramic pin.",
                "Swap the 3-pin Digmesa flow meter assembly if the internal hall effect chip failed."
            ],
            primary_part_name="Digmesa Flow Meter Turbine Assembly",
            oem_part_number="SP0001509",
            primary_part_search_query="Breville Dual Boiler BES920XL Digmesa Flow Meter replacement",
            required_tool_name="Hose Pinch Clamps & Phillips #1 Screwdriver",
            required_tool_search_query="Micro Hose Clamp Pliers and Phillips Precision Screwdriver",
            consumable_name="Organic Sulfamic Acid Espresso Descaler",
            consumable_search_query="Commercial Espresso Machine Descaling Powder Sulfamic Acid",
            asin_part="B0868Z2876",
            asin_tool="B004OVN078",
            asin_consumable="B003ATX0B0",
            faq_questions=[
                {
                    "question": "How do I fix a vapor lock causing ER01 after descaling?",
                    "answer": "Run the hot water wand dispensing cycle continuously for 30 seconds to force trapped air bubbles out of the flow meter chamber."
                },
                {
                    "question": "Does vinegar work to clean the Breville flow meter?",
                    "answer": "Avoid vinegar; acetic acid ruins internal silicone seals and leaves residual odors. Use certified espresso machine descalers."
                }
            ]
        ),
        ErrorFixItem(
            brand="Hayward",
            equipment_type="Pool Pump",
            model_series="TriStar VS / Super Pump VS",
            error_code="Err 0x0002",
            short_symptom="Drive Over-Current / Motor Rotor Stalled",
            plain_english_meaning="The variable speed drive inverter module detected excessive phase current draw to the brushless motor, triggered by physical debris jamming the wet-end impeller or damaged motor bearings.",
            diy_difficulty="Easy (15 mins)",
            estimated_pro_repair_cost="$240 - $380",
            diagnostic_and_fix_steps=[
                "Disconnect main 230V power to the pump at the breaker panel and wait 5 minutes for drive capacitors to discharge.",
                "Relieve filter tank pressure and remove the clear strainer pot lid.",
                "Reach your fingers through the front suction port into the center eye of the closed impeller to remove pine needles, acorns, or pebbles.",
                "Remove the motor shaft rear plastic cap and use a flathead screwdriver or 1/2-inch wrench to verify the rotor rotates with minimal resistance.",
                "Inspect the variable speed drive wiring harness terminals for burnt contacts or corrosion."
            ],
            primary_part_name="Closed Vane Impeller Replacement",
            oem_part_number="SPX3205C",
            primary_part_search_query="Hayward TriStar VS SPX3205C Impeller Assembly replacement",
            required_tool_name="Impeller Wedge Tool & 9/16-inch Open End Wrench",
            required_tool_search_query="Pool Pump Impeller Removal Tool and Open End Wrench Set",
            consumable_name="Silicone O-Ring Lube & Shaft Seal Sealant",
            consumable_search_query="Pool Pump O-Ring Lube and Ceramic Shaft Seal Kit",
            asin_part="B0032JTC1W",
            asin_tool="B003X5M7F8",
            asin_consumable="B002K6P0DO",
            faq_questions=[
                {
                    "question": "What if the impeller is clear but Err 0x0002 persists?",
                    "answer": "If the shaft turns smoothly by hand but the error trips instantly when energized, the drive's integrated IPM (Intelligent Power Module) inverter has failed."
                },
                {
                    "question": "Can low electrical line voltage cause Err 0x0002?",
                    "answer": "Yes, if the supply drops below 208V under high head pressure load, current spikes proportionally to maintain motor torque."
                }
            ]
        ),
        ErrorFixItem(
            brand="Hayward",
            equipment_type="Pool Pump",
            model_series="EcoStar VS (SP3400VSP)",
            error_code="Err 0x0021",
            short_symptom="Drive Heat Sink Over-Temperature",
            plain_english_meaning="The internal aluminum heat sink temperature of the variable speed drive exceeded 185°F (85°C), forcing an automatic safety shutdown to protect the microprocessor.",
            diy_difficulty="Easy (15 mins)",
            estimated_pro_repair_cost="$150 - $220",
            diagnostic_and_fix_steps=[
                "De-energize pump power at the circuit breaker.",
                "Inspect the rear motor fan shroud for spider webs, leaves, or mulch restricting cooling airflow.",
                "Ensure the pump is not completely enclosed in an unventilated shed or exposed to direct reflective afternoon sun without a heat shield.",
                "Blow out aluminum heat sink cooling fins using compressed air or an electric duster.",
                "Verify the motor rear centrifugal cooling fan is intact and not cracked or spinning loose on the shaft."
            ],
            primary_part_name="Motor Cooling Fan & Shroud Assembly",
            oem_part_number="SPX3400FAN",
            primary_part_search_query="Hayward EcoStar SPX3400FAN Motor Cooling Fan replacement",
            required_tool_name="Compressed Air Can & 1/4-inch Nut Driver",
            required_tool_search_query="Compressed Air Duster Can and Nut Driver Set",
            consumable_name="UV-Resistant Protective Pump Equipment Cover",
            consumable_search_query="UV Proof Waterproof Pool Pump Motor Sun Shield Cover",
            asin_part="B008E6OQ04",
            asin_tool="B0000AE67M",
            asin_consumable="B08B1M8K2T",
            faq_questions=[
                {
                    "question": "Will the pump automatically restart after cooling down?",
                    "answer": "Yes, once internal heat sink temperatures drop back below 150°F (65°C), the drive clears 0x0021 and resumes its scheduled timer profile."
                },
                {
                    "question": "Can running the pump at minimum RPM in summer cause 0x0021?",
                    "answer": "Yes, because the internal fan is shaft-driven. At 800 RPM in 105°F ambient heat, airflow is insufficient for continuous heavy loads."
                }
            ]
        ),
        ErrorFixItem(
            brand="Navien",
            equipment_type="Tankless Water Heater",
            model_series="NPE-240A / NPE-210S / NPE-A2",
            error_code="E003",
            short_symptom="Ignition Failure / Flame Not Established",
            plain_english_meaning="The burner controller attempted spark ignition 3 consecutive times but the flame rod sensor detected no ionization current within 5 seconds, indicating lack of gas supply or dirty flame rod.",
            diy_difficulty="Medium (30-45 mins)",
            estimated_pro_repair_cost="$180 - $310",
            diagnostic_and_fix_steps=[
                "Turn off electrical power switch beneath the unit and verify gas supply shutoff valve is fully open in parallel with the pipe.",
                "Check that the gas meter or propane regulator isn't frozen or locked out due to low tank pressure.",
                "Remove the 4 front cover thumb screws, disconnect the high-voltage spark electrode and flame ionization rod cables.",
                "Unscrew the flame rod assembly from the burner manifold and clean carbon/oxidation off the metal probes using ultra-fine #0000 steel wool.",
                "Verify static gas inlet pressure with a digital manometer (3.5 to 10.5 inches Water Column for Natural Gas; 8.0 to 13.5 for Propane)."
            ],
            primary_part_name="Dual Flame Rod and Ignition Electrode Assembly",
            oem_part_number="30010972A",
            primary_part_search_query="Navien NPE 30010972A Flame Rod Ignition Electrode replacement",
            required_tool_name="Gas Manometer & Phillips #2 Magnetic Screwdriver",
            required_tool_search_query="Digital Gas Manometer Pressure Tester and Phillips Screwdriver",
            consumable_name="#0000 Ultra-Fine Steel Wool & Burner Gasket",
            consumable_search_query="0000 Grade Steel Wool Pads and High Temp Gas Burner Gasket",
            asin_part="B07Q5W4G87",
            asin_tool="B0767R6LNY",
            asin_consumable="B075FDF9R6",
            faq_questions=[
                {
                    "question": "Can a clogged intake air filter cause Navien E003?",
                    "answer": "Yes, a dirty stainless mesh air intake screen starves the premix burner of oxygen, preventing the initial gas-air spark from catching."
                },
                {
                    "question": "Why does E003 only happen during windy storms?",
                    "answer": "Strong wind gusts down an improper two-pipe venting termination without an approved rain cap can blow out the burner ignition flame."
                }
            ]
        ),
        ErrorFixItem(
            brand="Navien",
            equipment_type="Tankless Water Heater",
            model_series="NPE-240A / NPE-180A",
            error_code="E110",
            short_symptom="Abnormal Flue Exhaust Gas Temperature",
            plain_english_meaning="Flue gas temperature sensor detected exhaust temps exceeding 149°F (65°C) for PVC or 194°F (90°C) for CPVC/Polypropylene, indicating lime scale insulating the secondary condensing heat exchanger.",
            diy_difficulty="Medium (30-45 mins)",
            estimated_pro_repair_cost="$210 - $340",
            diagnostic_and_fix_steps=[
                "Power down the unit and isolate cold and hot plumbing service valves.",
                "Perform a thorough 60-minute recirculation flush using 4 gallons of food-grade virgin white vinegar or citric acid solution.",
                "Unscrew the flue gas temperature thermistor located directly on the upper PVC vent collar.",
                "Inspect the thermistor tip for soot or condensation sediment and measure resistance against temperature curve specifications.",
                "Check the two-stage condensate trap and neutralize drain lines for mineral sediment blockages."
            ],
            primary_part_name="Flue Exhaust Gas Thermistor Sensor",
            oem_part_number="30008577A",
            primary_part_search_query="Navien NPE Flue Gas Temperature Sensor 30008577A replacement",
            required_tool_name="Tankless Water Heater Submersible Flush Pump Kit",
            required_tool_search_query="Tankless Water Heater Flush Kit Submersible Pump and Hoses",
            consumable_name="Food-Grade Citric Acid Tankless Descaler Solution",
            consumable_search_query="Tankless Water Heater Descaler Solution Citric Acid Powder",
            asin_part="B07P962G87",
            asin_tool="B0743B7Z7K",
            asin_consumable="B07R8T9V9W",
            faq_questions=[
                {
                    "question": "How often should I flush my Navien heater to prevent E110?",
                    "answer": "Annual flushing is mandatory. In hard water areas (>120 mg/L calcium carbonate), flush every 6 to 9 months to maintain thermal transfer efficiency."
                },
                {
                    "question": "Will E110 damage my PVC exhaust pipes?",
                    "answer": "E110 is an active safety protection feature designed specifically to shut down the burner before hot exhaust gases can soften or warp standard schedule 40 PVC venting."
                }
            ]
        ),
    ]

    existing_db = load_errors_db()
    existing_slugs: Set[str] = {err.get("slug") for err in existing_db if "slug" in err}

    added_count = 0
    for item in sample_items:
        enriched = enrich_item(
            item,
            amazon_tag,
            existing_slugs,
            source_filename="demo_seed_manual.pdf",
            source_md5=f"demo_seed_{slugify(item.brand)}_{slugify(item.error_code)}",
        )
        slug = enriched["slug"]

        # Check if already present
        matched = False
        for idx, ex in enumerate(existing_db):
            if ex.get("slug") == slug or (
                ex.get("brand") == item.brand and ex.get("error_code") == item.error_code
            ):
                existing_db[idx] = enriched
                matched = True
                break
        if not matched:
            existing_db.append(enriched)
            added_count += 1

    save_errors_db(existing_db)

    # Record in processed hashes
    hashes = load_processed_hashes()
    hashes["demo_seed_manual_hash"] = {
        "filename": "demo_seed_manual.pdf",
        "status": "success",
        "total_pages": 10,
        "matched_pages": 10,
        "codes_found": len(sample_items),
        "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    save_processed_hashes(hashes)

    logger.info(
        f"Demo seeding complete! Total database now contains {len(existing_db)} error codes. "
        f"Synced to {SITE_ERRORS_DB_FILE}."
    )


def run_extractor(pdf_file_filter: Optional[str] = None) -> None:
    """Main extraction routine for all unprocessed PDFs in data/raw_pdfs/."""
    gemini_key, amazon_tag = load_environment()
    if not gemini_key:
        logger.error("Extraction aborted: GEMINI_API_KEY is required in .env")
        return

    RAW_PDFS_DIR.mkdir(parents=True, exist_ok=True)
    all_pdfs = sorted(RAW_PDFS_DIR.glob("*.pdf"))

    if not all_pdfs:
        logger.info(f"No PDF files found in {RAW_PDFS_DIR}. Run 1_harvester.py first.")
        return

    processed_hashes = load_processed_hashes()
    errors_db = load_errors_db()

    # Index existing errors by slug for deduplication
    existing_slugs: Set[str] = {err.get("slug") for err in errors_db if "slug" in err}

    client = genai.Client(api_key=gemini_key)
    logger.info(
        f"Starting extraction. Found {len(all_pdfs)} total PDFs. "
        f"{len(processed_hashes)} already recorded in processed_hashes.json."
    )

    unprocessed_pdfs: List[Path] = []
    for pdf_path in all_pdfs:
        if pdf_file_filter and pdf_file_filter not in pdf_path.name:
            continue
        try:
            file_md5 = calculate_file_md5(pdf_path)
            if file_md5 not in processed_hashes:
                unprocessed_pdfs.append(pdf_path)
        except Exception as e:
            logger.warning(f"Could not hash {pdf_path}: {e}")

    logger.info(f"{len(unprocessed_pdfs)} PDFs require processing.")

    total_new_errors = 0

    for pdf_path in tqdm(unprocessed_pdfs, desc="Extracting PDFs"):
        file_md5 = calculate_file_md5(pdf_path)
        logger.info(f"\nProcessing: {pdf_path.name} (MD5: {file_md5})")

        # Step 3.1: Token-saving local page filter
        filtered_text, kept_pages, total_pages = filter_pdf_pages(pdf_path)
        logger.info(
            f"PyMuPDF Filter: Kept {kept_pages}/{total_pages} pages matching trigger keywords."
        )

        if kept_pages == 0 or not filtered_text.strip():
            logger.info(f"No troubleshooting pages detected in {pdf_path.name}. Skipping API call.")
            processed_hashes[file_md5] = {
                "filename": pdf_path.name,
                "status": "skipped_no_relevant_pages",
                "total_pages": total_pages,
                "matched_pages": 0,
                "codes_found": 0,
                "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            save_processed_hashes(processed_hashes)
            continue

        # Step 3.2: Gemini 2.5 Flash Structured Output Extraction
        try:
            logger.info(f"Sending {len(filtered_text.split())} words to Gemini 2.5 Flash...")
            result = call_gemini_extractor(client, filtered_text)
            extracted_items = result.items
            logger.info(f"Extracted {len(extracted_items)} error code entries from {pdf_path.name}")

            new_items_added = 0
            for raw_item in extracted_items:
                enriched = enrich_item(
                    raw_item,
                    amazon_tag,
                    existing_slugs,
                    pdf_path.name,
                    file_md5,
                )
                slug = enriched["slug"]

                matched = False
                for i, existing in enumerate(errors_db):
                    if existing.get("slug") == slug:
                        errors_db[i] = enriched
                        matched = True
                        break
                if not matched:
                    errors_db.append(enriched)
                    new_items_added += 1

            total_new_errors += new_items_added

            # Mark file hash as successfully processed
            processed_hashes[file_md5] = {
                "filename": pdf_path.name,
                "status": "success",
                "total_pages": total_pages,
                "matched_pages": kept_pages,
                "codes_found": len(extracted_items),
                "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

            # Persist updates to disk after each PDF and sync to Astro site
            save_errors_db(errors_db)
            save_processed_hashes(processed_hashes)
            logger.info(f"Successfully saved {new_items_added} new error codes to {ERRORS_DB_FILE.name}")

        except Exception as e:
            logger.error(f"Gemini extraction failed for {pdf_path.name}: {e}")
            # Do NOT mark as processed so it can be retried on next run

    logger.info(
        f"\nExtraction Completed. Added {total_new_errors} new error codes. "
        f"Total database count: {len(errors_db)} entries."
    )


def main():
    parser = argparse.ArgumentParser(description="FixMyCode Smart PDF Extractor")
    parser.add_argument(
        "--file",
        type=str,
        help="Optional specific PDF filename substring to process",
    )
    parser.add_argument(
        "--seed-demo",
        action="store_true",
        help="Generate 10 realistic sample error codes across target categories for testing the frontend",
    )
    args = parser.parse_args()

    _, amazon_tag = load_environment()

    if args.seed_demo:
        seed_demo_data(amazon_tag)
    else:
        run_extractor(pdf_file_filter=args.file)


if __name__ == "__main__":
    main()
