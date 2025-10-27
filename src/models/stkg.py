"""
4D Spatiotemporal Knowledge Graph (STKG) Data Models
Based on Definition 1 from the paper
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
from enum import Enum


class EntityClass(Enum):
    """Entity classes for the domain ontology"""
    EQUIPMENT = "Equipment"
    LOCATION = "Location"
    PERSONNEL = "Personnel"
    EVENT = "Event"
    COMPONENT = "Component"


class RelationType(Enum):
    """Relation types for the domain ontology"""
    INSTALLED_AT = "installedAt"
    INSPECTED_BY = "inspectedBy"
    LOCATED_IN = "locatedIn"
    PRECEDES = "precedes"
    MOVED_TO = "movedTo"
    CONTAINS = "contains"


@dataclass
class SpatiotemporalCoordinate:
    """Spatiotemporal coordinates (x, y, z, t)"""
    x: float
    y: float
    z: float
    t: datetime

    def distance_to(self, other: 'SpatiotemporalCoordinate') -> float:
        """Calculate Euclidean distance between spatial coordinates"""
        return ((self.x - other.x)**2 +
                (self.y - other.y)**2 +
                (self.z - other.z)**2)**0.5

    def time_diff(self, other: 'SpatiotemporalCoordinate') -> float:
        """Calculate time difference in seconds"""
        return abs((self.t - other.t).total_seconds())


@dataclass
class Entity:
    """Entity with versioning support"""
    id: str
    entity_class: EntityClass
    attributes: Dict[str, any]
    version: int = 1

    def __hash__(self):
        return hash(f"{self.id}-v{self.version}")


@dataclass
class Fact:
    """
    A fact triple (s, r, o) with spatiotemporal coordinate and confidence
    d_k = <s, r, o, T(d_k), conf_k>
    """
    subject: Entity
    relation: RelationType
    object: Entity
    coordinate: SpatiotemporalCoordinate
    confidence: float = 1.0  # LLM confidence score
    source_text: Optional[str] = None

    def __str__(self):
        return f"<{self.subject.id}, {self.relation.value}, {self.object.id}>"

    def to_dict(self) -> Dict:
        """Convert fact to dictionary representation"""
        return {
            "subject": self.subject.id,
            "subject_class": self.subject.entity_class.value,
            "relation": self.relation.value,
            "object": self.object.id,
            "object_class": self.object.entity_class.value,
            "coordinates": {
                "x": self.coordinate.x,
                "y": self.coordinate.y,
                "z": self.coordinate.z,
                "t": self.coordinate.t.isoformat()
            },
            "confidence": self.confidence,
            "source": self.source_text
        }


@dataclass
class DomainOntology:
    """Domain ontology O = (C, R_o, A)"""
    classes: Set[EntityClass]
    relations: Set[RelationType]
    attributes: Dict[EntityClass, List[str]]

    # Domain and range restrictions
    relation_domains: Dict[RelationType, Set[EntityClass]]
    relation_ranges: Dict[RelationType, Set[EntityClass]]

    def is_valid_triple(self, subject_class: EntityClass,
                       relation: RelationType,
                       object_class: EntityClass) -> bool:
        """Check if triple satisfies domain/range restrictions"""
        if relation not in self.relations:
            return False

        valid_domains = self.relation_domains.get(relation, set())
        valid_ranges = self.relation_ranges.get(relation, set())

        return (subject_class in valid_domains and
                object_class in valid_ranges)


class PhysicsConstraints:
    """Physical consistency predicate Ψ"""

    def __init__(self, max_velocity: float = 5.0,
                 temporal_resolution: float = 1.0,
                 spatial_resolution: float = 0.1):
        """
        Args:
            max_velocity: Maximum velocity in m/s (v_max)
            temporal_resolution: τ_res in seconds
            spatial_resolution: σ_res in meters
        """
        self.v_max = max_velocity
        self.tau_res = temporal_resolution
        self.sigma_res = spatial_resolution

    def spatial_consistency(self, fact: Fact,
                          existing_facts: List[Fact]) -> bool:
        """
        Check spatial consistency ψ_s (Definition 2)
        No entity at two separated locations within same time window
        """
        for other_fact in existing_facts:
            # Check if same entity
            if fact.subject.id != other_fact.subject.id:
                continue

            # Check temporal proximity
            time_diff = fact.coordinate.time_diff(other_fact.coordinate)
            if time_diff >= self.tau_res:
                continue

            # Check spatial separation
            distance = fact.coordinate.distance_to(other_fact.coordinate)
            if distance > self.sigma_res:
                return False  # Violation: same entity, same time, different location

        return True

    def temporal_consistency(self, fact: Fact,
                           previous_fact: Optional[Fact]) -> Tuple[bool, float]:
        """
        Check temporal consistency ψ_t (Definition 3)
        Returns: (is_consistent, required_velocity)
        """
        if previous_fact is None:
            return True, 0.0

        # Calculate travel time and required velocity
        distance = fact.coordinate.distance_to(previous_fact.coordinate)
        time_diff = fact.coordinate.time_diff(previous_fact.coordinate)

        if time_diff == 0:
            return distance < self.sigma_res, float('inf')

        v_required = distance / time_diff

        # Check if movement is physically possible
        is_consistent = v_required <= self.v_max

        return is_consistent, v_required

    def check_consistency(self, fact: Fact,
                         existing_facts: List[Fact]) -> Tuple[bool, Dict[str, any]]:
        """
        Check both spatial and temporal consistency: Ψ(d) = ψ_s(d) ∧ ψ_t(d)
        Returns: (is_consistent, details)
        """
        # Find previous fact for same entity
        previous_fact = None
        for f in sorted(existing_facts,
                       key=lambda x: x.coordinate.t,
                       reverse=True):
            if f.subject.id == fact.subject.id:
                previous_fact = f
                break

        spatial_ok = self.spatial_consistency(fact, existing_facts)
        temporal_ok, v_req = self.temporal_consistency(fact, previous_fact)

        return (spatial_ok and temporal_ok, {
            "spatial_consistent": spatial_ok,
            "temporal_consistent": temporal_ok,
            "required_velocity": v_req,
            "max_velocity": self.v_max
        })


class STKG:
    """4D Spatiotemporal Knowledge Graph G = (V, E, O, T, Ψ)"""

    def __init__(self, ontology: DomainOntology,
                 physics: PhysicsConstraints):
        self.vertices: List[Entity] = []
        self.edges: List[Fact] = []
        self.ontology = ontology
        self.physics = physics

    def add_fact(self, fact: Fact) -> Tuple[bool, str]:
        """
        Add fact to STKG with validation
        Returns: (success, message)
        """
        # Check ontology validity
        if not self.ontology.is_valid_triple(
            fact.subject.entity_class,
            fact.relation,
            fact.object.entity_class
        ):
            return False, "Ontology violation: invalid domain/range"

        # Check physical consistency
        is_consistent, details = self.physics.check_consistency(fact, self.edges)
        if not is_consistent:
            return False, f"Physical consistency violation: {details}"

        # Add entities if not present
        if fact.subject not in self.vertices:
            self.vertices.append(fact.subject)
        if fact.object not in self.vertices:
            self.vertices.append(fact.object)

        # Add fact
        self.edges.append(fact)
        return True, "Fact added successfully"

    def get_entity_history(self, entity_id: str) -> List[Fact]:
        """Get all facts involving an entity, sorted by time"""
        facts = [f for f in self.edges
                if f.subject.id == entity_id or f.object.id == entity_id]
        return sorted(facts, key=lambda f: f.coordinate.t)
