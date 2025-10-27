"""
AddQual Aerospace Domain Ontology
Complete ontology for aerospace maintenance and qualification operations
Based on STEP AP242 and FAA regulations
"""
from typing import Dict, List, Set, Tuple
from enum import Enum


class AddQualEntityClass(Enum):
    """Entity classes for AddQual aerospace domain"""
    # Aircraft Components
    TURBINE_BLADE = "TurbineBlade"
    ENGINE = "Engine"
    AIRFRAME_COMPONENT = "AirframeComponent"
    LANDING_GEAR = "LandingGear"
    AVIONICS = "Avionics"
    HYDRAULIC_SYSTEM = "HydraulicSystem"

    # Facilities
    MAINTENANCE_BAY = "MaintenanceBay"
    INSPECTION_STATION = "InspectionStation"
    ASSEMBLY_AREA = "AssemblyArea"
    STORAGE_FACILITY = "StorageFacility"
    TEST_CELL = "TestCell"
    CLEAN_ROOM = "CleanRoom"

    # Personnel
    INSPECTOR = "Inspector"
    TECHNICIAN = "Technician"
    ENGINEER = "Engineer"
    QUALITY_MANAGER = "QualityManager"

    # Processes
    INSPECTION = "Inspection"
    MAINTENANCE_TASK = "MaintenanceTask"
    QUALIFICATION_TEST = "QualificationTest"
    REPAIR_OPERATION = "RepairOperation"

    # Equipment
    MEASUREMENT_DEVICE = "MeasurementDevice"
    TRANSPORT_EQUIPMENT = "TransportEquipment"
    TOOLING = "Tooling"


class AddQualRelationType(Enum):
    """Relation types for AddQual domain"""
    # Location relations
    LOCATED_IN = "locatedIn"
    MOVED_TO = "movedTo"
    STORED_AT = "storedAt"

    # Component relations
    INSTALLED_ON = "installedOn"
    REMOVED_FROM = "removedFrom"
    PART_OF = "partOf"
    CONNECTED_TO = "connectedTo"

    # Process relations
    INSPECTED_BY = "inspectedBy"
    MAINTAINED_BY = "maintainedBy"
    TESTED_BY = "testedBy"
    APPROVED_BY = "approvedBy"

    # Status relations
    HAS_STATUS = "hasStatus"
    REQUIRES = "requires"
    COMPLIES_WITH = "compliesWith"

    # Temporal relations
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    CONCURRENT_WITH = "concurrentWith"


class AddQualOntology:
    """Complete AddQual domain ontology with industry-standard constraints"""

    @staticmethod
    def get_entity_attributes() -> Dict[AddQualEntityClass, List[str]]:
        """Define valid attributes for each entity class"""
        return {
            # Aircraft Components
            AddQualEntityClass.TURBINE_BLADE: [
                "serial_number", "part_number", "material", "blade_length_mm",
                "leading_edge_thickness_mm", "trailing_edge_thickness_mm",
                "coating_type", "manufacture_date", "flight_hours",
                "cycle_count", "last_inspection_date", "status"
            ],
            AddQualEntityClass.ENGINE: [
                "serial_number", "model", "manufacturer", "thrust_rating_lbs",
                "total_flight_hours", "cycles_since_overhaul", "status"
            ],
            AddQualEntityClass.AIRFRAME_COMPONENT: [
                "part_number", "serial_number", "material", "weight_kg",
                "dimensions", "corrosion_rating", "structural_integrity"
            ],

            # Facilities
            AddQualEntityClass.MAINTENANCE_BAY: [
                "bay_number", "facility_id", "coordinates", "capacity",
                "environmental_controls", "certification_level"
            ],
            AddQualEntityClass.INSPECTION_STATION: [
                "station_id", "inspection_type", "equipment_list",
                "certification_standard", "calibration_date"
            ],

            # Personnel
            AddQualEntityClass.INSPECTOR: [
                "employee_id", "name", "certification_number",
                "certification_level", "expiry_date", "specialization"
            ],
            AddQualEntityClass.TECHNICIAN: [
                "employee_id", "name", "license_number",
                "qualification_level", "authorized_operations"
            ],

            # Processes
            AddQualEntityClass.INSPECTION: [
                "inspection_id", "inspection_type", "timestamp",
                "result", "findings", "compliance_standard", "next_due_date"
            ],
            AddQualEntityClass.QUALIFICATION_TEST: [
                "test_id", "test_type", "standard", "result",
                "measured_values", "pass_criteria", "timestamp"
            ],

            # Equipment
            AddQualEntityClass.MEASUREMENT_DEVICE: [
                "device_id", "device_type", "accuracy", "range",
                "last_calibration_date", "calibration_due_date", "status"
            ],
            AddQualEntityClass.TRANSPORT_EQUIPMENT: [
                "equipment_id", "type", "max_velocity_ms", "max_load_kg",
                "operator_required", "safety_certification"
            ]
        }

    @staticmethod
    def get_hard_constraints() -> Dict[str, Dict]:
        """Hard constraints (must satisfy)"""
        return {
            # Dimensional constraints (STEP AP242)
            "blade_length_mm": {"min": 50.0, "max": 500.0, "type": "float"},
            "leading_edge_thickness_mm": {"min": 0.5, "max": 10.0, "type": "float"},
            "trailing_edge_thickness_mm": {"min": 0.3, "max": 5.0, "type": "float"},

            # Performance constraints
            "flight_hours": {"min": 0, "max": 50000, "type": "int"},
            "cycle_count": {"min": 0, "max": 100000, "type": "int"},
            "thrust_rating_lbs": {"min": 1000, "max": 100000, "type": "int"},

            # Environmental constraints
            "corrosion_rating": {"values": ["NONE", "MINOR", "MODERATE", "SEVERE"], "type": "enum"},
            "structural_integrity": {"values": ["EXCELLENT", "GOOD", "ACCEPTABLE", "UNACCEPTABLE"], "type": "enum"},
            "status": {"values": ["SERVICEABLE", "MAINTENANCE_REQUIRED", "UNSERVICEABLE", "QUARANTINE"], "type": "enum"},

            # Personnel constraints
            "certification_level": {"values": ["I", "II", "III", "MASTER"], "type": "enum"},
            "qualification_level": {"values": ["BASIC", "INTERMEDIATE", "ADVANCED", "EXPERT"], "type": "enum"},
        }

    @staticmethod
    def get_soft_constraints() -> Dict[str, Dict]:
        """Soft constraints (typical ranges, warnings if violated)"""
        return {
            # Typical operational ranges
            "blade_length_mm": {"typical_min": 100.0, "typical_max": 350.0},
            "leading_edge_thickness_mm": {"typical_min": 1.0, "typical_max": 5.0},
            "flight_hours": {"typical_max": 30000},  # Before major overhaul
            "cycle_count": {"typical_max": 50000},

            # Inspection intervals
            "days_since_inspection": {"typical_max": 90},  # Quarterly inspection
            "days_until_calibration": {"typical_min": 30},  # Advance warning
        }

    @staticmethod
    def get_relation_domains() -> Dict[AddQualRelationType, Set[AddQualEntityClass]]:
        """Define valid subject entity classes for each relation"""
        return {
            AddQualRelationType.LOCATED_IN: {
                AddQualEntityClass.TURBINE_BLADE,
                AddQualEntityClass.ENGINE,
                AddQualEntityClass.AIRFRAME_COMPONENT,
                AddQualEntityClass.LANDING_GEAR,
                AddQualEntityClass.MEASUREMENT_DEVICE
            },
            AddQualRelationType.MOVED_TO: {
                AddQualEntityClass.TURBINE_BLADE,
                AddQualEntityClass.ENGINE,
                AddQualEntityClass.AIRFRAME_COMPONENT
            },
            AddQualRelationType.INSPECTED_BY: {
                AddQualEntityClass.TURBINE_BLADE,
                AddQualEntityClass.ENGINE,
                AddQualEntityClass.AIRFRAME_COMPONENT,
                AddQualEntityClass.LANDING_GEAR,
                AddQualEntityClass.HYDRAULIC_SYSTEM
            },
            AddQualRelationType.INSTALLED_ON: {
                AddQualEntityClass.TURBINE_BLADE,
                AddQualEntityClass.AVIONICS,
                AddQualEntityClass.LANDING_GEAR
            },
            AddQualRelationType.APPROVED_BY: {
                AddQualEntityClass.INSPECTION,
                AddQualEntityClass.QUALIFICATION_TEST,
                AddQualEntityClass.REPAIR_OPERATION
            }
        }

    @staticmethod
    def get_relation_ranges() -> Dict[AddQualRelationType, Set[AddQualEntityClass]]:
        """Define valid object entity classes for each relation"""
        return {
            AddQualRelationType.LOCATED_IN: {
                AddQualEntityClass.MAINTENANCE_BAY,
                AddQualEntityClass.INSPECTION_STATION,
                AddQualEntityClass.ASSEMBLY_AREA,
                AddQualEntityClass.STORAGE_FACILITY,
                AddQualEntityClass.TEST_CELL,
                AddQualEntityClass.CLEAN_ROOM
            },
            AddQualRelationType.MOVED_TO: {
                AddQualEntityClass.MAINTENANCE_BAY,
                AddQualEntityClass.INSPECTION_STATION,
                AddQualEntityClass.ASSEMBLY_AREA,
                AddQualEntityClass.STORAGE_FACILITY
            },
            AddQualRelationType.INSPECTED_BY: {
                AddQualEntityClass.INSPECTOR
            },
            AddQualRelationType.MAINTAINED_BY: {
                AddQualEntityClass.TECHNICIAN
            },
            AddQualRelationType.INSTALLED_ON: {
                AddQualEntityClass.ENGINE,
                AddQualEntityClass.AIRFRAME_COMPONENT
            },
            AddQualRelationType.APPROVED_BY: {
                AddQualEntityClass.INSPECTOR,
                AddQualEntityClass.QUALITY_MANAGER
            }
        }

    @staticmethod
    def get_aerospace_standards_vocabulary() -> Set[str]:
        """
        Industry-standard terminology from STEP AP242, FAA regulations,
        and aerospace maintenance practices
        """
        return {
            # Component types (STEP AP242)
            "turbine", "blade", "rotor", "stator", "compressor", "combustor",
            "nozzle", "shaft", "bearing", "seal", "airfoil", "disk",
            "engine", "nacelle", "pylon", "wing", "fuselage", "empennage",
            "landing_gear", "strut", "actuator", "hydraulic", "pneumatic",

            # Materials (AMS specifications)
            "titanium", "nickel_alloy", "inconel", "aluminum", "composite",
            "steel", "ceramic", "coating", "thermal_barrier", "erosion_resistant",

            # Inspection terms (FAA/EASA)
            "visual_inspection", "dimensional_inspection", "NDT", "eddy_current",
            "ultrasonic", "radiographic", "magnetic_particle", "dye_penetrant",
            "borescope", "fluorescent_penetrant",

            # Maintenance operations
            "installation", "removal", "replacement", "overhaul", "repair",
            "cleaning", "coating_application", "balancing", "alignment",
            "functional_test", "ground_test", "acceptance_test",

            # Status terms (FAA Part 145)
            "serviceable", "unserviceable", "beyond_economical_repair",
            "awaiting_parts", "in_progress", "quarantine", "released_to_service",

            # Damage types
            "crack", "corrosion", "erosion", "foreign_object_damage",
            "thermal_damage", "fatigue", "wear", "pitting", "scoring",
            "delamination", "disbonding",

            # Relations
            "locatedIn", "installedOn", "inspectedBy", "maintainedBy",
            "approvedBy", "removedFrom", "movedTo", "partOf",

            # Facilities
            "maintenance_bay", "inspection_station", "test_cell",
            "assembly_area", "storage_facility", "clean_room",

            # Standards references
            "FAA", "EASA", "AS9100", "STEP_AP242", "AMS", "SAE",
            "ASTM", "ISO", "MIL_STD", "airworthiness_directive"
        }


# Facility layout for AddQual (spatial constraints)
ADDQUAL_FACILITY_LAYOUT = {
    # Ground floor - Maintenance
    "MaintenanceBay_1": {"x": 10.0, "y": 10.0, "z": 0.0, "capacity": 1},
    "MaintenanceBay_2": {"x": 30.0, "y": 10.0, "z": 0.0, "capacity": 1},
    "MaintenanceBay_3": {"x": 50.0, "y": 10.0, "z": 0.0, "capacity": 1},
    "MaintenanceBay_4": {"x": 70.0, "y": 10.0, "z": 0.0, "capacity": 1},

    # Ground floor - Inspection
    "InspectionStation_A": {"x": 10.0, "y": 40.0, "z": 0.0, "capacity": 2},
    "InspectionStation_B": {"x": 30.0, "y": 40.0, "z": 0.0, "capacity": 2},
    "InspectionStation_C": {"x": 50.0, "y": 40.0, "z": 0.0, "capacity": 2},

    # Ground floor - Storage
    "StorageFacility_Main": {"x": 10.0, "y": 70.0, "z": 0.0, "capacity": 50},
    "StorageFacility_Quarantine": {"x": 30.0, "y": 70.0, "z": 0.0, "capacity": 20},

    # Ground floor - Assembly
    "AssemblyArea_1": {"x": 60.0, "y": 70.0, "z": 0.0, "capacity": 5},
    "AssemblyArea_2": {"x": 80.0, "y": 70.0, "z": 0.0, "capacity": 5},

    # Second floor - Clean rooms
    "CleanRoom_ISO5": {"x": 10.0, "y": 10.0, "z": 5.0, "capacity": 3},
    "CleanRoom_ISO7": {"x": 30.0, "y": 10.0, "z": 5.0, "capacity": 5},

    # Second floor - Test cells
    "TestCell_1": {"x": 50.0, "y": 10.0, "z": 5.0, "capacity": 1},
    "TestCell_2": {"x": 70.0, "y": 10.0, "z": 5.0, "capacity": 1},
}

# Transport modes and constraints
TRANSPORT_MODES = {
    "manual_carry": {
        "max_velocity_ms": 1.5,  # Walking speed
        "max_distance_m": 50.0,
        "max_weight_kg": 25.0,
        "requires_operator": True
    },
    "hand_cart": {
        "max_velocity_ms": 2.0,
        "max_distance_m": 200.0,
        "max_weight_kg": 100.0,
        "requires_operator": True
    },
    "forklift": {
        "max_velocity_ms": 5.0,  # Facility speed limit
        "max_distance_m": 500.0,
        "max_weight_kg": 2000.0,
        "requires_operator": True,
        "operator_certification": "FORKLIFT_LICENSE"
    },
    "overhead_crane": {
        "max_velocity_ms": 0.5,  # Slow for safety
        "max_distance_m": 100.0,
        "max_weight_kg": 5000.0,
        "requires_operator": True,
        "operator_certification": "CRANE_OPERATOR"
    },
    "automated_conveyor": {
        "max_velocity_ms": 1.0,
        "max_distance_m": 150.0,
        "max_weight_kg": 500.0,
        "requires_operator": False
    }
}
