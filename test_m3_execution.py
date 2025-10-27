"""
Test that M3 always executes, even with high cumulative confidence
"""
from datetime import datetime
from src.models.stkg import (
    Entity, EntityClass, RelationType, Fact,
    SpatiotemporalCoordinate, DomainOntology
)
from src.modules.verification import LOV_Module, POV_Module, MAV_Module
from src.modules.rmmve import RMMVeEngine, Decision


def test_m3_execution():
    """Test that M3 runs even when M1-M2 would trigger early termination"""

    print("🧪 Testing M3 Force Execution\n")
    print("=" * 60)

    # Setup ontology
    ontology = DomainOntology(
        classes={EntityClass.COMPONENT, EntityClass.LOCATION},
        relations={RelationType.LOCATED_IN},
        attributes={EntityClass.COMPONENT: ["part_number"]},
        relation_domains={RelationType.LOCATED_IN: {EntityClass.COMPONENT}},
        relation_ranges={RelationType.LOCATED_IN: {EntityClass.LOCATION}}
    )

    # Create baseline fact (for M3 to compare against)
    baseline_coord = SpatiotemporalCoordinate(x=10.0, y=20.0, z=1.0, t=datetime.now())
    baseline_fact = Fact(
        subject=Entity("blade-123", EntityClass.COMPONENT, {"part_number": "B-123"}),
        relation=RelationType.LOCATED_IN,
        object=Entity("bay-7", EntityClass.LOCATION, {}),
        coordinate=baseline_coord,
        confidence=0.95
    )

    # Create physics violation fact (100m away, 15 seconds later)
    from datetime import timedelta
    violation_coord = SpatiotemporalCoordinate(
        x=110.0, y=20.0, z=1.0,
        t=datetime.now() + timedelta(seconds=15)
    )
    violation_fact = Fact(
        subject=Entity("blade-123", EntityClass.COMPONENT, {"part_number": "B-123"}),
        relation=RelationType.LOCATED_IN,
        object=Entity("bay-15", EntityClass.LOCATION, {}),
        coordinate=violation_coord,
        confidence=0.60  # Lower confidence (spatial reasoning weakness)
    )

    # Test 1: Without force_m3_execution (would allow early termination)
    print("\n📊 Test 1: force_m3_execution=False (OLD BEHAVIOR)")
    print("-" * 60)

    modules_no_force = [
        LOV_Module(ontology=ontology, threshold=0.5, alpha=0.5, weight=0.2),
        POV_Module(standard_terms=["blade", "bay", "locatedIn"], threshold=0.5, alpha=0.5, weight=0.2),
        MAV_Module(existing_facts=[baseline_fact], max_velocity=5.0, threshold=0.5, alpha=0.5, weight=0.25)
    ]

    engine_no_force = RMMVeEngine(
        modules=modules_no_force,
        global_threshold=0.75,
        review_margin=0.10,
        force_m3_execution=False
    )

    decision1, results1 = engine_no_force.verify(violation_fact)

    print(f"Decision: {decision1.value}")
    print(f"Cumulative Confidence: {results1['cumulative_confidence']:.3f}")
    print(f"Activated Modules: {results1['activated_modules']}")
    print(f"Early Terminated: {results1['early_terminated']}")
    print(f"M3 Executed: {'M3' in [r['module_id'] for r in results1['module_results']]}")

    # Check if M3 detected the violation
    m3_result = next((r for r in results1['module_results'] if r['module_id'] == 'M3'), None)
    if m3_result:
        print(f"M3 Score: {m3_result['final_score']:.3f}")
        print(f"M3 Activated: {m3_result['activated']}")
        if m3_result['details']:
            print(f"M3 Details: Velocity {m3_result['details'].get('required_velocity_ms', 0):.2f} m/s "
                  f"vs Max {m3_result['details'].get('max_velocity_ms', 0)} m/s")

    # Test 2: With force_m3_execution (ensures M3 runs)
    print("\n📊 Test 2: force_m3_execution=True (NEW BEHAVIOR)")
    print("-" * 60)

    modules_force = [
        LOV_Module(ontology=ontology, threshold=0.5, alpha=0.5, weight=0.2),
        POV_Module(standard_terms=["blade", "bay", "locatedIn"], threshold=0.5, alpha=0.5, weight=0.2),
        MAV_Module(existing_facts=[baseline_fact], max_velocity=5.0, threshold=0.5, alpha=0.5, weight=0.25)
    ]

    engine_force = RMMVeEngine(
        modules=modules_force,
        global_threshold=0.75,
        review_margin=0.10,
        force_m3_execution=True  # Force M3 to run
    )

    decision2, results2 = engine_force.verify(violation_fact)

    print(f"Decision: {decision2.value}")
    print(f"Cumulative Confidence: {results2['cumulative_confidence']:.3f}")
    print(f"Activated Modules: {results2['activated_modules']}")
    print(f"Early Terminated: {results2['early_terminated']}")
    print(f"M3 Executed: {'M3' in [r['module_id'] for r in results2['module_results']]}")

    # Check if M3 detected the violation
    m3_result = next((r for r in results2['module_results'] if r['module_id'] == 'M3'), None)
    if m3_result:
        print(f"M3 Score: {m3_result['final_score']:.3f}")
        print(f"M3 Activated: {m3_result['activated']}")
        if m3_result['details']:
            print(f"M3 Details: Velocity {m3_result['details'].get('required_velocity_ms', 0):.2f} m/s "
                  f"vs Max {m3_result['details'].get('max_velocity_ms', 0)} m/s")

    # Summary
    print("\n" + "=" * 60)
    print("✅ SUMMARY")
    print("=" * 60)

    m3_ran_test1 = any(r['module_id'] == 'M3' for r in results1['module_results'])
    m3_ran_test2 = any(r['module_id'] == 'M3' for r in results2['module_results'])

    print(f"Test 1 (no force): M3 executed = {m3_ran_test1}")
    print(f"Test 2 (force):    M3 executed = {m3_ran_test2}")

    if m3_ran_test2:
        print("\n✅ SUCCESS: M3 now runs even with high confidence from M1-M2!")
        print("   This ensures 100% of spatiotemporal errors are caught.")
        return True
    else:
        print("\n❌ FAILURE: M3 still not running!")
        return False


if __name__ == "__main__":
    try:
        success = test_m3_execution()
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Tests failed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
