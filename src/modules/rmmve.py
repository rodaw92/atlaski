"""
Ranked Multi-Modal Verification Engine (RMMVe)
Implements Algorithm 1 from the paper
"""
from typing import List, Dict, Tuple
from enum import Enum
from src.models.stkg import Fact
from src.modules.verification import (
    VerificationModule, VerificationResult,
    LOV_Module, POV_Module, MAV_Module, WSV_Module, ESV_Module
)


class Decision(Enum):
    """Verification decision"""
    ACCEPT = "Accept"
    REJECT = "Reject"
    REVIEW = "Review"


class RMMVeEngine:
    """
    Ranked Multi-Modal Verification Engine
    Executes modules sequentially with early termination
    """

    def __init__(self, modules: List[VerificationModule],
                 global_threshold: float = 0.75,
                 review_margin: float = 0.10):
        """
        Args:
            modules: List of verification modules (M1-M5)
            global_threshold: Θ for accept/reject decision
            review_margin: ε for review margin
        """
        self.modules = modules
        self.global_threshold = global_threshold
        self.review_margin = review_margin

    def verify(self, fact: Fact, context: Dict = None) -> Tuple[Decision, Dict]:
        """
        Verify a candidate fact using RMMVe
        Returns: (decision, detailed_results)

        Implements Algorithm 1:
        1. Execute modules sequentially
        2. Check activation threshold for each module
        3. Compute cumulative confidence after each activation
        4. Early termination if C >= Θ
        5. Final decision based on C and ε
        """
        if context is None:
            context = {}

        activated_modules = []
        module_results = []
        total_weight = 0.0
        cumulative_confidence = 0.0
        early_terminated = False
        termination_module = None

        # Sequential module execution
        for module in self.modules:
            # Compute module score
            result = module.compute_score(fact, context)
            module_results.append(result)

            # Check activation
            if result.activated:
                activated_modules.append(module)
                total_weight += module.weight

                # Update cumulative confidence (Equation 7)
                weighted_sum = sum(m.weight * r.final_score
                                  for m, r in zip(activated_modules, module_results)
                                  if r.activated)
                cumulative_confidence = weighted_sum / total_weight

                # Early termination check
                if cumulative_confidence >= self.global_threshold:
                    early_terminated = True
                    termination_module = module.module_id
                    decision = Decision.ACCEPT
                    break

        # If no early termination, make final decision (Equation 8)
        if not early_terminated:
            if cumulative_confidence >= self.global_threshold:
                decision = Decision.ACCEPT
            elif cumulative_confidence >= (self.global_threshold - self.review_margin):
                decision = Decision.REVIEW
            else:
                decision = Decision.REJECT

        # Compile detailed results
        detailed_results = {
            "decision": decision.value,
            "cumulative_confidence": cumulative_confidence,
            "global_threshold": self.global_threshold,
            "review_margin": self.review_margin,
            "activated_modules": [m.module_id for m in activated_modules],
            "early_terminated": early_terminated,
            "termination_module": termination_module,
            "module_results": [
                {
                    "module_id": r.module_id,
                    "module_name": r.module_name,
                    "metric1": r.metric1_score,
                    "metric2": r.metric2_score,
                    "final_score": r.final_score,
                    "activated": r.activated,
                    "details": r.details,
                    "cost_ms": r.cost_ms,
                    "cost_usd": r.cost_usd
                }
                for r in module_results
            ],
            "total_latency_ms": sum(r.cost_ms for r in module_results),
            "total_cost_usd": sum(r.cost_usd for r in module_results)
        }

        return decision, detailed_results

    def batch_verify(self, facts: List[Fact],
                    context: Dict = None) -> List[Tuple[Fact, Decision, Dict]]:
        """Verify multiple facts"""
        results = []
        for fact in facts:
            decision, details = self.verify(fact, context)
            results.append((fact, decision, details))
        return results

    def get_statistics(self, results: List[Tuple[Fact, Decision, Dict]]) -> Dict:
        """Compute statistics from verification results"""
        total = len(results)
        if total == 0:
            return {}

        accepted = sum(1 for _, d, _ in results if d == Decision.ACCEPT)
        rejected = sum(1 for _, d, _ in results if d == Decision.REJECT)
        review = sum(1 for _, d, _ in results if d == Decision.REVIEW)

        early_terminated = sum(1 for _, _, details in results
                              if details["early_terminated"])

        avg_confidence = sum(details["cumulative_confidence"]
                           for _, _, details in results) / total

        avg_latency = sum(details["total_latency_ms"]
                         for _, _, details in results) / total

        total_cost = sum(details["total_cost_usd"]
                        for _, _, details in results)

        # Module activation rates
        module_activations = {}
        for _, _, details in results:
            for mod in details["activated_modules"]:
                module_activations[mod] = module_activations.get(mod, 0) + 1

        return {
            "total_facts": total,
            "accepted": accepted,
            "rejected": rejected,
            "review": review,
            "acceptance_rate": accepted / total,
            "rejection_rate": rejected / total,
            "review_rate": review / total,
            "early_termination_rate": early_terminated / total,
            "avg_confidence": avg_confidence,
            "avg_latency_ms": avg_latency,
            "total_cost_usd": total_cost,
            "cost_per_fact_usd": total_cost / total,
            "module_activation_rates": {
                mod: count / total
                for mod, count in module_activations.items()
            }
        }
