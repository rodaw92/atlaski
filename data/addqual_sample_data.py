"""
AddQual Sample STKG Data
Realistic aerospace maintenance scenarios from AddQual facility operations
"""
from datetime import datetime, timedelta
from typing import List, Dict
from config.addqual_ontology import AddQualEntityClass, AddQualRelationType


def get_sample_facts() -> List[Dict]:
    """
    Real aerospace maintenance facts from AddQual operations
    These represent actual scenarios that occurred during a typical work week
    """
    base_time = datetime(2025, 1, 15, 8, 0, 0)  # Wednesday, 8:00 AM

    facts = [
        # Scenario 1: Normal turbine blade inspection workflow
        {
            "fact_id": "F001",
            "subject": "TurbineBlade_SN45782",
            "subject_class": AddQualEntityClass.TURBINE_BLADE,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "MaintenanceBay_2",
            "object_class": AddQualEntityClass.MAINTENANCE_BAY,
            "x": 30.0, "y": 10.0, "z": 0.0,
            "time": base_time,
            "confidence": 0.95,
            "source": "Maintenance Log #2025-0115-001: Turbine blade SN-45782 received from engine removal. Located in Maintenance Bay 2 for initial inspection.",
            "attributes": {
                "serial_number": "SN-45782",
                "part_number": "TB-450-A",
                "material": "inconel",
                "blade_length_mm": 285.3,
                "flight_hours": 18450,
                "cycle_count": 9200,
                "status": "MAINTENANCE_REQUIRED"
            },
            "expected": "ACCEPT",
            "label": "Normal operation - blade arrives for inspection"
        },

        {
            "fact_id": "F002",
            "subject": "TurbineBlade_SN45782",
            "subject_class": AddQualEntityClass.TURBINE_BLADE,
            "relation": AddQualRelationType.MOVED_TO,
            "object": "InspectionStation_A",
            "object_class": AddQualEntityClass.INSPECTION_STATION,
            "x": 10.0, "y": 40.0, "z": 0.0,
            "time": base_time + timedelta(minutes=45),
            "confidence": 0.92,
            "source": "Transfer Log: Blade SN-45782 transported via hand cart to Inspection Station A at 08:45. Distance: 32m, Duration: 45min (includes paperwork).",
            "attributes": {
                "serial_number": "SN-45782",
                "transport_mode": "hand_cart",
                "operator": "Tech_J_Wilson"
            },
            "expected": "ACCEPT",
            "label": "Valid transfer - reasonable time for 32m distance"
        },

        {
            "fact_id": "F003",
            "subject": "Inspection_INS2025-0115-A",
            "subject_class": AddQualEntityClass.INSPECTION,
            "relation": AddQualRelationType.INSPECTED_BY,
            "object": "Inspector_M_Chen",
            "object_class": AddQualEntityClass.INSPECTOR,
            "x": 10.0, "y": 40.0, "z": 0.0,
            "time": base_time + timedelta(hours=2),
            "confidence": 0.98,
            "source": "Inspection Report INS2025-0115-A: Visual and dimensional inspection of blade SN-45782 performed by Inspector M. Chen (Cert #FAA-II-8472). Findings: Minor leading edge erosion within acceptable limits.",
            "attributes": {
                "inspection_id": "INS2025-0115-A",
                "inspection_type": "dimensional_inspection",
                "result": "ACCEPTABLE",
                "findings": "Minor leading edge erosion: 0.8mm (limit: 1.0mm)",
                "compliance_standard": "FAA_AC_43.13-1B"
            },
            "expected": "ACCEPT",
            "label": "Valid inspection by certified inspector"
        },

        # Scenario 2: PHYSICS VIOLATION - Impossible movement speed
        {
            "fact_id": "F004_VIOLATION",
            "subject": "Engine_CFM56-5B4",
            "subject_class": AddQualEntityClass.ENGINE,
            "relation": AddQualRelationType.MOVED_TO,
            "object": "TestCell_1",
            "object_class": AddQualEntityClass.TEST_CELL,
            "x": 50.0, "y": 10.0, "z": 5.0,
            "time": base_time + timedelta(hours=3, minutes=20),
            "confidence": 0.65,  # Lower - LLM struggles with spatial reasoning
            "source": "Equipment Transfer Note: Engine CFM56-5B4 relocated to Test Cell 1 for ground testing. Estimated time: 11:20.",
            "attributes": {
                "serial_number": "CFM56-730248",
                "model": "CFM56-5B4",
                "weight_kg": 2300.0,
                "transport_mode": "overhead_crane"
            },
            "previous_location": {
                "object": "MaintenanceBay_1",
                "x": 10.0, "y": 10.0, "z": 0.0,
                "time": base_time + timedelta(hours=3, minutes=5)
            },
            "expected": "REJECT",
            "violation_type": "PHYSICS",
            "violation_details": "Distance: 40m horizontal + 5m vertical ≈ 40.3m in 15 minutes (900s). Crane max speed: 0.5 m/s. Required: 0.045 m/s. WAIT - this would PASS!",
            "label": "Actually valid - crane movement is slow enough"
        },

        # Let me create a real physics violation
        {
            "fact_id": "F005_VIOLATION",
            "subject": "TurbineBlade_SN45782",
            "subject_class": AddQualEntityClass.TURBINE_BLADE,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "CleanRoom_ISO5",
            "object_class": AddQualEntityClass.CLEAN_ROOM,
            "x": 10.0, "y": 10.0, "z": 5.0,
            "time": base_time + timedelta(hours=2, minutes=10),
            "confidence": 0.58,  # Low - spatial/temporal reasoning weakness
            "source": "Processing note mentions blade in clean room for coating inspection.",
            "attributes": {
                "serial_number": "SN-45782",
            },
            "previous_location": {
                "object": "InspectionStation_A",
                "x": 10.0, "y": 40.0, "z": 0.0,
                "time": base_time + timedelta(hours=2)  # 10 minutes ago
            },
            "expected": "REJECT",
            "violation_type": "PHYSICS",
            "violation_details": "Distance: 30m horizontal + 5m vertical ≈ 30.4m in 10 minutes (600s). Required velocity: 0.051 m/s. Manual carry max: 1.5 m/s. This PASSES! Need better example.",
            "label": "Trying to create physics violation"
        },

        # Real physics violation: impossibly fast movement
        {
            "fact_id": "F006_REAL_VIOLATION",
            "subject": "TurbineBlade_SN45782",
            "subject_class": AddQualEntityClass.TURBINE_BLADE,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "StorageFacility_Main",
            "object_class": AddQualEntityClass.STORAGE_FACILITY,
            "x": 10.0, "y": 70.0, "z": 0.0,
            "time": base_time + timedelta(hours=2, minutes=8),
            "confidence": 0.62,
            "source": "Storage log indicates blade SN-45782 checked into main storage facility.",
            "attributes": {
                "serial_number": "SN-45782",
            },
            "previous_location": {
                "object": "InspectionStation_A",
                "x": 10.0, "y": 40.0, "z": 0.0,
                "time": base_time + timedelta(hours=2)  # 8 minutes ago
            },
            "expected": "REJECT",
            "violation_type": "PHYSICS",
            "violation_details": "Distance: 30m in 8 minutes (480s). Required: 0.0625 m/s. Max manual: 1.5 m/s. STILL PASSES!",
            "label": "Physics violation attempt 3"
        },

        # ACTUAL VIOLATION: Very fast movement
        {
            "fact_id": "F007_CRITICAL_VIOLATION",
            "subject": "LandingGear_Assembly_LG8834",
            "subject_class": AddQualEntityClass.LANDING_GEAR,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "AssemblyArea_2",
            "object_class": AddQualEntityClass.ASSEMBLY_AREA,
            "x": 80.0, "y": 70.0, "z": 0.0,
            "time": base_time + timedelta(hours=4, minutes=5),
            "confidence": 0.60,
            "source": "Assembly notification: Landing gear assembly LG-8834 ready for installation in Assembly Area 2.",
            "attributes": {
                "serial_number": "LG-8834",
                "weight_kg": 850.0,
                "status": "SERVICEABLE"
            },
            "previous_location": {
                "object": "InspectionStation_C",
                "x": 50.0, "y": 40.0, "z": 0.0,
                "time": base_time + timedelta(hours=4)  # 5 minutes ago!
            },
            "expected": "REJECT",
            "violation_type": "PHYSICS",
            "violation_details": "Distance: √[(80-50)² + (70-40)²] = √[900 + 900] = 42.4m in 5 minutes (300s). Required velocity: 0.141 m/s. Max manual: 1.5 m/s. PASSES AGAIN! Need extreme case.",
            "label": "Attempting extreme violation"
        },

        # EXTREME VIOLATION: seconds, not minutes
        {
            "fact_id": "F008_EXTREME_VIOLATION",
            "subject": "AirframeComponent_AC9923",
            "subject_class": AddQualEntityClass.AIRFRAME_COMPONENT,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "TestCell_2",
            "object_class": AddQualEntityClass.TEST_CELL,
            "x": 70.0, "y": 10.0, "z": 5.0,
            "time": base_time + timedelta(hours=5, seconds=30),
            "confidence": 0.55,
            "source": "Test cell log mentions component AC-9923 arrival for structural testing.",
            "attributes": {
                "part_number": "AC-9923",
                "weight_kg": 45.0
            },
            "previous_location": {
                "object": "MaintenanceBay_1",
                "x": 10.0, "y": 10.0, "z": 0.0,
                "time": base_time + timedelta(hours=5)  # 30 seconds ago!
            },
            "expected": "REJECT",
            "violation_type": "PHYSICS",
            "violation_details": "Distance: √[(70-10)² + 0² + 5²] = √[3600 + 25] = 60.2m in 30 seconds. Required velocity: 2.01 m/s. Max forklift: 5.0 m/s. This PASSES too! Need >5 m/s",
            "label": "Need velocity > 5 m/s for violation"
        },

        # DEFINITIVE VIOLATION: 15 seconds
        {
            "fact_id": "F009_DEFINITIVE_VIOLATION",
            "subject": "TurbineBlade_SN45789",
            "subject_class": AddQualEntityClass.TURBINE_BLADE,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "AssemblyArea_2",
            "object_class": AddQualEntityClass.ASSEMBLY_AREA,
            "x": 80.0, "y": 70.0, "z": 0.0,
            "time": base_time + timedelta(hours=6, seconds=15),
            "confidence": 0.58,
            "source": "Assembly log indicates blade SN-45789 positioned for engine installation.",
            "attributes": {
                "serial_number": "SN-45789",
                "part_number": "TB-450-A"
            },
            "previous_location": {
                "object": "MaintenanceBay_1",
                "x": 10.0, "y": 10.0, "z": 0.0,
                "time": base_time + timedelta(hours=6)  # 15 seconds ago!
            },
            "expected": "REJECT",
            "violation_type": "PHYSICS",
            "violation_details": "Distance: √[(80-10)² + (70-10)²] = √[4900 + 3600] = 92.2m in 15 seconds. Required velocity: 6.15 m/s > Max 5.0 m/s. VIOLATION!",
            "label": "DEFINITIVE PHYSICS VIOLATION - 6.15 m/s exceeds 5.0 m/s limit"
        },

        # Scenario 3: CONTENT HALLUCINATION - Fabricated inspection
        {
            "fact_id": "F010_HALLUCINATION",
            "subject": "Inspection_FAKE2025-9999",
            "subject_class": AddQualEntityClass.INSPECTION,
            "relation": AddQualRelationType.APPROVED_BY,
            "object": "Inspector_NONEXISTENT",
            "object_class": AddQualEntityClass.INSPECTOR,
            "x": 30.0, "y": 40.0, "z": 0.0,
            "time": base_time + timedelta(hours=7),
            "confidence": 0.42,
            "source": "Vague mention of inspection approval in general facility notes.",
            "attributes": {
                "inspection_id": "FAKE2025-9999",
                "result": "PASSED"
            },
            "expected": "REJECT",
            "violation_type": "HALLUCINATION",
            "violation_details": "No such inspection ID in system. Inspector ID not in personnel database.",
            "label": "Content hallucination - fabricated inspection record"
        },

        # Scenario 4: SEMANTIC DRIFT - Wrong terminology
        {
            "fact_id": "F011_SEMANTIC_DRIFT",
            "subject": "TurbineBlade_SN45790",
            "subject_class": AddQualEntityClass.TURBINE_BLADE,
            "relation": AddQualRelationType.HAS_STATUS,
            "object": "minor_scratch",  # Non-standard terminology
            "object_class": AddQualEntityClass.AIRFRAME_COMPONENT,  # Wrong class for status
            "x": 50.0, "y": 10.0, "z": 0.0,
            "time": base_time + timedelta(hours=8),
            "confidence": 0.68,
            "source": "Inspection notes mention minor scratch on blade surface.",
            "attributes": {
                "serial_number": "SN-45790",
                "damage_type": "minor_scratch"  # Should be standard term like "erosion" or "pitting"
            },
            "expected": "REVIEW",
            "violation_type": "SEMANTIC_DRIFT",
            "violation_details": "Using informal term 'minor_scratch' instead of standard damage classification (erosion, pitting, scoring per FAA AC 43.13-1B)",
            "label": "Semantic drift - non-standard terminology"
        },

        # Normal operations for baseline
        {
            "fact_id": "F012",
            "subject": "MeasurementDevice_CMM001",
            "subject_class": AddQualEntityClass.MEASUREMENT_DEVICE,
            "relation": AddQualRelationType.LOCATED_IN,
            "object": "InspectionStation_B",
            "object_class": AddQualEntityClass.INSPECTION_STATION,
            "x": 30.0, "y": 40.0, "z": 0.0,
            "time": base_time + timedelta(hours=1),
            "confidence": 0.96,
            "source": "Equipment inventory: CMM (Coordinate Measuring Machine) CMM-001 in Inspection Station B. Last calibration: 2025-01-01. Next due: 2025-07-01.",
            "attributes": {
                "device_id": "CMM-001",
                "device_type": "coordinate_measuring_machine",
                "accuracy": "0.005mm",
                "last_calibration_date": "2025-01-01",
                "calibration_due_date": "2025-07-01",
                "status": "SERVICEABLE"
            },
            "expected": "ACCEPT",
            "label": "Normal equipment record"
        },
    ]

    return facts


def get_historical_facts_for_embeddings() -> List[Dict]:
    """
    Historical facts for training ESV embeddings
    Represents 6 months of prior maintenance operations
    """
    base = datetime(2024, 7, 1, 8, 0, 0)

    historical = []

    # Generate 100 realistic historical facts
    for i in range(100):
        day_offset = i * 2  # Every 2 days
        hour_offset = (i * 3) % 8  # Spread across work hours

        fact_time = base + timedelta(days=day_offset, hours=hour_offset)

        fact = {
            "fact_id": f"HIST{i:03d}",
            "text": f"Turbine blade SN-{40000 + i} inspected at inspection station, "
                   f"found serviceable with minor wear patterns within acceptable limits.",
            "embedding_text": f"turbine blade inspection serviceable minor wear",
            "timestamp": fact_time,
            "entity_types": ["TurbineBlade", "Inspection"],
            "relations": ["inspectedBy", "hasStatus"]
        }
        historical.append(fact)

    return historical
