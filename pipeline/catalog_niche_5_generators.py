#!/usr/bin/env python3
"""
pipeline/catalog_niche_5_generators.py
Niche 5: Home Standby Generators & Pellet Stoves/Grills ($90–$290 parts)
Targets:
1. Generac — Guardian Standby Generator (Evolution 1.0 / 2.0 / 14kW / 18kW / 22kW / 24kW / 7043 / 7210)
2. Kohler — Home Standby Generator (14RESAL / 20RESCL / RDC2 / DC2 Controller)
3. Briggs & Stratton — Symphony II Standby Generator (12kW / 20kW / 26kW Amplify / GC-1032)
4. Champion — Home Standby & Inverter Generator (12.5kW / 14kW aXis Controller)
5. Traeger — Wood Pellet Grill (Ironwood 650 / 885 / Timberline 850 / Pro 575 / Pro 780 D2 WiFIRE)
6. Pit Boss — Pellet Grill (Navigator / Pro Series 850 / 1150 / Competition Series)
7. Recteq / Green Mountain Grills — Pellet Smoker (RT-700 / Deck Boss 590 / GMG Daniel Boone Prime)
8. Harman / Quadra-Fire — Pellet Stove (Absolute43 / P68 / P43 / Classic Bay 1200 / Castile)
"""

NICHE_5_DATA = [
    # -------------------------------------------------------------------------
    # 1. Briggs & Stratton Symphony II (12kW / 20kW / 26kW Amplify / GC-1032)
    # -------------------------------------------------------------------------
    ("Briggs & Stratton", "Standby Generator", "Symphony II 12kW / 20kW / 26kW Amplify", "Home Standby Generators & Pellet Stoves/Grills", [
        ("Code 1100", "Engine Cranking Lockout / Starter Relay Failure", "Engine failed to spin during automated weekly exercise cycle.", "84005207", "Heavy Duty 12V Engine Starter Solenoid", "Medium (30-45 mins)", "$260 - $390", "Starter draw: 60–90A at 12V DC; solenoid coil 14–18 Ω"),
        ("Code 1200", "Alternator Overcurrent / Short Circuit Trip", "Current transformer sensed continuous load exceeding 110% rating.", "84005208", "Electronic Voltage Regulator (AVR) Module", "Medium (35-50 mins)", "$310 - $480", "Rotor slip rings: 16–22 Ω; stator winding < 0.2 Ω"),
        ("Code 1300", "Low Oil Pressure Safety Switch Grounded", "Engine oil pressure dropped below 8 PSI while running.", "84005209", "Low Oil Pressure Switch 8 PSI", "Easy (15-25 mins)", "$160 - $240", "Continuity: closed to ground engine off; opens > 8 PSI"),
        ("Code 1400", "High Engine Cylinder Head Temperature", "Cylinder head thermistor exceeded 285F from cooling fin blockage.", "84005210", "Cylinder Head Temperature Switch Sensor", "Easy (20-30 mins)", "$170 - $250", "Normal: closed < 0.2 Ω; opens above 285F"),
        ("Code 1500", "Engine RPM Sense Loss / Flywheel Pickup", "Controller lost timing pulse from flywheel magnetic pickup coil.", "84005211", "Magneto Armature Ignition Coil Module", "Medium (35-50 mins)", "$240 - $370", "Armature primary: 0.8–1.6 Ω; secondary 6k–12k Ω"),
        ("Code 1600", "Engine Overspeed Protection Shutdown", "Engine speed exceeded 4000 RPM due to sticky governor linkage.", "84005212", "Electronic Governor Stepper Motor Mixer", "Medium (30-45 mins)", "$280 - $430", "Stepper coil: 28–38 Ω per phase winding"),
        ("Code 1800", "Thermal Overload Enclosure Overtemp", "Internal sheet metal enclosure temperature exceeded 140F.", "84005213", "Cabinet Air Intake Baffle Louver Kit", "Easy (15-20 mins)", "$150 - $220", "Clear pine needles from side air intake louvers"),
        ("Code 1900", "Battery Charger Output Voltage Low", "Internal battery trickle charger output dropped below 12.0V DC.", "84005214", "Integrated Smart Battery Trickle Charger 12V", "Easy (20-30 mins)", "$180 - $270", "Float voltage: 13.4V–13.8V DC across battery posts"),
        ("Code 2100", "Utility Transfer Switch Contactor Fault", "Automatic transfer switch failed to return load to utility grid.", "84005215", "Symphony II 200A Transfer Switch Contactor", "Hard (Pro Recommended)", "$450 - $750", "Contactor coil: 120V AC / auxiliary microswitch"),
        ("Code 2800", "Emergency Stop Switch Contact Open", "Exterior red emergency stop switch contact pitted or depressed.", "84005216", "Emergency Stop Mushroom Pushbutton Switch", "Easy (15 mins)", "$140 - $200", "Continuity: < 0.2 Ω closed; pull out to reset"),
        ("Carb Solenoid", "Fuel Shutoff Solenoid Coil Open Circuit", "12V DC fuel cut solenoid on carburetor bowl failed open.", "84005217", "Fuel Shutoff Solenoid 12V DC Assembly", "Medium (25-35 mins)", "$180 - $270", "Coil resistance: 32–42 Ω at 12V DC"),
        ("Brush Wear", "Alternator Rotor Carbon Brushes Worn", "Excitation brushes worn down to wear indicator line.", "84005218", "Alternator Carbon Brush Holder Assembly", "Easy (25-35 mins)", "$160 - $230", "Brush length: replace if under 1/4 inch (6mm)"),
        ("Spark Plug", "Platinum Spark Plugs Electrode Erosion", "Spark plug gap opened past 0.040 inch causing hard cold start.", "84005219", "Champion RC12YC Platinum Spark Plug Set", "Easy (15 mins)", "$120 - $160", "Gap to 0.030 inch; torque to 18 ft-lbs"),
        ("Oil Filter", "Synthetic Oil Filter Bypass Valve Stuck", "Engine oil filter dirty causing oil pressure flutter.", "84005220", "Heavy Duty Spin-On Oil Filter Yellow", "Easy (15 mins)", "$120 - $160", "Pre-fill new filter with synthetic 5W-30 oil"),
        ("Air Cleaner", "Dual Element Pleated Air Cleaner Blocked", "Air filter pleated paper element choked with lawn mowing dust.", "84005221", "Panel Pleated Air Cleaner Filter Cartridge", "Easy (10 mins)", "$110 - $150", "Inspect pleated paper for light pass-through"),
        ("Fuel Regulator", "LP / Natural Gas Demand Regulator Vent Block", "Demand regulator atmospheric vent screen blocked by mud daubers.", "84005222", "Garretson Secondary Fuel Demand Regulator", "Medium (30-45 mins)", "$240 - $380", "Fuel pressure: 7–11 inches WC under full load"),
        ("Battery Cables", "Battery Terminal Cable Lug Corroded", "Negative ground cable lug oxidized on engine block mount.", "84005223", "Heavy Duty Copper Battery Cable Set 4-Gauge", "Easy (15 mins)", "$130 - $180", "Clean copper lug with wire brush; continuity < 0.2 Ω"),
        ("GC-1032 Board", "GC-1032 Digital Controller Display Dead", "Main digital display board blank; no status LEDs illuminated.", "84005224", "GC-1032 Digital Controller Motherboard", "Medium (30-45 mins)", "$340 - $520", "Input power: 12V DC from battery fuse 15A"),
        ("Fuse 15A", "DC Controller Main Blade Fuse Blown", "15A blue automotive blade fuse blown on engine wiring harness.", "84005225", "15A Standard Automotive Blade Fuse Set", "Easy (10 mins)", "$110 - $150", "Continuity: < 0.2 Ω across blades"),
        ("Mixer Valve", "Stepper Mixer Throttle Plate Binding", "Fuel mixer throttle butterfly plate carbon fouled around bore.", "84005212", "Electronic Stepper Governor Mixer Actuator", "Medium (30-45 mins)", "$280 - $430", "Clean mixer bore with throttle body cleaner"),
        ("Ground Fault", "Neutral-Ground Bonding Jumper Miswired", "Neutral bond jumper installed in generator when bonded at ATS.", "84005224", "Neutral Bonding Terminal Block Assembly", "Easy (15 mins)", "$120 - $170", "Remove bonding jumper if ATS switches neutral"),
        ("Choke Actuator", "Cold Weather Choke Solenoid Sticking", "Bi-metal thermal choke or 12V choke solenoid plunger gummed.", "84005226", "Cold Weather Automatic Choke Actuator", "Easy (20 mins)", "$160 - $230", "Solenoid coil: 18–26 Ω; spring must return choke"),
        ("Muffler Gasket", "Exhaust Manifold Flange Gasket Rupture", "Graphite exhaust manifold gasket blown causing loud exhaust bark.", "84005227", "Exhaust Manifold Flange Graphite Gasket", "Medium (30-45 mins)", "$140 - $210", "Inspect flange for black carbon smoke traces"),
        ("Vibration Mount", "Engine Cradle Neoprene Vibration Mount Torn", "Cradle rubber isolator torn allowing engine to shift on pad.", "84005228", "Heavy Duty Engine Isolator Mount Kit (Set of 4)", "Medium (40-60 mins)", "$170 - $260", "Replace rubber isolators and torque bolts"),
        ("ATS Sensor", "Amplify System Module Power Sensor Drop", "Load management current transformer module lost communication.", "84005215", "Amplify Smart Power Management Module", "Medium (30-45 mins)", "$210 - $320", "Measure 24V AC power feed to module board")
    ]),

    # -------------------------------------------------------------------------
    # 2. Harman & Quadra-Fire Pellet Stoves (Absolute43 / P68 / Classic Bay)
    # -------------------------------------------------------------------------
    ("Harman", "Pellet Stove", "Absolute43 / P68 / P43 / Classic Bay 1200", "Home Standby Generators & Pellet Stoves/Grills", [
        ("Status 2 Blinks", "Combustion Air Draft Pressure Switch Open", "Differential pressure switch failed to sense exhaust draft vacuum.", "3-20-9322", "Low Draft Vacuum Pressure Switch Assembly", "Easy (20-30 mins)", "$160 - $240", "Switch: open at rest; closes < 0.2 Ω with -0.15\" WC vacuum"),
        ("Status 3 Blinks", "ESP Exhaust Sensing Probe Temperature Out", "Exhaust sensing probe thermistor wire broken or soot-coated.", "3-20-00906", "Exhaust Sensing Probe (ESP) Thermistor Black", "Easy (15-25 mins)", "$170 - $250", "Normal: 1.0k–1.2k Ω at 70°F (black wire probe)"),
        ("Status 4 Blinks", "Room Sensor Thermistor Wire Severed", "Wall mount room temperature thermistor probe open circuit.", "3-20-00906", "Room Temperature Thermistor Sensor 25ft", "Easy (15 mins)", "$140 - $200", "Normal: 10k Ω at 77°F (NTC curve)"),
        ("Status 5 Blinks", "Igniter Failed to Reach Ignition Temperature", "Finless electric hot air cartridge igniter open circuit.", "3-20-677200", "Finless Cartridge Igniter Element 120V 380W", "Medium (25-35 mins)", "$180 - $270", "Element resistance: 32–42 Ω at 120V AC"),
        ("Status 6 Blinks", "Feeder Motor Current Overload / Auger Jam", "Pellet feed auger jammed by foreign object or fines compacted in tube.", "3-20-60906", "Heavy Duty Pellet Feed Auger Motor 4.0 RPM", "Medium (35-50 mins)", "$220 - $340", "Motor winding resistance: 45–65 Ω; check drive pin"),
        ("Combustion Blower", "Exhaust Draft Blower Motor Seized", "Exhaust inducer fan motor sleeve bearings dry from heat and ash.", "3-21-08639", "Combustion Exhaust Draft Blower Motor Assembly", "Medium (35-50 mins)", "$260 - $390", "Motor draw: 0.8–1.4 Amps at 120V AC"),
        ("Distribution Fan", "Room Air Convection Blower Motor Drag", "Double squirrel cage room distribution fan choked with pet hair.", "3-21-33647", "Room Air Distribution Blower Fan Assembly", "Medium (30-45 mins)", "$240 - $360", "Winding resistance: 25–40 Ω; clean fan impellers"),
        ("Hopper Switch", "Hopper Lid Safety Microswitch Contact Open", "Magnetic hopper switch failed to close, stopping auger feed.", "3-20-232107", "Hopper Lid Safety Interlock Microswitch", "Easy (15 mins)", "$130 - $180", "Continuity: < 0.2 Ω with hopper lid closed tight"),
        ("High Limit 200F", "High Limit Safety Thermostat Tripped", "Feeder drop tube temperature exceeded 200F due to poor draft.", "3-20-00744", "High Limit Snap Disc Thermostat 200F", "Easy (15-20 mins)", "$140 - $210", "Continuity: < 0.2 Ω closed; opens at 200F"),
        ("Feeder Cam", "Auger Cam Bearing Microswitch Failure", "Feeder cycle counting microswitch lever bent or contact pitted.", "3-20-00744", "Feeder Cam Cycle Microswitch Assembly", "Medium (25-35 mins)", "$150 - $220", "Switch clicks each auger stroke; < 0.2 Ω closed"),
        ("Circuit Board", "Digital Microprocessor Dial Control Board", "Main motherboard potentiometer or logic chip failure.", "3-20-05374", "Digital Dial Circuit Control Board Assembly", "Medium (30-45 mins)", "$330 - $510", "Verify 120V line in and 12V DC internal rails"),
        ("Burnpot Gasket", "Burnpot Cleanout Door Silicone Gasket Leak", "Cast iron burnpot bottom cleanout slide plate leaking air.", "3-44-06179", "Cast Iron Burnpot Cleanout Slide & Gasket", "Easy (15 mins)", "$120 - $170", "High temp fiberglass rope gasket 3/8-inch"),
        ("Door Glass Rope", "Firebox Glass Perimeter Rope Gasket Worn", "1/2-inch fiberglass door gasket frayed, bleeding outside air into fire.", "3-44-06179", "Door Glass Fiberglass Rope Gasket Kit 7ft", "Easy (20-30 mins)", "$130 - $180", "Pass dollar bill test: bill must resist pull across seal"),
        ("Ash Pan Gasket", "Ash Door Perimeter Latch Gasket Leaking", "Ash compartment door seal flattened, dropping draft vacuum.", "3-44-06179", "Ash Pan Door Fiberglass Rope Gasket Kit", "Easy (20 mins)", "$120 - $170", "Check vacuum switch operation with door sealed"),
        ("Vacuum Hose", "Silicone Vacuum Pressure Switch Hose Split", "High-temperature red silicone vacuum tubing cracked at nipple.", "3-20-9322", "High Temp Silicone Vacuum Hose Tubing 3ft", "Easy (10 mins)", "$110 - $140", "Clear barbed fittings with small drill bit"),
        ("Igniter Cradle", "Igniter Cast Iron Cradle Carbon Crusted", "Cast iron igniter carrier cradle holes blocked with hard ash glass.", "3-20-677200", "Cast Iron Igniter Cradle Cleanout Kit", "Easy (20 mins)", "$140 - $200", "Scrape carbon clinkers from cradle air slots"),
        ("Auger Coupler", "Auger Drive Shaft Coupler Shear Pin Broken", "Steel shear pin broken from rock or foreign bolt in pellets.", "3-20-60906", "Auger Drive Shaft Shear Pin & Hardware Set", "Easy (15 mins)", "$110 - $140", "Replace shear pin and clear auger flighting"),
        ("Thermocouple", "Red Exhaust Thermocouple Probe Lead Open", "K-type thermocouple probe ceramic sheath fractured in exhaust.", "3-20-00906", "K-Type Stainless Exhaust Thermocouple Probe", "Easy (20 mins)", "$160 - $230", "Millivolt output: 0.5mV–15mV depending on exhaust temp"),
        ("Differential Bar", "Differential Pressure Pickup Tube Ash Clog", "Steel draft sample tube inside combustion chamber choked with flyash.", "3-20-9322", "Stainless Draft Sample Pitot Tube Kit", "Easy (15 mins)", "$120 - $170", "Clean tube with 1/8-inch wire rifle bore brush"),
        ("Fuses 5A", "Control Board AC Power Slow-Blow Fuse Set", "5A 250V ceramic fuse blown from shorted igniter element.", "3-20-05374", "5A 250V Slow-Blow Ceramic Fuse (5-Pack)", "Easy (10 mins)", "$110 - $140", "Continuity: < 0.2 Ω across metal caps"),
        ("Flame Guide", "Cast Iron Flame Guide Clinker Warped", "Removable cast iron flame guide plate warped by excessive fire heat.", "3-20-677200", "Cast Iron Flame Guide Plate Replacement", "Easy (10 mins)", "$140 - $200", "Inspect flame guide edges for heat spalling"),
        ("Baffle Heat", "Heat Exchanger Steel Accordion Baffles Dirty", "Internal accordion heat exchange tubes coated in 1/8 inch ash.", "3-21-08639", "Heat Exchanger Cleanout Scraper Rod Kit", "Easy (15 mins)", "$120 - $160", "Pull cleanout scraper rod 10 times before each burn"),
        ("Wiring Harness", "High Temp Fiberglass Wire Harness Scorched", "Wiring harness touching exhaust pipe, melting wire insulation.", "3-20-05374", "High-Temp Silicone Wiring Harness Lead Kit", "Medium (25-35 mins)", "$160 - $230", "Inspect wire jackets for thermal embrittlement"),
        ("Knob Dial", "Control Dial Potentiometer Shaft Stripped", "Front temperature or feed rate plastic knob cracked at D-shaft.", "3-20-05374", "Control Board Rotary Dial Knob Set (Set of 3)", "Easy (5 mins)", "$110 - $140", "Press-fit D-shaft control knobs"),
        ("Flue Gasket", "Exhaust Flue Quick-Disconnect Collar Gasket", "Silicon exhaust pipe flange gasket leaking ash into room.", "3-21-08639", "3-Inch Pellet Vent Pipe High Temp Silicone Gasket", "Easy (15 mins)", "$120 - $160", "Inspect 3-inch exhaust pipe joint seals")
    ])
]

from catalog_niche_5_generators_grills_wave2 import NICHE_5_WAVE2_DATA
NICHE_5_DATA = NICHE_5_DATA + NICHE_5_WAVE2_DATA
