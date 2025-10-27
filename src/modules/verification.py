"""
TruthFlow Verification Modules (M1-M5)
Implementation of Ranked Multi-Modal Verification (RMMVe)
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from src.models.stkg import Fact, DomainOntology, EntityClass, RelationType


@dataclass
class VerificationResult:
    """Result from a verification module"""
    module_name: str
    module_id: str
    metric1_score: float
    metric2_score: float
    final_score: float
    activated: bool
    details: Dict[str, any]
    cost_ms: float
    cost_usd: float


class VerificationModule:
    """Base class for verification modules"""

    def __init__(self, module_id: str, module_name: str,
                 threshold: float = 0.5,
                 alpha: float = 0.5,
                 weight: float = 0.2,
                 cost_ms: float = 10,
                 cost_usd: float = 0.001):
        """
        Args:
            threshold: Activation threshold θ_i
            alpha: Balance factor α_i for metrics
            weight: Trust weight w_i
        """
        self.module_id = module_id
        self.module_name = module_name
        self.threshold = threshold
        self.alpha = alpha
        self.weight = weight
        self.cost_ms = cost_ms
        self.cost_usd = cost_usd

    def compute_score(self, fact: Fact, context: Dict) -> VerificationResult:
        """
        Compute module score using dual metrics
        S_i(d_k) = conf_k × [α_i · Metric_1^(i)(d_k) + (1-α_i) · Metric_2^(i)(d_k)]
        """
        metric1 = self._compute_metric1(fact, context)
        metric2 = self._compute_metric2(fact, context)

        # Apply balance factor
        raw_score = self.alpha * metric1 + (1 - self.alpha) * metric2

        # Apply LLM confidence weighting
        final_score = fact.confidence * raw_score

        # Check activation
        activated = final_score >= self.threshold

        details = self._get_details(fact, context, metric1, metric2)

        return VerificationResult(
            module_name=self.module_name,
            module_id=self.module_id,
            metric1_score=metric1,
            metric2_score=metric2,
            final_score=final_score,
            activated=activated,
            details=details,
            cost_ms=self.cost_ms,
            cost_usd=self.cost_usd
        )

    def _compute_metric1(self, fact: Fact, context: Dict) -> float:
        """Compute first metric - to be overridden"""
        raise NotImplementedError

    def _compute_metric2(self, fact: Fact, context: Dict) -> float:
        """Compute second metric - to be overridden"""
        raise NotImplementedError

    def _get_details(self, fact: Fact, context: Dict,
                    metric1: float, metric2: float) -> Dict:
        """Get detailed explanation - to be overridden"""
        return {}


class LOV_Module(VerificationModule):
    """
    M1: Lexical-Ontological Verification
    Target: Semantic Drift (Definition 3)
    """

    def __init__(self, ontology: DomainOntology, **kwargs):
        super().__init__(
            module_id="M1",
            module_name="Lexical-Ontological Verification (LOV)",
            cost_ms=5,
            cost_usd=0.0008,
            **kwargs
        )
        self.ontology = ontology

    def _compute_metric1(self, fact: Fact, context: Dict) -> float:
        """
        Structural Compliance: Verify entity classes and relation types
        Metric_1^LOV = 1/3[𝟙(type(s) ∈ C) + 𝟙(type(o) ∈ C) + 𝟙(r ∈ R_o)]
        """
        scores = []

        # Check subject class
        scores.append(1.0 if fact.subject.entity_class in self.ontology.classes else 0.0)

        # Check object class
        scores.append(1.0 if fact.object.entity_class in self.ontology.classes else 0.0)

        # Check relation type
        scores.append(1.0 if fact.relation in self.ontology.relations else 0.0)

        return sum(scores) / 3.0

    def _compute_metric2(self, fact: Fact, context: Dict) -> float:
        """
        Attribute Compliance: Validate attributes against ontology constraints
        Handles both hard (type, format) and soft (typical ranges) constraints
        """
        if not fact.subject.attributes:
            return 1.0  # No attributes to validate

        total_attrs = len(fact.subject.attributes)
        if total_attrs == 0:
            return 1.0

        valid_attrs = self.ontology.attributes.get(fact.subject.entity_class, [])

        score_sum = 0.0
        for attr_name, attr_value in fact.subject.attributes.items():
            # Hard constraint: attribute must be in valid list
            hard_score = 1.0 if attr_name in valid_attrs else 0.0

            # Soft constraint: check if value is in typical range
            # For demo, we use simple heuristics
            soft_score = 1.0  # Assume valid for demo

            score_sum += (hard_score + 0.5 * soft_score)

        # Normalize by max possible score (1.5 per attribute)
        return score_sum / (1.5 * total_attrs)

    def _get_details(self, fact: Fact, context: Dict,
                    metric1: float, metric2: float) -> Dict:
        return {
            "subject_valid": fact.subject.entity_class in self.ontology.classes,
            "object_valid": fact.object.entity_class in self.ontology.classes,
            "relation_valid": fact.relation in self.ontology.relations,
            "triple_valid": self.ontology.is_valid_triple(
                fact.subject.entity_class,
                fact.relation,
                fact.object.entity_class
            )
        }


class POV_Module(VerificationModule):
    """
    M2: Protocol-Ontology Verification
    Target: Content Hallucination (Definition 1)
    """

    def __init__(self, standard_terms: List[str], **kwargs):
        super().__init__(
            module_id="M2",
            module_name="Protocol-Ontology Verification (POV)",
            cost_ms=15,
            cost_usd=0.0012,
            **kwargs
        )
        self.standard_terms = set(standard_terms)

    def _compute_metric1(self, fact: Fact, context: Dict) -> float:
        """
        Standard Terminology Match
        Metric_1^POV = 1/|T_d| Σ 𝟙(t ∈ T_std)
        """
        # Extract terms from fact
        terms = [
            fact.subject.id,
            fact.relation.value,
            fact.object.id
        ]

        if not terms:
            return 1.0

        matching_terms = sum(1 for t in terms if t in self.standard_terms)
        return matching_terms / len(terms)

    def _compute_metric2(self, fact: Fact, context: Dict) -> float:
        """
        Cross-Standard Consistency
        Check if terms have consistent meanings across standards
        """
        # For demo: simplified consistency check
        # In production, would check multiple standard databases

        # Simulate consistency score based on term recognition
        terms = [fact.subject.id, fact.relation.value, fact.object.id]
        recognized = sum(1 for t in terms if t in self.standard_terms)

        if len(terms) == 0:
            return 1.0

        # High consistency if most terms are recognized
        consistency = recognized / len(terms)
        return consistency

    def _get_details(self, fact: Fact, context: Dict,
                    metric1: float, metric2: float) -> Dict:
        terms = [fact.subject.id, fact.relation.value, fact.object.id]
        return {
            "terms_checked": terms,
            "standard_matches": [t for t in terms if t in self.standard_terms],
            "non_standard": [t for t in terms if t not in self.standard_terms]
        }


class MAV_Module(VerificationModule):
    """
    M3: Motion-Aware Verification
    Target: Spatiotemporal Inconsistency (Definition 2)
    MOST CRITICAL MODULE - catches physics violations
    """

    def __init__(self, existing_facts: List[Fact], max_velocity: float = 5.0, **kwargs):
        super().__init__(
            module_id="M3",
            module_name="Motion-Aware Verification (MAV)",
            cost_ms=50,
            cost_usd=0.0018,
            **kwargs
        )
        self.existing_facts = existing_facts
        self.max_velocity = max_velocity

    def _compute_metric1(self, fact: Fact, context: Dict) -> float:
        """
        Temporal-Spatial Validity: Check ψ_s and ψ_t
        Metric_1^MAV = (ψ_s(d_k) + ψ_t(d_k)) / 2
        """
        spatial_score = self._check_spatial_consistency(fact)
        temporal_score = self._check_temporal_consistency(fact)

        return (spatial_score + temporal_score) / 2.0

    def _check_spatial_consistency(self, fact: Fact) -> float:
        """
        Check no entity at two separated locations at same time
        ψ_s(d) = 1 iff ∄d': same_entity ∧ |t_d - t_d'| < τ_res ∧ dist > σ_res
        """
        tau_res = 1.0  # seconds
        sigma_res = 0.1  # meters

        for other_fact in self.existing_facts:
            if fact.subject.id != other_fact.subject.id:
                continue

            time_diff = fact.coordinate.time_diff(other_fact.coordinate)
            if time_diff >= tau_res:
                continue

            distance = fact.coordinate.distance_to(other_fact.coordinate)
            if distance > sigma_res:
                return 0.0  # Violation detected

        return 1.0

    def _check_temporal_consistency(self, fact: Fact) -> float:
        """
        Check temporal causality and travel time
        ψ_t(d) = 1 iff t2 > t1 ∧ (t2 - t1) ≥ travel_time(ℓ1, ℓ2)
        """
        # Find previous fact for same entity
        previous_fact = None
        for f in sorted(self.existing_facts,
                       key=lambda x: x.coordinate.t,
                       reverse=True):
            if f.subject.id == fact.subject.id:
                previous_fact = f
                break

        if previous_fact is None:
            return 1.0  # No previous state to check

        # Check time ordering
        if fact.coordinate.t <= previous_fact.coordinate.t:
            return 0.0  # Temporal violation

        return 1.0

    def _compute_metric2(self, fact: Fact, context: Dict) -> float:
        """
        Physical Feasibility: Check velocity constraints
        If v_req > v_max, return exp(-(v_req - v_max)/v_max)
        """
        # Find previous fact for same entity
        previous_fact = None
        for f in sorted(self.existing_facts,
                       key=lambda x: x.coordinate.t,
                       reverse=True):
            if f.subject.id == fact.subject.id:
                previous_fact = f
                break

        if previous_fact is None:
            return 1.0  # No previous state

        delta_d = fact.coordinate.distance_to(previous_fact.coordinate)
        delta_t = fact.coordinate.time_diff(previous_fact.coordinate)

        if delta_t <= 0:
            return 0.0  # Temporal violation

        v_required = delta_d / delta_t

        if v_required <= self.max_velocity:
            return 1.0

        # Exponential penalty for exceeding max velocity
        return np.exp(-(v_required - self.max_velocity) / self.max_velocity)

    def _get_details(self, fact: Fact, context: Dict,
                    metric1: float, metric2: float) -> Dict:
        # Find previous fact
        previous_fact = None
        for f in sorted(self.existing_facts,
                       key=lambda x: x.coordinate.t,
                       reverse=True):
            if f.subject.id == fact.subject.id:
                previous_fact = f
                break

        details = {
            "spatial_consistent": self._check_spatial_consistency(fact) == 1.0,
            "temporal_consistent": self._check_temporal_consistency(fact) == 1.0
        }

        if previous_fact:
            delta_d = fact.coordinate.distance_to(previous_fact.coordinate)
            delta_t = fact.coordinate.time_diff(previous_fact.coordinate)
            v_req = delta_d / delta_t if delta_t > 0 else float('inf')

            details.update({
                "distance_m": delta_d,
                "time_s": delta_t,
                "required_velocity_ms": v_req,
                "max_velocity_ms": self.max_velocity,
                "velocity_feasible": v_req <= self.max_velocity
            })

        return details


class WSV_Module(VerificationModule):
    """
    M4: Web-Source Verification
    Target: Content Hallucination (Definition 1)
    """

    def __init__(self, **kwargs):
        super().__init__(
            module_id="M4",
            module_name="Web-Source Verification (WSV)",
            cost_ms=120,
            cost_usd=0.0006,
            **kwargs
        )

    def _compute_metric1(self, fact: Fact, context: Dict) -> float:
        """
        Source Credibility: Weighted average of semantic similarity
        Metric_1^WSV = Σ(w_cred,i · sim(d_k, result_i)) / Σw_cred,i
        """
        # For demo: simulate web search results
        # In production, would query actual external sources

        # Simulate credibility scores based on fact confidence
        simulated_similarity = min(fact.confidence + np.random.uniform(-0.1, 0.1), 1.0)
        return max(0.0, simulated_similarity)

    def _compute_metric2(self, fact: Fact, context: Dict) -> float:
        """
        Cross-Source Agreement: Measure consistency across sources
        Metric_2^WSV = 1 / (1 + CV(sim_scores))
        """
        # Simulate coefficient of variation
        # Low CV = high agreement
        simulated_cv = np.random.uniform(0.1, 0.5)

        return 1.0 / (1.0 + simulated_cv)

    def _get_details(self, fact: Fact, context: Dict,
                    metric1: float, metric2: float) -> Dict:
        return {
            "sources_queried": 5,
            "avg_similarity": metric1,
            "cross_source_agreement": metric2,
            "note": "Demo mode: actual web queries not performed"
        }


class ESV_Module(VerificationModule):
    """
    M5: Embedding Similarity Verification
    Target: Semantic Drift + Hallucination
    """

    def __init__(self, historical_facts: List[Fact], **kwargs):
        super().__init__(
            module_id="M5",
            module_name="Embedding Similarity Verification (ESV)",
            cost_ms=800,
            cost_usd=0.0003,
            **kwargs
        )
        self.historical_facts = historical_facts

    def _compute_metric1(self, fact: Fact, context: Dict) -> float:
        """
        Nearest Neighbor Similarity
        Metric_1^ESV = 1/K Σ (1 + cos(e_k, e_ni)) / 2
        """
        # For demo: simulate embedding similarity
        # In production, would use actual sentence-transformers

        # Simulate K=3 nearest neighbors
        K = 3
        simulated_similarities = [
            np.random.uniform(0.7, 0.95) for _ in range(K)
        ]

        # Normalize cosine similarity from [-1,1] to [0,1]
        normalized = [(1 + sim) / 2 for sim in simulated_similarities]

        return sum(normalized) / K

    def _compute_metric2(self, fact: Fact, context: Dict) -> float:
        """
        Cluster Membership: GMM probability
        Metric_2^ESV = max P(c | e_k)
        """
        # Simulate GMM cluster membership probability
        simulated_prob = np.random.uniform(0.6, 0.9)

        return simulated_prob

    def _get_details(self, fact: Fact, context: Dict,
                    metric1: float, metric2: float) -> Dict:
        return {
            "nn_similarity": metric1,
            "cluster_probability": metric2,
            "nearest_neighbors": 3,
            "note": "Demo mode: using simulated embeddings"
        }
