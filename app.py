"""
ATLASky-AI Demo Interface
Streamlit application for demonstrating the verification framework
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict

# Import our modules
from src.models.stkg import (
    Entity, EntityClass, RelationType, Fact,
    SpatiotemporalCoordinate, DomainOntology, PhysicsConstraints, STKG
)
from src.modules.verification import (
    LOV_Module, POV_Module, MAV_Module, WSV_Module, ESV_Module
)
from src.modules.rmmve import RMMVeEngine, Decision


# Page configuration
st.set_page_config(
    page_title="ATLASky-AI Demo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .accept {
        color: #28a745;
        font-weight: bold;
    }
    .reject {
        color: #dc3545;
        font-weight: bold;
    }
    .review {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_demo_system():
    """Initialize the ATLASky-AI system with demo configuration"""

    # Define domain ontology
    ontology = DomainOntology(
        classes={EntityClass.EQUIPMENT, EntityClass.LOCATION,
                EntityClass.PERSONNEL, EntityClass.EVENT, EntityClass.COMPONENT},
        relations={RelationType.INSTALLED_AT, RelationType.INSPECTED_BY,
                  RelationType.LOCATED_IN, RelationType.PRECEDES,
                  RelationType.MOVED_TO, RelationType.CONTAINS},
        attributes={
            EntityClass.EQUIPMENT: ["serial_number", "model", "status"],
            EntityClass.COMPONENT: ["part_number", "tolerance", "material"],
            EntityClass.LOCATION: ["facility_id", "bay_number", "coordinates"],
            EntityClass.PERSONNEL: ["employee_id", "role", "certification"],
        },
        relation_domains={
            RelationType.INSTALLED_AT: {EntityClass.EQUIPMENT, EntityClass.COMPONENT},
            RelationType.LOCATED_IN: {EntityClass.EQUIPMENT, EntityClass.COMPONENT},
            RelationType.INSPECTED_BY: {EntityClass.EQUIPMENT, EntityClass.COMPONENT},
            RelationType.MOVED_TO: {EntityClass.EQUIPMENT, EntityClass.COMPONENT},
        },
        relation_ranges={
            RelationType.INSTALLED_AT: {EntityClass.LOCATION},
            RelationType.LOCATED_IN: {EntityClass.LOCATION},
            RelationType.INSPECTED_BY: {EntityClass.PERSONNEL},
            RelationType.MOVED_TO: {EntityClass.LOCATION},
        }
    )

    # Standard terminology (simplified for demo)
    standard_terms = [
        "turbine", "blade", "engine", "bay", "inspection",
        "maintenance", "forklift", "manual", "automated",
        "installedAt", "locatedIn", "inspectedBy", "movedTo"
    ]

    # Initialize modules
    existing_facts = []  # Will be populated during demo

    modules = [
        LOV_Module(ontology=ontology, threshold=0.5, alpha=0.5, weight=0.2),
        POV_Module(standard_terms=standard_terms, threshold=0.5, alpha=0.5, weight=0.2),
        MAV_Module(existing_facts=existing_facts, max_velocity=5.0,
                  threshold=0.5, alpha=0.5, weight=0.25),
        WSV_Module(threshold=0.5, alpha=0.5, weight=0.15),
        ESV_Module(historical_facts=existing_facts, threshold=0.5, alpha=0.5, weight=0.2)
    ]

    # Initialize RMMVe engine
    engine = RMMVeEngine(
        modules=modules,
        global_threshold=0.75,
        review_margin=0.10
    )

    # Initialize STKG
    physics = PhysicsConstraints(max_velocity=5.0, temporal_resolution=1.0, spatial_resolution=0.1)
    stkg = STKG(ontology=ontology, physics=physics)

    return engine, stkg, ontology, modules


def create_sample_facts() -> List[Dict]:
    """Create sample facts for demonstration"""
    base_time = datetime.now()

    samples = [
        {
            "subject": "TurbineBlade-SN789",
            "subject_class": EntityClass.COMPONENT,
            "relation": RelationType.LOCATED_IN,
            "object": "MaintenanceBay-7",
            "object_class": EntityClass.LOCATION,
            "x": 12.3, "y": 4.5, "z": 1.2,
            "time": base_time,
            "confidence": 0.95,
            "source": "Inspection log entry: Turbine blade SN-789 currently located in maintenance bay 7 for routine inspection.",
            "attributes": {"part_number": "TB-789", "material": "titanium"},
            "expected": "ACCEPT",
            "description": "Valid fact with high confidence, proper ontology compliance"
        },
        {
            "subject": "TurbineBlade-SN789",
            "subject_class": EntityClass.COMPONENT,
            "relation": RelationType.LOCATED_IN,
            "object": "MaintenanceBay-12",
            "object_class": EntityClass.LOCATION,
            "x": 45.8, "y": 12.1, "z": 1.2,
            "time": base_time + timedelta(seconds=30),
            "confidence": 0.70,
            "source": "Transfer note: Blade moved to bay 12 for final assembly.",
            "attributes": {"part_number": "TB-789", "material": "titanium"},
            "expected": "REJECT",
            "description": "Physics violation: 50m distance in 30s requires 1.67 m/s (acceptable), but from Bay 7"
        },
        {
            "subject": "Engine-X250",
            "subject_class": EntityClass.EQUIPMENT,
            "relation": RelationType.INSPECTED_BY,
            "object": "Inspector-042",
            "object_class": EntityClass.PERSONNEL,
            "x": 20.0, "y": 15.0, "z": 2.0,
            "time": base_time + timedelta(hours=1),
            "confidence": 0.88,
            "source": "Quality report: Engine X250 inspected by certified inspector 042.",
            "attributes": {"serial_number": "ENG-X250", "status": "operational"},
            "expected": "ACCEPT",
            "description": "Valid inspection record with good confidence"
        },
        {
            "subject": "Component-INVALID",
            "subject_class": EntityClass.COMPONENT,
            "relation": RelationType.LOCATED_IN,
            "object": "UnknownLocation-999",
            "object_class": EntityClass.LOCATION,
            "x": 0.0, "y": 0.0, "z": 0.0,
            "time": base_time,
            "confidence": 0.45,
            "source": "Unstructured note: Component might be somewhere in facility",
            "attributes": {},
            "expected": "REJECT",
            "description": "Low confidence, vague information, likely hallucination"
        },
        {
            "subject": "TurbineBlade-SN789",
            "subject_class": EntityClass.COMPONENT,
            "relation": RelationType.LOCATED_IN,
            "object": "AssemblyBay-3",
            "object_class": EntityClass.LOCATION,
            "x": 100.0, "y": 50.0, "z": 1.5,
            "time": base_time + timedelta(seconds=45),
            "confidence": 0.75,
            "source": "Assembly log: Blade installed in assembly bay 3",
            "attributes": {"part_number": "TB-789", "material": "titanium"},
            "expected": "REJECT",
            "description": "CRITICAL: Physics violation - 100m+ distance in 45s from bay 7 requires >2.2 m/s (exceeds limits)"
        },
    ]

    return samples


def fact_dict_to_object(fact_dict: Dict) -> Fact:
    """Convert fact dictionary to Fact object"""
    subject = Entity(
        id=fact_dict["subject"],
        entity_class=fact_dict["subject_class"],
        attributes=fact_dict.get("attributes", {}),
        version=1
    )

    obj = Entity(
        id=fact_dict["object"],
        entity_class=fact_dict["object_class"],
        attributes={},
        version=1
    )

    coord = SpatiotemporalCoordinate(
        x=fact_dict["x"],
        y=fact_dict["y"],
        z=fact_dict["z"],
        t=fact_dict["time"]
    )

    return Fact(
        subject=subject,
        relation=fact_dict["relation"],
        object=obj,
        coordinate=coord,
        confidence=fact_dict["confidence"],
        source_text=fact_dict.get("source", "")
    )


def main():
    """Main application"""

    # Header
    st.markdown('<div class="main-header">🛡️ ATLASky-AI Demonstration</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Defense-in-Depth Verification for 4D Spatiotemporal Knowledge Graphs</div>',
        unsafe_allow_html=True
    )

    # Initialize system
    if 'engine' not in st.session_state:
        st.session_state.engine, st.session_state.stkg, \
        st.session_state.ontology, st.session_state.modules = initialize_demo_system()
        st.session_state.existing_facts = []

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Demo",
        ["Overview", "Single Fact Verification", "Batch Processing",
         "Module Deep Dive", "Performance Metrics"]
    )

    if page == "Overview":
        show_overview()
    elif page == "Single Fact Verification":
        show_single_verification()
    elif page == "Batch Processing":
        show_batch_processing()
    elif page == "Module Deep Dive":
        show_module_deep_dive()
    elif page == "Performance Metrics":
        show_performance_metrics()


def show_overview():
    """Show system overview"""
    st.header("System Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Architecture")
        st.markdown("""
        **ATLASky-AI** implements a three-stage verification pipeline:

        **Stage 1: Data Preprocessing**
        - Normalizes heterogeneous raw data
        - Temporal alignment and spatial validation
        - Schema standardization

        **Stage 2: LLM-Based Extraction**
        - Domain-specialized prompts
        - Structured fact extraction
        - Confidence-weighted output

        **Stage 3: TruthFlow Verification**
        - Five specialized modules (M1-M5)
        - Early termination for efficiency
        - Adaptive parameter tuning (AAIC)
        """)

    with col2:
        st.subheader("Verification Modules")

        modules_info = [
            ("M1", "LOV", "Lexical-Ontological", "Semantic Drift", 5, "ms"),
            ("M2", "POV", "Protocol-Ontology", "Hallucination", 15, "ms"),
            ("M3", "MAV", "Motion-Aware", "ST-Inconsistency", 50, "ms"),
            ("M4", "WSV", "Web-Source", "Hallucination", 120, "ms"),
            ("M5", "ESV", "Embedding Similarity", "Drift + Hallucination", 800, "ms"),
        ]

        df = pd.DataFrame(modules_info,
                         columns=["ID", "Code", "Name", "Target", "Latency", "Unit"])
        st.dataframe(df, use_container_width=True)

    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precision", "94%", "")
    col2.metric("Recall", "93%", "")
    col3.metric("FPR Reduction", "39-57%", "vs baselines")
    col4.metric("Early Term.", "40%", "efficiency gain")

    st.info("""
    **Demo Features:**
    - ✅ Single fact verification with detailed module breakdowns
    - ✅ Batch processing with statistics
    - ✅ Module-by-module deep dive
    - ✅ Performance visualization
    """)


def show_single_verification():
    """Show single fact verification interface"""
    st.header("Single Fact Verification")

    st.markdown("Select a sample fact or create your own to see the verification process.")

    # Sample facts
    samples = create_sample_facts()

    # Fact selection
    col1, col2 = st.columns([1, 1])

    with col1:
        fact_idx = st.selectbox(
            "Select Sample Fact",
            range(len(samples)),
            format_func=lambda i: f"Fact {i+1}: {samples[i]['description'][:50]}..."
        )

    selected_sample = samples[fact_idx]

    # Display fact details
    st.subheader("Candidate Fact")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Fact Triple:**")
        st.code(f"<{selected_sample['subject']}, {selected_sample['relation'].value}, {selected_sample['object']}>")

        st.markdown("**Spatiotemporal Coordinates:**")
        st.json({
            "x": selected_sample['x'],
            "y": selected_sample['y'],
            "z": selected_sample['z'],
            "time": selected_sample['time'].isoformat()
        })

    with col2:
        st.markdown("**Source Text:**")
        st.text_area("", selected_sample['source'], height=100, disabled=True)

        st.markdown(f"**LLM Confidence:** {selected_sample['confidence']:.2f}")
        st.markdown(f"**Expected Decision:** {selected_sample['expected']}")

    # Run verification
    if st.button("🔍 Run Verification", type="primary"):
        with st.spinner("Running verification pipeline..."):
            # Convert to Fact object
            fact = fact_dict_to_object(selected_sample)

            # Update module context with existing facts
            for module in st.session_state.modules:
                if hasattr(module, 'existing_facts'):
                    module.existing_facts = st.session_state.existing_facts

            # Run verification
            decision, results = st.session_state.engine.verify(fact)

            # Display results
            st.divider()
            st.subheader("Verification Results")

            # Decision
            decision_color = "accept" if decision == Decision.ACCEPT else \
                           "reject" if decision == Decision.REJECT else "review"

            st.markdown(
                f'<h2 class="{decision_color}">Decision: {decision.value}</h2>',
                unsafe_allow_html=True
            )

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Cumulative Confidence", f"{results['cumulative_confidence']:.3f}")
            col2.metric("Threshold", f"{results['global_threshold']:.2f}")
            col3.metric("Modules Activated", len(results['activated_modules']))
            col4.metric("Early Terminated", "Yes" if results['early_terminated'] else "No")

            # Module results
            st.subheader("Module Breakdown")

            for mod_result in results['module_results']:
                with st.expander(
                    f"{mod_result['module_id']}: {mod_result['module_name']} - "
                    f"Score: {mod_result['final_score']:.3f} "
                    f"{'✅ Activated' if mod_result['activated'] else '❌ Not Activated'}"
                ):
                    col1, col2, col3 = st.columns(3)

                    col1.metric("Metric 1", f"{mod_result['metric1']:.3f}")
                    col2.metric("Metric 2", f"{mod_result['metric2']:.3f}")
                    col3.metric("Final Score", f"{mod_result['final_score']:.3f}")

                    st.markdown("**Details:**")
                    st.json(mod_result['details'])

                    col1, col2 = st.columns(2)
                    col1.metric("Latency", f"{mod_result['cost_ms']:.1f} ms")
                    col2.metric("Cost", f"${mod_result['cost_usd']:.6f}")

            # Visualization
            st.subheader("Score Progression")

            module_names = [r['module_id'] for r in results['module_results']]
            scores = [r['final_score'] for r in results['module_results']]
            activated = [r['activated'] for r in results['module_results']]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=module_names,
                y=scores,
                marker_color=['green' if a else 'lightgray' for a in activated],
                text=[f"{s:.3f}" for s in scores],
                textposition='outside'
            ))

            fig.add_hline(y=results['global_threshold'],
                         line_dash="dash", line_color="red",
                         annotation_text="Global Threshold")

            fig.update_layout(
                title="Module Scores and Activation",
                xaxis_title="Module",
                yaxis_title="Score",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Add to existing facts if accepted
            if decision == Decision.ACCEPT:
                st.session_state.existing_facts.append(fact)
                st.success(f"Fact added to knowledge graph! Total facts: {len(st.session_state.existing_facts)}")


def show_batch_processing():
    """Show batch processing interface"""
    st.header("Batch Processing")

    st.markdown("Process multiple facts simultaneously and analyze aggregate statistics.")

    # Load sample facts
    samples = create_sample_facts()

    st.subheader(f"Sample Dataset ({len(samples)} facts)")

    # Display sample facts
    df_samples = pd.DataFrame([
        {
            "Subject": s["subject"],
            "Relation": s["relation"].value,
            "Object": s["object"],
            "Confidence": f"{s['confidence']:.2f}",
            "Expected": s["expected"]
        }
        for s in samples
    ])
    st.dataframe(df_samples, use_container_width=True)

    if st.button("🚀 Process Batch", type="primary"):
        with st.spinner("Processing batch..."):
            # Convert to Fact objects
            facts = [fact_dict_to_object(s) for s in samples]

            # Update module context
            for module in st.session_state.modules:
                if hasattr(module, 'existing_facts'):
                    module.existing_facts = st.session_state.existing_facts

            # Process batch
            results = st.session_state.engine.batch_verify(facts)

            # Get statistics
            stats = st.session_state.engine.get_statistics(results)

            # Display results
            st.divider()
            st.subheader("Batch Results")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Facts", stats['total_facts'])
            col2.metric("Accepted", stats['accepted'], f"{stats['acceptance_rate']:.1%}")
            col3.metric("Rejected", stats['rejected'], f"{stats['rejection_rate']:.1%}")
            col4.metric("Review", stats['review'], f"{stats['review_rate']:.1%}")

            # Performance metrics
            st.subheader("Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Avg Confidence", f"{stats['avg_confidence']:.3f}")
            col2.metric("Avg Latency", f"{stats['avg_latency_ms']:.1f} ms")
            col3.metric("Total Cost", f"${stats['total_cost_usd']:.4f}")
            col4.metric("Early Term. Rate", f"{stats['early_termination_rate']:.1%}")

            # Decision distribution
            col1, col2 = st.columns(2)

            with col1:
                fig = go.Figure(data=[go.Pie(
                    labels=['Accept', 'Reject', 'Review'],
                    values=[stats['accepted'], stats['rejected'], stats['review']],
                    marker_colors=['green', 'red', 'orange']
                )])
                fig.update_layout(title="Decision Distribution")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Module activation rates
                mod_names = list(stats['module_activation_rates'].keys())
                mod_rates = list(stats['module_activation_rates'].values())

                fig = go.Figure(data=[go.Bar(
                    x=mod_names,
                    y=mod_rates,
                    marker_color='steelblue'
                )])
                fig.update_layout(
                    title="Module Activation Rates",
                    xaxis_title="Module",
                    yaxis_title="Activation Rate",
                    yaxis=dict(tickformat=".0%")
                )
                st.plotly_chart(fig, use_container_width=True)

            # Detailed results table
            st.subheader("Detailed Results")

            results_df = pd.DataFrame([
                {
                    "Fact": f"{fact.subject.id} → {fact.object.id}",
                    "Decision": decision.value,
                    "Confidence": f"{details['cumulative_confidence']:.3f}",
                    "Modules Activated": len(details['activated_modules']),
                    "Early Term.": "Yes" if details['early_terminated'] else "No",
                    "Latency (ms)": f"{details['total_latency_ms']:.1f}"
                }
                for fact, decision, details in results
            ])

            st.dataframe(results_df, use_container_width=True)


def show_module_deep_dive():
    """Show detailed module analysis"""
    st.header("Module Deep Dive")

    st.markdown("Explore individual verification modules and their mechanisms.")

    module_info = {
        "M1: LOV (Lexical-Ontological)": {
            "target": "Semantic Drift",
            "metric1": "Structural Compliance - checks entity classes and relation types against ontology",
            "metric2": "Attribute Compliance - validates attributes against hard/soft constraints",
            "cost": "5 ms, $0.0008/fact",
            "details": """
            **How it works:**
            1. Verifies subject and object belong to valid entity classes
            2. Checks relation type exists in ontology
            3. Validates domain/range restrictions
            4. Assesses attribute compliance with type constraints
            """
        },
        "M2: POV (Protocol-Ontology)": {
            "target": "Content Hallucination",
            "metric1": "Standard Terminology Match - fraction of terms matching industry standards",
            "metric2": "Cross-Standard Consistency - checks semantic consistency across multiple standards",
            "cost": "15 ms, $0.0012/fact",
            "details": """
            **How it works:**
            1. Extracts terms from fact (entities, relations)
            2. Compares against authoritative standard vocabularies (STEP AP242, HL7 FHIR, etc.)
            3. Identifies non-standard or informal terminology
            4. Checks for conflicts between multiple applicable standards
            """
        },
        "M3: MAV (Motion-Aware)": {
            "target": "Spatiotemporal Inconsistency (CRITICAL)",
            "metric1": "Temporal-Spatial Validity - checks ψ_s and ψ_t predicates",
            "metric2": "Physical Feasibility - validates velocity constraints",
            "cost": "50 ms, $0.0018/fact",
            "details": """
            **How it works:**
            1. **Spatial Consistency (ψ_s):** Ensures no entity exists at two separated locations simultaneously
            2. **Temporal Consistency (ψ_t):** Validates causal ordering and travel time requirements
            3. **Velocity Check:** Computes required velocity v_req = Δd/Δt and compares to v_max
            4. **Exponential Penalty:** For violations, score = exp(-(v_req - v_max)/v_max)

            **This module catches 100% of spatiotemporal errors (35% of all errors)!**
            """
        },
        "M4: WSV (Web-Source)": {
            "target": "Content Hallucination",
            "metric1": "Source Credibility - weighted similarity with authoritative external sources",
            "metric2": "Cross-Source Agreement - measures consistency across multiple sources",
            "cost": "120 ms, $0.0006/fact",
            "details": """
            **How it works:**
            1. Queries external authoritative sources (manufacturer docs, standards, databases)
            2. Computes semantic similarity between fact and search results
            3. Weights results by source credibility (manufacturer > academic > news > forums)
            4. Measures coefficient of variation to detect conflicting information
            """
        },
        "M5: ESV (Embedding Similarity)": {
            "target": "Semantic Drift + Hallucination",
            "metric1": "Nearest Neighbor Similarity - average cosine similarity with K-NN",
            "metric2": "Cluster Membership - GMM probability of belonging to semantic clusters",
            "cost": "800 ms, $0.0003/fact",
            "details": """
            **How it works:**
            1. Converts fact to dense vector embedding using sentence-transformers
            2. Finds K nearest neighbors in historical fact embeddings
            3. Computes average normalized cosine similarity
            4. Uses Gaussian Mixture Model to assess cluster membership probability
            5. Flags statistical anomalies that deviate from learned patterns
            """
        }
    }

    selected_module = st.selectbox("Select Module", list(module_info.keys()))

    info = module_info[selected_module]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(selected_module)

        st.markdown(f"**Primary Target:** {info['target']}")
        st.markdown(f"**Computational Cost:** {info['cost']}")

        st.markdown("#### Dual-Metric Design")
        st.markdown(f"**Metric 1:** {info['metric1']}")
        st.markdown(f"**Metric 2:** {info['metric2']}")

        st.markdown("#### How It Works")
        st.markdown(info['details'])

    with col2:
        st.markdown("#### Parameters")

        module_id = selected_module.split(":")[0]
        module_obj = [m for m in st.session_state.modules if m.module_id == module_id][0]

        st.metric("Activation Threshold (θ_i)", f"{module_obj.threshold:.2f}")
        st.metric("Balance Factor (α_i)", f"{module_obj.alpha:.2f}")
        st.metric("Trust Weight (w_i)", f"{module_obj.weight:.2f}")

        st.info("These parameters are tuned by AAIC based on performance feedback.")


def show_performance_metrics():
    """Show performance metrics and comparison"""
    st.header("Performance Metrics")

    st.markdown("Comparative analysis with baselines and system efficiency metrics.")

    # Baseline comparison (from paper Table 5)
    st.subheader("Comparison with State-of-the-Art")

    comparison_data = {
        "Method": ["KGValidator", "KG-Agent", "World Avatar", "ATLASky-AI"],
        "Precision": [0.82, 0.85, 0.88, 0.94],
        "Recall": [0.81, 0.83, 0.86, 0.93],
        "F1": [0.81, 0.84, 0.87, 0.94],
        "FPR (%)": [9.8, 8.3, 6.6, 3.2]
    }

    df_comparison = pd.DataFrame(comparison_data)

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        for metric in ["Precision", "Recall", "F1"]:
            fig.add_trace(go.Bar(
                name=metric,
                x=comparison_data["Method"],
                y=comparison_data[metric]
            ))

        fig.update_layout(
            title="Performance Comparison",
            xaxis_title="Method",
            yaxis_title="Score",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(data=[go.Bar(
            x=comparison_data["Method"],
            y=comparison_data["FPR (%)"],
            marker_color=['lightcoral', 'coral', 'orange', 'green']
        )])

        fig.update_layout(
            title="False Positive Rate (Lower is Better)",
            xaxis_title="Method",
            yaxis_title="FPR (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_comparison, use_container_width=True)

    st.success("**ATLASky-AI achieves 39-57% FPR reduction compared to best baseline!**")

    # Module costs
    st.subheader("Module Computational Costs")

    module_costs = {
        "Module": ["M1: LOV", "M2: POV", "M3: MAV", "M4: WSV", "M5: ESV"],
        "Latency (ms)": [5, 15, 50, 120, 800],
        "Cost ($/fact)": [0.0008, 0.0012, 0.0018, 0.0006, 0.0003],
        "Activation Rate": [0.683, 0.521, 0.412, 0.285, 0.227]
    }

    df_costs = pd.DataFrame(module_costs)

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(data=[go.Bar(
            x=module_costs["Module"],
            y=module_costs["Latency (ms)"],
            marker_color='steelblue'
        )])
        fig.update_layout(
            title="Module Latency",
            xaxis_title="Module",
            yaxis_title="Latency (ms)",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(data=[go.Bar(
            x=module_costs["Module"],
            y=module_costs["Activation Rate"],
            marker_color='seagreen'
        )])
        fig.update_layout(
            title="Activation Rates",
            xaxis_title="Module",
            yaxis_title="Activation Rate",
            yaxis=dict(tickformat=".0%"),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_costs, use_container_width=True)

    # Efficiency gains
    st.subheader("Efficiency Gains")

    col1, col2, col3 = st.columns(3)
    col1.metric("Early Termination Rate", "40%", "Reduced computation")
    col2.metric("Avg Latency", "248 ms", "-75% with early term.")
    col3.metric("Cost per Fact", "$0.0029", "-59% vs baselines")

    st.info("""
    **Key Insights:**
    - M3 (MAV) is the most critical module, catching 100% of spatiotemporal errors
    - Early termination reduces computation by 40% while maintaining accuracy
    - Sequential execution with cheap modules first optimizes cost
    - Only 22.7% of facts require expensive ESV analysis
    """)


if __name__ == "__main__":
    main()
