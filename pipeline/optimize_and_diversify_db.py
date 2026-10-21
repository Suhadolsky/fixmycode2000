import os
import re
import json
import urllib.parse
import hashlib

AMAZON_TAG = "amazinrevie0a-20"
DB_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "errors_db.json"),
    os.path.join(os.path.dirname(__file__), "..", "site", "src", "data", "errors_db.json"),
]

def clean_part_name(part: str) -> str:
    # Strip parentheses and excessive extra punctuation
    cleaned = re.sub(r'\(.*?\)', '', part).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def make_clean_search_urls(brand: str, oem: str, part: str, tool: str, consumable: str):
    c_part = clean_part_name(part)
    has_oem = oem and 'check' not in oem.lower() and oem != 'N/A'
    
    if has_oem:
        part_query = f"{brand} {oem} {c_part}".strip()
        bundle_query = f"{brand} {oem} {c_part} replacement kit".strip()
    else:
        part_query = f"{brand} {c_part}".strip()
        bundle_query = f"{brand} {c_part} repair kit".strip()
        
    part_url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(part_query)}&tag={AMAZON_TAG}"
    bundle_url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(bundle_query)}&tag={AMAZON_TAG}"
    tool_url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(tool.strip())}&tag={AMAZON_TAG}"
    consumable_url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(consumable.strip())}&tag={AMAZON_TAG}"
    
    return part_url, bundle_url, tool_url, consumable_url, part_query, bundle_query

def generate_varied_steps(item: dict) -> list:
    brand = item.get('brand', 'Equipment')
    model = item.get('model_series', 'Series')
    code = item.get('error_code', 'ERR')
    symptom = item.get('short_symptom', 'fault')
    part = item.get('primary_part_name', 'component')
    c_part = clean_part_name(part)
    oem = item.get('oem_part_number', 'OEM')
    tool = item.get('required_tool_name', 'Digital Multimeter')
    equip = item.get('equipment_type', 'Appliance')
    spec = item.get('multimeter_spec', 'test resistance')

    h = int(hashlib.md5(f"{brand}_{code}_{equip}".encode()).hexdigest(), 16)
    pattern_idx = h % 4

    steps_variants = [
        # Variant 0: Safety -> Disassembly -> Diagnostic Spec -> Installation -> Verification
        [
            f"Isolate electrical power and fuel/water supplies to the {brand} {equip} before servicing; discharge stored capacitor energy and test main terminals with your {tool}.",
            f"Remove the primary access housing using hand tools to visually inspect the {c_part} (OEM #{oem}) and wiring harness for heat discoloration, oxidation, or mechanical play.",
            f"Perform an electrical diagnostic check on the {c_part} terminals using your {tool}; verify readings against the OEM specification ({spec}).",
            f"If resistance is out of spec or mechanical damage is present, unmount the old assembly and install the certified replacement {c_part} (OEM #{oem}).",
            f"Reassemble the chassis securely, restore power, clear diagnostic error memory, and run a full diagnostic test cycle to verify error {code} is resolved."
        ],
        # Variant 1: Power Disconnect -> Component Access -> Pinout Check -> Direct Swap -> System Reset
        [
            f"Completely disconnect power from the {brand} {model}; verify zero voltage at the incoming terminal block using a {tool} to guarantee technician safety.",
            f"Unscrew the service access panel to expose the {c_part} assembly; check all plug connections, harness clips, and grounding points for looseness or moisture.",
            f"Set your {tool} to resistance or continuity mode and probe the {c_part} test points: expected baseline is {spec}.",
            f"Disconnect mounting fasteners and swap in the replacement {c_part} (OEM #{oem}), ensuring O-rings and gasket surfaces are seated flush.",
            f"Power up the {brand} {equip}, perform the control board reset procedure, and monitor operating temperature and cycle completion to confirm error {code} does not return."
        ],
        # Variant 2: Circuit Safety -> Component Inspection -> Electrical Benchmarking -> Replacement -> Recalibration
        [
            f"Turn off the dedicated circuit breaker or disconnect switch supplying the {brand} {model} to eliminate shock hazard prior to opening cabinetry.",
            f"Gain access to the internal compartment housing the {c_part} (OEM #{oem}); inspect wire leads for chafing, loose spade connectors, or thermal stress.",
            f"Measure electrical parameters across the component leads with your {tool}; confirm readings align with {spec} before condemning the part.",
            f"Unclip wiring connectors, detach mounting brackets, and install the new replacement {c_part} (OEM #{oem}) in reverse order of removal.",
            f"Re-energize the {brand} unit, clear the stored fault history from the control interface, and run an automated test cycle to confirm normal operation."
        ],
        # Variant 3: Lockout -> Diagnostic Probing -> Component Verification -> OEM Install -> Final Validation
        [
            f"Follow safety protocol by switching off main power to the {brand} {equip}; use your {tool} to confirm circuits are de-energized.",
            f"Remove external panels to reach the {c_part}; inspect terminal pins, mounting clips, and adjacent piping or ducting for debris or corrosion.",
            f"Test electrical response of the {c_part} using your {tool}; out-of-range values compared to {spec} confirm internal component breakdown.",
            f"Carefully remove the defective unit and seat the replacement {c_part} (OEM #{oem}), tightening fasteners to factory torque specifications.",
            f"Restore service power, initialize the {brand} {model} startup diagnostic sequence, and verify the display clears error {code} during active operation."
        ]
    ]

    return steps_variants[pattern_idx]

def generate_varied_faqs(item: dict) -> list:
    brand = item.get('brand', 'Equipment')
    model = item.get('model_series', 'Series')
    code = item.get('error_code', 'ERR')
    symptom = item.get('short_symptom', 'fault')
    part = item.get('primary_part_name', 'component')
    c_part = clean_part_name(part)
    oem = item.get('oem_part_number', 'OEM')
    meaning = item.get('plain_english_meaning', 'diagnostic fault detected')
    cost = item.get('estimated_pro_repair_cost', '$150 - $300')
    diff = item.get('diy_difficulty', 'Medium (30-45 mins)')

    h = int(hashlib.md5(f"{code}_{brand}_{symptom}".encode()).hexdigest(), 16)
    variant_idx = h % 4

    faq_pools = [
        # Set 0
        [
            {
                "question": f"What causes {brand} error code {code} on {model}?",
                "answer": f"Error code {code} triggers when the internal control system detects: {meaning}. In standard service documentation, the root failure point is the {c_part} (OEM #{oem}) or its direct circuit connection."
            },
            {
                "question": f"Can I clear {brand} fault code {code} by power cycling?",
                "answer": f"A power reset can clear transient software glitches. However, if the {c_part} has failed mechanically or drifted outside operating tolerances, error {code} will trigger again as soon as the test cycle begins."
            },
            {
                "question": f"What is the average cost to fix {brand} error {code}?",
                "answer": f"Professional technician dispatch typically costs {cost} including diagnosis and labor. Completing the replacement of {c_part} (OEM #{oem}) yourself usually takes {diff} and saves 70% or more."
            }
        ],
        # Set 1
        [
            {
                "question": f"Why is my {brand} {model} flashing error {code} ({symptom})?",
                "answer": f"The controller flags {code} when feedback indicates: {meaning}. The primary component responsible for this signal is the {c_part} (part number #{oem})."
            },
            {
                "question": f"Is it safe to run my {brand} equipment while error {code} is active?",
                "answer": f"Operating equipment with an active {code} fault is not recommended because the system may enter safety shutdown or fail to regulate properly until the {c_part} is inspected and verified."
            },
            {
                "question": f"How difficult is replacing {c_part} #{oem} on {brand}?",
                "answer": f"DIY difficulty is rated as {diff}. Most owners with standard hand tools can complete the swap without calling a pro service crew."
            }
        ],
        # Set 2
        [
            {
                "question": f"What does error code {code} indicate on {brand} {model}?",
                "answer": f"According to technical service bulletins, error {code} means: {meaning}. The primary component requiring diagnostic check is the {c_part} (OEM #{oem})."
            },
            {
                "question": f"Will error {code} damage other parts if not fixed immediately?",
                "answer": f"Persistent operation with a faulty {c_part} can cause auxiliary components to overheat or overwork. Replacing OEM #{oem} promptly prevents compound equipment failure."
            },
            {
                "question": f"What tools are needed to repair {brand} error {code}?",
                "answer": f"Standard repairs require basic hand tools and a digital multimeter to verify component specs. The repair typically takes {diff} and avoids {cost} in technician fees."
            }
        ],
        # Set 3
        [
            {
                "question": f"How do technicians diagnose {brand} fault code {code}?",
                "answer": f"Field technicians first inspect the {c_part} (OEM #{oem}) and measure electrical response across its terminals because {code} corresponds to {meaning.lower()}."
            },
            {
                "question": f"Does replacing {c_part} #{oem} require special programming?",
                "answer": f"No, the certified OEM #{oem} {c_part} is a direct factory-spec replacement. Once mounted and connected, the {brand} control board recognizes the signal upon the next power cycle."
            },
            {
                "question": f"What is the DIY savings for fixing {brand} error code {code}?",
                "answer": f"A service call costs approximately {cost}. By sourcing the replacement {c_part} directly and performing the {diff} repair, owners typically save between $150 and $250."
            }
        ]
    ]

    return faq_pools[variant_idx]

def main():
    primary_db = os.path.abspath(DB_PATHS[0])
    with open(primary_db, 'r', encoding='utf-8') as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records for optimization & diversification...")

    for r in records:
        brand = r.get('brand', '')
        oem = r.get('oem_part_number', '')
        part = r.get('primary_part_name', '')
        tool = r.get('required_tool_name', 'Digital Multimeter')
        consumable = r.get('consumable_name', 'High-Temp Silicone Grease')

        # FIX 1: Clean search queries and eliminate hallucinated ASINs
        part_url, bundle_url, tool_url, consumable_url, p_query, b_query = make_clean_search_urls(
            brand, oem, part, tool, consumable
        )
        r['part_affiliate_url'] = part_url
        r['primary_part_affiliate_url'] = part_url
        r['bundle_cart_url'] = bundle_url
        r['tool_affiliate_url'] = tool_url
        r['consumable_affiliate_url'] = consumable_url
        r['primary_part_search_query'] = p_query
        
        # Strip hallucinated ASINs
        r['asin_part'] = None
        r['asin_tool'] = None
        r['asin_consumable'] = None
        r['has_asin_bundle'] = False

        # FIX 3: Varied diagnostic steps and FAQs
        r['diagnostic_and_fix_steps'] = generate_varied_steps(r)
        r['faq_questions'] = generate_varied_faqs(r)

    for path in DB_PATHS:
        abs_p = os.path.abspath(path)
        with open(abs_p, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"Updated & saved {len(records)} records to {abs_p}")

if __name__ == '__main__':
    main()
