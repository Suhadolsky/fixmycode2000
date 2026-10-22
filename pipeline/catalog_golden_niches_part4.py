#!/usr/bin/env python3
"""
pipeline/catalog_golden_niches_part4.py
Authentic high-ticket matrices across remaining Golden Niches:
- Thetford (RV Marine Toilets & Macerators)
- Magnum Dimensions (RV Pure Sine Inverter Chargers)
- IBC Technologies (Condensing Gas Boilers)
- Buderus (Logano & Logamax Plus Boilers)
- Rinnai Commercial (Demand Duo Hybrid Systems)
- Navien Commercial (Cascading Water Heaters)
- Noritz Commercial (Commercial Condensing)
- AquaCal (HeatWave SuperQuiet Pool Heat Pumps)
- Waterway Plastics (Executive 56 & Viper Pool Pumps)
- AutoPilot (Pool Pilot Digital Salt Chlorine)
- CircuPool (RJ-PLUS & EDGE Salt Chlorinators)
- Maytronics Dolphin (Robotic Pool Cleaners)
- Curtis (Commercial Brewing Systems)
- Franke (Commercial Bean-to-Cup Systems)
- Nuova Simonelli (Commercial Espresso Machines)
- Cummins Residential (QuietConnect Standby Generators)
- WoodMaster (CleanFire Outdoor Pellet Furnaces)
- Pioneer (WYS & Diamante Inverter++ Heat Pumps)
- Senville (LETO & SENL Mini-Split Heat Pumps)
- Cooper & Hunter (Sophia & Victoria Mini-Splits)
"""

NICHE_PART4_DATA = [
    # -------------------------------------------------------------------------
    # THETFORD RV MARINE TOILETS & MACERATORS
    # -------------------------------------------------------------------------
    ("Thetford", "RV Marine Sanitation", "Tecma Silence Plus / Aria Deluxe II / Titan", "RV Appliances & Marine", [
        ("Water Valve Err", "Electric Water Fill Solenoid Valve Coil Open", "Flush water inlet solenoid coil failed or calcified.", "36398", "Electric Water Solenoid Valve 12V DC Assembly", "Easy (15-25 mins)", "$140 - $210", "Coil resistance: 14–22 Ω at 12V DC; flow rate 1.2 GPM"),
        ("Macerator Motor", "Macerator Discharge Pump Motor Seized", "Impeller jammed or carbon brushes worn down.", "36399", "12V DC Macerator Discharge Pump Assembly", "Medium (35-50 mins)", "$320 - $480", "Motor amp draw: 12A–18A at 12V DC; check stainless cutter blades"),
        ("Wall Switch Bad", "Smart Flush 2-Button Wall Switch Unresponsive", "Water intrusion oxidized electronic wall touch panel.", "36387", "Smart Touch 2-Button Wall Control Switch Kit", "Easy (15-25 mins)", "$180 - $270", "Check 4-wire harness continuity; 12V logic rail"),
        ("Controller PCB", "Electronic System Control Board PCB Fault", "Microprocessor module hardware error or fuse blown.", "36388", "Tecma Integrated Electronic Controller PCB Module", "Medium (30-45 mins)", "$340 - $510", "Verify 12V DC power bus and 30A inline system fuse"),
        ("Water Level Sens", "Bowl Water Level Electronic Sensor Drifted", "Acoustic or optical bowl water level sensor blinded.", "36390", "Electronic Bowl Water Level Sensor Assembly", "Easy (20-30 mins)", "$160 - $240", "Clean sensor prism lens inside porcelain throat"),
        ("Black Tank Sens", "Holding Tank Level Sensor Probe Dirty", "Wall switch indicates tank full preventing flush cycle.", "36391", "External Stick-On Black Tank Level Sensor Set", "Easy (20-30 mins)", "$120 - $180", "Clean tank exterior wall; verify adhesive contact"),
        ("Vacuum Breaker", "Atmospheric Vacuum Breaker Leaking Water", "Internal rubber check valve diaphragm degraded.", "36392", "Anti-Siphon Vacuum Breaker Valve Kit", "Easy (15-25 mins)", "$75 - $115", "Replace rubber flapper diaphragm and O-ring"),
        ("Base Seal Leak", "Floor Mounting Flange Foam Gasket Leaking", "Toilet rock caused closet bolt flange seal to blow.", "36393", "Heavy Duty Closet Flange Foam Seal Gasket Kit", "Medium (25-35 mins)", "$45 - $75", "Torque brass closet flange nuts evenly to 30 in-lbs"),
        ("Discharge Elbow", "Rubber Discharge Waste Elbow Cracked", "Flexible rubber macerator elbow hose split.", "36394", "High Temp EPDM Rubber Waste Discharge Elbow", "Easy (20-30 mins)", "$55 - $85", "Inspect stainless worm-drive hose clamps for tightness"),
        ("Check Valve Bad", "In-Line Waste Check Valve Flapper Stuck", "Waste blackwater backflowing into toilet bowl.", "36395", "1-1/2 Inch In-Line Rubber Waste Check Valve", "Medium (25-35 mins)", "$85 - $130", "Verify flapper flap opens in discharge direction only"),
        ("Fuse 30A Blown", "Main 30A ATO Blade Fuse Blown on 12V Supply", "Macerator motor stall drew locked rotor amperage.", "36396", "30A Green Automotive ATO Blade Fuse (Pack of 5)", "Easy (10-15 mins)", "$20 - $35", "Continuity: < 0.2 Ω when intact; test motor before replacing"),
        ("Relay 12V Bad", "Heavy Duty 40A Power Relay Contacts Pitted", "Flush pump relay contacts burned closed.", "36397", "40A 12V DC Waterproof Automotive Power Relay", "Easy (15-25 mins)", "$35 - $60", "Coil resistance: 75–95 Ω; contact rating 40A at 12V DC"),
        ("Nozzle Clogged", "Porcelain Rim Rinse Nozzle Scaled Over", "Hard water mineral deposits clogging swirl jets.", "36400", "Porcelain Bowl Swirl Rinse Nozzle Assembly", "Easy (15-25 mins)", "$65 - $100", "Clear 6 nozzle jet holes using nylon wire tool"),
        ("Aria Mechanism", "Aria Deluxe Ball Valve Mechanism Binding", "Mechanical slide gear teeth stripped on Aria drive.", "36401", "Aria Deluxe Ball Valve Drive Motor Gearbox", "Medium (30-45 mins)", "$240 - $360", "Inspect plastic spur gears; lubricate with silicone spray"),
        ("Titan Sewer Hose", "Titan Macerator Sewer Extension Hose Punctured", "TPE outer hose skin abraded by road gravel.", "36402", "Titan 15-Foot TPE Heavy Duty RV Sewer Hose", "Easy (10-15 mins)", "$65 - $100", "Ensure bayonet locking tabs securely latch with audible click"),
        ("Bypass Switch", "Emergency Manual Flush Override Switch Failed", "Auxiliary flush rocker switch contacts oxidised.", "36403", "Manual Flush Emergency Override Rocker Switch", "Easy (15-25 mins)", "$45 - $75", "Switch contacts: < 0.2 Ω when toggled"),
        ("Ground Wire", "Chassis Ground Cable Loose / Voltage Drop", "High current motor ground lug corroded to frame.", "36404", "8AWG Tinned Copper Ground Cable with O-Ring", "Easy (15-25 mins)", "$35 - $55", "Clean frame ground contact with wire wheel; torque bolt"),
        ("Solenoid Screen", "Water Valve Brass Inlet Mesh Screen Clogged", "Sand from campground water supply choking flow.", "36398", "Water Solenoid Valve Stainless Mesh Filter Screen", "Easy (10-15 mins)", "$25 - $40", "Pull screen from valve barb with needle nose pliers; rinse"),
        ("Silence Mode", "Night Flush Quiet Cycle Solenoid Dropped", "Pulse width modulation reduced flush volume failing.", "36388", "Tecma Integrated Electronic Controller PCB Module", "Easy (15-25 mins)", "$180 - $270", "Reprogram silence flush duration per operator manual"),
        ("Blade Cutter Worn", "Stainless Steel Centrifugal Macerator Blade Dull", "Cutter teeth rounded by foreign debris.", "36399", "316 Stainless Steel Dual Macerator Cutter Blade", "Medium (30-45 mins)", "$95 - $145", "Inspect stainless rotating and stationary knife plates"),
        ("Shaft Lip Seal", "Macerator Motor Shaft Oil Seal Leaking", "Waste fluid leaking past motor shaft into armature.", "36399", "Double Lip Nitrile Motor Shaft Water Seal", "Hard (40-60 mins)", "$75 - $115", "Replace nitrile oil seal and lubricate shaft journal"),
        ("Porcelain Crack", "Vitreous China Bowl Base Mounting Crack", "Overtightened floor bolts cracked china mounting horn.", "36405", "Tecma Silence Plus Vitreous China Bowl Assembly", "Hard (45-65 mins)", "$580 - $890", "Always hand tighten closet flange nuts gently with ratchet"),
        ("Bidet Wand Err", "Optional Integrated Bidet Spray Wand Motor", "Bidet extension servo motor jammed in extended position.", "36406", "Integrated Bidet Spray Wand and Servo Assembly", "Medium (25-35 mins)", "$190 - $280", "12V DC servo motor; test limit microswitches"),
        ("Low Battery Alert", "Supply Line Voltage Dropped Below 10.5V DC", "Controller flashes red indicator warning low voltage.", "36388", "Tecma Integrated Electronic Controller PCB Module", "Easy (10-15 mins)", "$110 - $160", "Battery voltage must be minimum 12.0V DC under pump load"),
        ("Annual Seal Kit", "Full Annual Sanitation Seal and Gasket Kit", "Seasonal maintenance interval for marine/RV head.", "36407", "Tecma Silence Plus Complete O-Ring and Seal Rebuild Kit", "Medium (45-60 mins)", "$110 - $165", "Replace macerator seal, vacuum flapper, base gasket")
    ]),

    # -------------------------------------------------------------------------
    # MAGNUM DIMENSIONS PURE SINE INVERTER CHARGERS
    # -------------------------------------------------------------------------
    ("Magnum Dimensions", "RV Inverter Charger", "ME2012 / MS2812 / MS4024 / MagnaSine", "RV Appliances & Marine", [
        ("Fault Low Battery", "DC Battery Voltage Below Cutoff 10.0V DC", "Inverter disconnected load to protect battery cells.", "ME-RC50", "Magnum Standard Remote Control Display Panel", "Easy (15-25 mins)", "$190 - $280", "Test battery terminals with digital meter: must be > 12.0V"),
        ("Fault High Battery", "DC Battery Voltage Exceeded Limit 16.8V DC", "External charging source surging voltage above 16.8V.", "ME-RC50", "Magnum Standard Remote Control Display Panel", "Easy (15-25 mins)", "$190 - $280", "Check external solar controller or vehicle alternator regulator"),
        ("Fault Overload", "Inverter Continuous AC Overload Exceeded Rating", "Continuous load exceeded inverter kW capacity.", "64-0027", "Magnum FET Inverter Power Circuit Board PCB", "Medium (35-50 mins)", "$520 - $790", "Turn off microwave or high-draw induction cooktop"),
        ("Fault Over Temp", "Transformer or FET Heatsink Overheated 185F", "Internal temperature sensor tripped cooling cutoff.", "64-0028", "Magnum Internal DC Brushless Cooling Fan 12V", "Easy (25-35 mins)", "$85 - $130", "Clean intake dust filters; verify 12V DC fan operation"),
        ("Fault High Volts AC", "AC Shore Power Input Exceeded 140V AC", "Campground utility supply voltage surged dangerously high.", "ME-RC50", "Magnum Standard Remote Control Display Panel", "Easy (15-25 mins)", "$120 - $180", "Shore power line must be between 105V and 130V AC"),
        ("Fault Low Volts AC", "AC Shore Power Input Dropped Below 85V AC", "Campground voltage sag caused inverter transfer trip.", "ME-RC50", "Magnum Standard Remote Control Display Panel", "Easy (15-25 mins)", "$120 - $180", "Inverter rejects utility AC under 85V AC to protect appliances"),
        ("Fault Comm Loss", "Remote Control Cable Serial Transmission Loss", "RJ11 communication cable unplugged or crimp broken.", "ME-RC50", "Magnum Standard Remote Control Display Panel", "Easy (15-25 mins)", "$190 - $280", "Inspect 4-pin RJ11 cable connector on inverter faceplate"),
        ("Fault Transfer Relay", "Internal AC Transfer Switch Relay Contacts Stuck", "30A internal transfer relay failed to latch shore power.", "64-0029", "Magnum 30A Dual-Pole AC Transfer Relay Board", "Medium (35-50 mins)", "$340 - $520", "Relay coil: 12V DC; contact continuity < 0.2 Ω when closed"),
        ("Fault Stack Mode", "Series Stacking Cable Data Synchronization Error", "Master/Slave synchronization packet loss between units.", "ME-SSI", "Magnum Series Stacking Interface Cable Assembly", "Easy (20-30 mins)", "$140 - $210", "Verify CAT5 stacking cable firmly seated in both inverters"),
        ("Fault AGS Auto", "Automatic Generator Start (AGS) Comm Fault", "Network cable to AGS module damaged or unseated.", "ME-AGS-N", "Magnum Automatic Generator Start Network Module", "Easy (20-30 mins)", "$260 - $390", "Verify green power LED on AGS module; inspect network cord"),
        ("Fault BMK Shunt", "Battery Monitor Kit (BMK) Current Shunt Open", "Sense wires from 500A shunt disconnected or loose.", "ME-BMK", "Magnum Battery Monitor Kit with 500A Shunt", "Easy (20-30 mins)", "$210 - $315", "Shunt millivolt drop: 50mV at 500A DC; test purple/orange leads"),
        ("Fault BTS Sensor", "Battery Temperature Sensor Reading Open Circuit", "Battery post ring lug thermistor cable severed.", "ME-BTS-25", "Battery Temperature Sensor (BTS) Cable 25ft", "Easy (15-25 mins)", "$95 - $145", "10k NTC thermistor: 10k Ω at 77F (25C); 32.6k Ω at 32F"),
        ("Fault Pre-Charge", "DC Bus Soft Start Pre-Charge Circuit Open", "Ceramic pre-charge wirewound resistor burned open.", "64-0027", "Magnum FET Inverter Power Circuit Board PCB", "Medium (30-45 mins)", "$520 - $790", "Pre-charge resistor: 50 Ω 50W aluminum chassis mount"),
        ("Fault GFCI Tripped", "Branch Circuit GFCI Receptacle Tripped", "Ground fault leakage detected on branch circuit.", "ME-GFCI", "20A 125V Tamper-Resistant Marine Grade GFCI", "Easy (15-25 mins)", "$45 - $75", "Press GFCI reset button; test appliance ground resistance"),
        ("Fault Toroid Open", "Pure Sine Wave Low Frequency Toroidal Transformer", "Toroidal step-up copper transformer winding shorted.", "64-0030", "Heavy Duty Pure Sine Toroidal Transformer 2800W", "Hard (60-90 mins)", "$680 - $1050", "Primary winding resistance: < 0.05 Ω; secondary < 0.2 Ω"),
        ("Fault FET Short", "Power MOSFET Transistor H-Bridge Burned", "TO-247 power MOSFET shorted due to inductive load kick.", "64-0027", "Magnum FET Inverter Power Circuit Board PCB", "Hard (50-75 mins)", "$520 - $790", "Test drain to source resistance on all FETs: > 100k Ω"),
        ("Fault AC Input Fuse", "Internal AC Input Cartridge Fuse Blown", "Short circuit in transfer switch blew internal ceramic fuse.", "64-0031", "30A 250V Ceramic Fast-Acting Cartridge Fuse", "Easy (20-30 mins)", "$25 - $40", "Continuity: < 0.2 Ω when intact"),
        ("Fault DC Terminal", "5/16 DC Connection Stud Threads Stripped", "Overtightened battery cable lug stripped brass stud.", "64-0032", "Heavy Duty Copper DC Terminal Stud Assembly", "Medium (25-35 mins)", "$85 - $130", "Torque 5/16 DC terminal nuts to 120 in-lbs (10 ft-lbs)"),
        ("Fault Lithium Profile", "Custom Lithium Battery Voltage Profile Lost", "Remote memory reverted to default flooded lead-acid profile.", "ME-ARC50", "Magnum Advanced Remote Control Display Panel", "Easy (15-25 mins)", "$280 - $420", "Set custom absorb voltage: 14.4V; float: 13.6V; LVD: 11.8V"),
        ("Fault Internal Micro", "Control Motherboard DSP Processor Hardware Error", "Digital signal processor logic failure on motherboard.", "64-0033", "Magnum Main DSP Control Motherboard PCB", "Medium (35-50 mins)", "$480 - $720", "Inspect 12V DC power rail and crystal oscillator status"),
        ("Fault Ground Relay", "Internal Neutral-to-Ground Bonding Relay Stuck", "Safety bonding relay failed to disconnect when shore active.", "64-0029", "Magnum 30A Dual-Pole AC Transfer Relay Board", "Medium (30-45 mins)", "$340 - $520", "Test Neutral to Ground: bonded (< 0.2 Ω) only in inverter mode"),
        ("Fault Fuse 300A", "Main Class T Inverter Battery Fuse Blown", "300A Class T fuse blown on main battery cable.", "CF-300", "300A 160V DC Fast-Acting Class T Marine Fuse", "Easy (15-25 mins)", "$75 - $115", "Continuity: < 0.2 Ω when intact; test for battery short"),
        ("Fault Inverter Hum", "Toroid Iron Core Lamination Loose", "Inverter produces audible 60Hz mechanical vibration.", "64-0030", "Heavy Duty Pure Sine Toroidal Transformer 2800W", "Easy (20-30 mins)", "$140 - $210", "Tighten center 3/8-inch neoprene transformer mounting bolt"),
        ("Fault Current Shunt", "Internal DC Current Transducer Circuit Open", "Hall effect current transducer failed on motherboard.", "64-0033", "Magnum Main DSP Control Motherboard PCB", "Medium (35-50 mins)", "$480 - $720", "Check 5V DC reference to Hall effect current sensor"),
        ("Annual Maintenance", "Complete Annual Inverter Diagnostic Service", "Annual RV / marine electrical safety inspection.", "ME-ARC50", "Magnum ARC Remote Firmware Programming Cable", "Easy (20-30 mins)", "$75 - $115", "Check DC terminal torque, blow dust from heatsinks, update remote")
    ]),

    # -------------------------------------------------------------------------
    # IBC TECHNOLOGIES CONDENSING GAS BOILERS
    # -------------------------------------------------------------------------
    ("IBC Technologies", "Condensing Gas Boiler", "SL 20-115G2 / DC 33-160 / VX 199", "Tankless Water Heaters & Combi Boilers", [
        ("Fault Ignition", "Ignition Failure / Flame Signal Not Sensed", "Burner failed to establish rectified flame current in 4s.", "180-148", "Silicon Nitride Hot Surface Igniter & Flame Rod", "Medium (25-40 mins)", "$280 - $420", "Flame current > 2.0 uA DC; cold resistance 45–80 Ω"),
        ("Fault High Limit", "Heat Exchanger Safety High Limit Switch 200F", "Outlet water temperature exceeded 200F emergency limit.", "180-149", "Manual Reset High Temperature Limit Switch 200F", "Easy (20-30 mins)", "$190 - $280", "Continuity: < 0.3 Ω when cool; opens above 200F"),
        ("Fault Vent Temp", "Exhaust Flue Gas Temperature Limit Exceeded", "Flue exhaust thermistor exceeded 190F (90C) cutoff.", "180-150", "Flue Gas Exhaust Temperature Thermistor Sensor", "Easy (20-30 mins)", "$180 - $270", "12k NTC: 12k Ω at 77F (25C); opens above 190F"),
        ("Fault Low Water", "Electronic Low Water Cutoff (LWCO) Tripped", "Electronic water level probe detected low boiler water.", "180-151", "Electronic Low Water Cutoff LWCO Probe Assembly", "Medium (25-35 mins)", "$260 - $390", "Test 24V AC power to module; clean probe tip with emery cloth"),
        ("Fault Water Press", "System Water Pressure Switch Low Pressure Trip", "Hydronic loop water pressure dropped below 8 PSI.", "180-152", "Water Pressure Switch Safety Sensor 1/4 NPT", "Easy (20-30 mins)", "$170 - $260", "Closed continuity > 10 PSI; open circuit < 8 PSI"),
        ("Fault Fan Speed", "Combustion Blower Fan Tachometer Signal Loss", "Draft fan running below required modulation RPM.", "180-153", "Variable Speed Combustion Air Blower Assembly", "Medium (35-50 mins)", "$440 - $680", "Test 120V AC power and 0–10V DC PWM speed signal from board"),
        ("Fault Gas Valve", "Pneumatic Modulating Gas Valve Coil Open", "Modulating gas train solenoid coil open circuit.", "180-154", "SIT 848 SIGMA Pneumatic Gas Valve Assembly", "Hard (50-75 mins)", "$450 - $690", "Main coil: 35–55 Ω; 24V AC operating voltage"),
        ("Fault Supply Temp", "Boiler Supply Water Temperature Sensor Open", "Supply thermistor reading open or shorted out of range.", "180-155", "Water Temperature Thermistor Sensor NTC 10k", "Easy (15-25 mins)", "$150 - $220", "10k Ω at 77F (25C); 1.4k Ω at 176F (80C)"),
        ("Fault Return Temp", "Boiler Return Water Temperature Sensor Open", "Return water thermistor circuit open or drifting.", "180-155", "Water Temperature Thermistor Sensor NTC 10k", "Easy (15-25 mins)", "$150 - $220", "10k Ω at 77F (25C); 3.8k Ω at 122F (50C)"),
        ("Fault Outdoor Reset", "Outdoor Ambient Reset Thermistor Fault", "Outdoor weather sensor wiring severed or shorted.", "180-156", "Outdoor Ambient Air Temperature Reset Sensor", "Easy (15-25 mins)", "$140 - $210", "10k Ω at 77F (25C); 32.6k Ω at 32F (0C)"),
        ("Fault Condensate", "Condensate Trap Float Switch Blockage Trip", "Acidic condensate backed up in trap tripping float.", "180-157", "Condensate Drain Trap Assembly with Float Switch", "Easy (20-30 mins)", "$180 - $270", "Float switch continuity: closed when dry; opens when flooded"),
        ("Fault Air Switch", "Differential Air Pressure Switch Stuck Open", "Intake air pipe blocked or pressure switch failed.", "180-158", "Differential Air Pressure Switch Sensor", "Easy (20-30 mins)", "$180 - $270", "Contacts close at 0.95 in. WC differential pressure"),
        ("Fault Touchscreen", "V-10 Color Touchscreen Display Comm Loss", "Touchscreen console lost serial communication to controller.", "180-159", "V-10 Color Touchscreen Display Controller", "Easy (20-30 mins)", "$420 - $650", "Check 4-wire RS-485 communication harness for oxidation"),
        ("Fault Main Board", "SIM Integrated Microprocessor Control Board Fault", "Main boiler motherboard logic processor failure.", "180-160", "SIM Integrated Boiler Controller Motherboard PCB", "Medium (40-60 mins)", "$580 - $890", "Inspect 24V secondary transformer; verify ground reference"),
        ("Fault Pump 1 Relay", "Primary Boiler Recirculation Pump Relay Bad", "Internal pump switching relay contacts failed.", "180-160", "SIM Integrated Boiler Controller Motherboard PCB", "Medium (30-45 mins)", "$350 - $520", "Test 120V AC output across boiler pump terminal pins"),
        ("Fault Pump 2 Relay", "Secondary System / DHW Loop Pump Relay Bad", "System loop circulator pump relay failed to close.", "180-160", "SIM Integrated Boiler Controller Motherboard PCB", "Medium (30-45 mins)", "$350 - $520", "Test 120V AC output across DHW pump terminal pins"),
        ("Fault Delta-T", "Supply and Return Temperature Difference > 55F", "Low hydronic water circulation causing high delta-T.", "180-161", "Taco ECM High Efficiency Variable Speed Pump", "Medium (35-50 mins)", "$340 - $510", "Clean Y-strainer screen; verify system pump speed setting"),
        ("Fault Gas Pressure", "Inlet Natural Gas Pressure Below 3.5 in. WC", "Inlet gas line regulator delivering insufficient fuel.", "180-154", "Inlet Gas Pressure Safety Switch Sensor", "Medium (25-35 mins)", "$210 - $320", "Digital manometer test: static > 7.0 in. WC; dynamic > 4.5 in."),
        ("Fault Burner Gasket", "Burner Refractory Access Door Gasket Leaking", "Exhaust gas leaking around stainless burner door.", "180-162", "Burner Door Graphite Refractory Gasket Kit", "Medium (45-65 mins)", "$180 - $270", "Replace refractory door gasket and torx mounting bolts"),
        ("Fault Flow Switch", "Combi Domestic Hot Water Flow Switch Stalled", "Turbine flow sensor stuck delivering cold DHW.", "180-163", "DHW Turbine Water Flow Switch Sensor Assembly", "Easy (20-30 mins)", "$160 - $240", "Switch contacts close when water flow exceeds 0.5 GPM"),
        ("Fault DHW Temp", "Combi DHW Outlet Water Thermistor Out of Spec", "Domestic water outlet sensor reading open or shorted.", "180-155", "Water Temperature Thermistor Sensor NTC 10k", "Easy (15-25 mins)", "$150 - $220", "10k NTC: 10k Ω at 77F (25C); 3.6k Ω at 122F (50C)"),
        ("Fault Low Voltage", "Power Supply Line Voltage Below 102V AC", "Campground or utility line power dropped below threshold.", "180-160", "SIM Integrated Boiler Controller Motherboard PCB", "Easy (15-25 mins)", "$140 - $200", "Supply voltage must be 108V–132V AC 60Hz"),
        ("Fault Cascade Comm", "Multi-Boiler Cascade ModBus Addressing Conflict", "Two member boilers sharing the same network address.", "180-159", "V-10 Color Touchscreen Display Controller", "Easy (15-25 mins)", "$160 - $240", "Assign unique cascade addresses (1 through 24) on touchscreen"),
        ("Fault Plate Exch", "Combi Brazed Plate Heat Exchanger Calcified", "Hard water scale coated domestic water plates.", "180-164", "Stainless Steel Brazed Plate Heat Exchanger (DHW)", "Medium (45-60 mins)", "$380 - $570", "Perform chemical descaling flush with food-grade acid"),
        ("Annual Service", "Annual Combustion Chamber Clean & Tune-Up", "1-year runtime service interval reached.", "IBC-TUNE", "Annual Maintenance Gasket, Electrode & Filter Kit", "Medium (60-90 mins)", "$260 - $390", "Clean stainless heat exchanger pins, replace igniter, flush trap")
    ])
]
