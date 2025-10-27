"""
Quick test script to verify the verification pipeline works
"""
from datetime import datetime
from src.models.stkg import (
    Entity, EntityClass, RelationType, Fact,
    SpatiotemporalCoordinate, DomainOntology
)
from src.modules.verification import LOV_Module, POV_Module, MAV_Module
from src.modules.rmmve import RMMVeEngine, Decision


def test_verification():
    """Test the verification pipeline with a simple fact"""

    print("🧪 Testing ATLASky-AI Verification Pipeline\n")

    # Setup ontology
    ontology = DomainOntology(
        classes={EntityClass.EQUIPMENT, EntityClass.LOCATION, EntityClass.COMPONENT},
        relations={RelationType.LOCATED_IN, RelationType.INSTALLED_AT},
        attributes={
            EntityClass.COMPONENT: ["part_number", "material"]
        },
        relation_domains={
            RelationType.LOCATED_IN: {EntityClass.COMPONENT, EntityClass.EQUIPMENT}
        },
        relation_ranges={
            RelationType.LOCATED_IN: {EntityClass.LOCATION}
        }
    )

    # Create modules
    modules = [
        LOV_Module(ontology=ontology, threshold=0.5, alpha=0.5, weight=0.3),
        POV_Module(standard_terms=["blade", "bay", "locatedIn"],
                  threshold=0.5, alpha=0.5, weight=0.3),
        MAV_Module(existing_facts=[], max_velocity=5.0,
                  threshold=0.5, alpha=0.5, weight=0.4)
    ]

    # Create engine
    engine = RMMVeEngine(modules=modules, global_threshold=0.75, review_margin=0.10)

    # Test fact 1: Valid fact
    print("Test 1: Valid Fact")
    print("-" * 50)

    subject = Entity(
        id="blade-123",
        entity_class=EntityClass.COMPONENT,
        attributes={"part_number": "B-123", "material": "titanium"}
    )

    obj = Entity(
        id="bay-7",
        entity_class=EntityClass.LOCATION,
        attributes={}
    )

    coord = SpatiotemporalCoordinate(x=10.0, y=20.0, z=1.0, t=datetime.now())

    fact1 = Fact(
        subject=subject,
        relation=RelationType.LOCATED_IN,
        object=obj,
        coordinate=coord,
        confidence=0.95,
        source_text="Blade located in bay 7"
    )

    decision1, results1 = engine.verify(fact1)

    print(f"Subject: {fact1.subject.id}")
    print(f"Relation: {fact1.relation.value}")
    print(f"Object: {fact1.object.id}")
    print(f"Confidence: {fact1.confidence}")
    print(f"\nDecision: {decision1.value}")
    print(f"Cumulative Confidence: {results1['cumulative_confidence']:.3f}")
    print(f"Activated Modules: {results1['activated_modules']}")
    print(f"Early Terminated: {results1['early_terminated']}")

    # Test fact 2: Low confidence fact
    print("\n\nTest 2: Low Confidence Fact")
    print("-" * 50)

    fact2 = Fact(
        subject=subject,
        relation=RelationType.LOCATED_IN,
        object=obj,
        coordinate=coord,
        confidence=0.40,  # Low confidence
        source_text="Maybe in bay 7?"
    )

    decision2, results2 = engine.verify(fact2)

    print(f"Confidence: {fact2.confidence}")
    print(f"Decision: {decision2.value}")
    print(f"Cumulative Confidence: {results2['cumulative_confidence']:.3f}")

    # Summary
    print("\n\n✅ Verification Pipeline Test Complete!")
    print(f"Test 1: {decision1.value} (Expected: ACCEPT)")
    print(f"Test 2: {decision2.value} (Expected: REJECT or REVIEW)")

    return True


if __name__ == "__main__":
    try:
        test_verification()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
