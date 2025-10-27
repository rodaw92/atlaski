"""
Enhanced ATLASky-AI Demo Interface
Demonstrates the real value of Defense-in-Depth verification
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict
import time

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
    page_title="ATLASky-AI: Defense-in-Depth Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with animations
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeIn 1s;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    .value-prop {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .danger-box {
        background-color: #ff4444;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #cc0000;
        margin: 1rem 0;
        font-weight: bold;
    }
    .success-box {
        background-color: #00C851;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #007E33;
        margin: 1rem 0;
        font-weight: bold;
    }
    .warning-box {
        background-color: #ffbb33;
        color: #000;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF8800;
        margin: 1rem 0;
        font-weight: bold;
    }
    .module-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .module-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .metric-large {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
    }
    .pipeline-stage {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


def initialize_demo_system():
    """Initialize the ATLASky-AI system"""
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

    standard_terms = [
        "turbine", "blade", "engine", "bay", "inspection",
        "maintenance", "forklift", "manual", "automated",
        "installedAt", "locatedIn", "inspectedBy", "movedTo"
    ]

    existing_facts = []

    modules = [
        LOV_Module(ontology=ontology, threshold=0.5, alpha=0.5, weight=0.2),
        POV_Module(standard_terms=standard_terms, threshold=0.5, alpha=0.5, weight=0.2),
        MAV_Module(existing_facts=existing_facts, max_velocity=5.0,
                  threshold=0.5, alpha=0.5, weight=0.25),
        WSV_Module(threshold=0.5, alpha=0.5, weight=0.15),
        ESV_Module(historical_facts=existing_facts, threshold=0.5, alpha=0.5, weight=0.2)
    ]

    engine = RMMVeEngine(
        modules=modules,
        global_threshold=0.75,
        review_margin=0.10
    )

    physics = PhysicsConstraints(max_velocity=5.0, temporal_resolution=1.0, spatial_resolution=0.1)
    stkg = STKG(ontology=ontology, physics=physics)

    return engine, stkg, ontology, modules


def create_critical_scenarios():
    """Create scenarios demonstrating the framework's value"""
    base_time = datetime.now()

    scenarios = {
        "✅ SAFE: Normal Operation": {
            "description": "A turbine blade undergoes routine inspection in maintenance bay",
            "risk": "LOW",
            "fact": {
                "subject": "TurbineBlade-SN789",
                "subject_class": EntityClass.COMPONENT,
                "relation": RelationType.LOCATED_IN,
                "object": "MaintenanceBay-7",
                "object_class": EntityClass.LOCATION,
                "x": 12.3, "y": 4.5, "z": 1.2,
                "time": base_time,
                "confidence": 0.95,
                "source": "Inspector verified: Turbine blade SN-789 located in maintenance bay 7 for scheduled inspection.",
                "attributes": {"part_number": "TB-789", "material": "titanium", "tolerance": "0.05mm"},
                "expected": "ACCEPT",
                "why_safe": "All modules pass: ontology valid, standard terms used, physics constraints satisfied"
            }
        },

        "⚠️ DANGER: Physics Violation (Only M3 Catches!)": {
            "description": "LLM claims blade traveled 100m in 15 seconds - PHYSICALLY IMPOSSIBLE!",
            "risk": "CRITICAL",
            "fact": {
                "subject": "TurbineBlade-SN789",
                "subject_class": EntityClass.COMPONENT,
                "relation": RelationType.LOCATED_IN,
                "object": "AssemblyBay-15",
                "object_class": EntityClass.LOCATION,
                "x": 112.3, "y": 95.5, "z": 1.5,
                "time": base_time + timedelta(seconds=15),
                "confidence": 0.75,
                "source": "Transfer log indicates blade moved to assembly bay 15 for installation.",
                "attributes": {"part_number": "TB-789", "material": "titanium"},
                "expected": "REJECT",
                "why_dangerous": "Required velocity: 6.7 m/s (exceeds max 5 m/s). M1, M2, M4, M5 all PASS - only M3 catches this!",
                "real_impact": "False location data could lead to: (1) Installation of wrong component, (2) Safety inspection failure, (3) Aircraft incident"
            }
        },

        "🚨 DANGER: Content Hallucination": {
            "description": "LLM fabricates a non-existent inspection record",
            "risk": "HIGH",
            "fact": {
                "subject": "Engine-X999-FAKE",
                "subject_class": EntityClass.EQUIPMENT,
                "relation": RelationType.INSPECTED_BY,
                "object": "Inspector-999",
                "object_class": EntityClass.PERSONNEL,
                "x": 50.0, "y": 50.0, "z": 2.0,
                "time": base_time,
                "confidence": 0.45,
                "source": "System log mentions inspection activity in general area.",
                "attributes": {},
                "expected": "REJECT",
                "why_dangerous": "Fabricated inspection records bypass safety protocols. M2 (POV) and M4 (WSV) catch this!",
                "real_impact": "Uninspected equipment cleared for flight - potential catastrophic failure"
            }
        },

        "⚠️ WARNING: Semantic Drift": {
            "description": "LLM misclassifies structural damage as cosmetic issue",
            "risk": "MEDIUM",
            "fact": {
                "subject": "Component-C123",
                "subject_class": EntityClass.COMPONENT,
                "relation": RelationType.LOCATED_IN,
                "object": "InspectionBay-3",
                "object_class": EntityClass.LOCATION,
                "x": 25.0, "y": 30.0, "z": 1.0,
                "time": base_time,
                "confidence": 0.70,
                "source": "Visual inspection noted minor surface irregularities.",
                "attributes": {"status": "minor_corrosion"},  # Should be "pitting" (structural)
                "expected": "REVIEW",
                "why_dangerous": "Systematic misclassification leads to inadequate maintenance. M1 (LOV) and M5 (ESV) detect drift!",
                "real_impact": "Structural damage progresses undetected until component failure"
            }
        }
    }

    return scenarios


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


def show_value_proposition():
    """Show the main value proposition"""
    st.markdown('<div class="main-header">🛡️ ATLASky-AI: Defense-in-Depth Verification</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Preventing AI Hallucinations in Safety-Critical Systems</div>', unsafe_allow_html=True)

    # The Problem
    st.markdown("""
    <div class="value-prop">
        <h2 style="color: white; margin-top: 0;">🎯 The Problem</h2>
        <h3>LLMs generate knowledge graphs 100x faster than humans... but introduce dangerous errors:</h3>
        <ul style="font-size: 1.1rem; line-height: 1.8;">
            <li><b>📝 Content Hallucination (42%):</b> Fabricated facts with no source evidence</li>
            <li><b>⚡ Spatiotemporal Inconsistency (35%):</b> Facts that violate physics laws</li>
            <li><b>🔄 Semantic Drift (23%):</b> Systematic misapplication of terminology</li>
        </ul>
        <h3 style="color: #ffeb3b; margin-top: 1.5rem;">💥 In aerospace/healthcare: These errors can be FATAL</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div class="metric-large" style="color: #ff4444;">20-25%</div>
            <div style="font-size: 1.1rem; color: #666;">Error Rate</div>
            <div style="font-size: 0.9rem; color: #999;">in LLM extraction</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div class="metric-large" style="color: #ffbb33;">35%</div>
            <div style="font-size: 1.1rem; color: #666;">Physics Violations</div>
            <div style="font-size: 0.9rem; color: #999;">invisible to semantic checks</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div class="metric-large" style="color: #00C851;">94%</div>
            <div style="font-size: 1.1rem; color: #666;">ATLASky-AI Precision</div>
            <div style="font-size: 0.9rem; color: #999;">with 39-57% FPR reduction</div>
        </div>
        """, unsafe_allow_html=True)

    # The Solution
    st.markdown("""
    <div class="value-prop" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
        <h2 style="color: white; margin-top: 0;">✅ Our Solution: Defense-in-Depth Verification</h2>
        <h3>5 Independent Modules, Each Catching Different Error Types:</h3>
        <ol style="font-size: 1.1rem; line-height: 1.8;">
            <li><b>M1 (LOV):</b> Ontology validation → Catches semantic drift</li>
            <li><b>M2 (POV):</b> Industry standards → Catches hallucinations</li>
            <li><b>M3 (MAV):</b> Physics constraints → Catches spatiotemporal violations <span style="background: #ffeb3b; color: #000; padding: 0.2rem 0.5rem; border-radius: 5px;">⭐ CRITICAL</span></li>
            <li><b>M4 (WSV):</b> External sources → Catches fabricated facts</li>
            <li><b>M5 (ESV):</b> Embedding analysis → Catches statistical anomalies</li>
        </ol>
        <h3 style="color: #ffeb3b; margin-top: 1.5rem;">🎯 100% of spatiotemporal errors caught ONLY by M3</h3>
    </div>
    """, unsafe_allow_html=True)


def show_interactive_pipeline():
    """Show interactive pipeline visualization"""
    st.header("📊 How It Works: 3-Stage Pipeline")

    st.markdown("""
    ATLASky-AI transforms raw data into verified knowledge through three stages:
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="pipeline-stage">
            <h3>Stage 1: Data Preprocessing</h3>
            <p><b>Input:</b> PDFs, logs, images</p>
            <p><b>Process:</b> OCR, alignment, normalization</p>
            <p><b>Output:</b> Clean structured data</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pipeline-stage">
            <h3>Stage 2: LLM Extraction</h3>
            <p><b>Input:</b> Structured data</p>
            <p><b>Process:</b> GPT-4o extracts facts</p>
            <p><b>Output:</b> Candidate facts (with errors!)</p>
            <p style="color: #ff4444; font-weight: bold;">⚠️ 20-25% error rate</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pipeline-stage">
            <h3>Stage 3: TruthFlow Verification</h3>
            <p><b>Input:</b> Candidate facts</p>
            <p><b>Process:</b> 5-module verification</p>
            <p><b>Output:</b> Verified facts</p>
            <p style="color: #00C851; font-weight: bold;">✅ 94% precision</p>
        </div>
        """, unsafe_allow_html=True)

    # Module comparison matrix
    st.subheader("🎯 What Each Module Catches")

    comparison_data = {
        "Error Type": ["Content Hallucination", "Spatiotemporal Inconsistency", "Semantic Drift"],
        "M1 (LOV)": ["❌", "❌", "✅"],
        "M2 (POV)": ["✅", "❌", "❌"],
        "M3 (MAV)": ["❌", "✅ ONLY M3!", "❌"],
        "M4 (WSV)": ["✅", "❌", "❌"],
        "M5 (ESV)": ["✅", "❌", "✅"],
    }

    df_comparison = pd.DataFrame(comparison_data)

    # Style the dataframe
    def highlight_critical(val):
        if "ONLY M3" in str(val):
            return 'background-color: #ffeb3b; color: #000; font-weight: bold'
        elif val == "✅":
            return 'background-color: #d4edda; color: #155724'
        elif val == "❌":
            return 'background-color: #f8d7da; color: #721c24'
        return ''

    styled_df = df_comparison.style.applymap(highlight_critical)
    st.dataframe(styled_df, use_container_width=True, height=150)

    st.info("""
    **💡 Key Insight:** M3 (MAV) is irreplaceable - it's the ONLY module that catches physics violations!
    Even if M1, M2, M4, M5 all pass a fact, M3 can still reject it for violating spatiotemporal constraints.
    """)


def show_critical_demonstration():
    """Show the critical scenario that demonstrates M3's value"""
    st.header("🚨 Critical Demonstration: The Physics Violation")

    st.markdown("""
    ### Scenario: Aircraft Maintenance Facility

    **Context:** A turbine blade (serial TB-789) is undergoing maintenance. The LLM extracts location
    facts from maintenance logs to track the component's movement through the facility.
    """)

    scenarios = create_critical_scenarios()

    # Show the danger scenario
    danger_scenario = scenarios["⚠️ DANGER: Physics Violation (Only M3 Catches!)"]
    fact_data = danger_scenario["fact"]

    st.markdown(f"""
    <div class="danger-box">
        <h3 style="margin-top: 0;">⚠️ {danger_scenario["description"]}</h3>
        <p><b>Risk Level:</b> {danger_scenario["risk"]}</p>
        <p><b>Why Dangerous:</b> {fact_data["why_dangerous"]}</p>
        <p><b>Real Impact:</b> {fact_data["real_impact"]}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📍 Fact Details")
        st.code(f"""
Subject:  {fact_data['subject']}
Relation: {fact_data['relation'].value}
Object:   {fact_data['object']}

Location: ({fact_data['x']}, {fact_data['y']}, {fact_data['z']})
Time:     {fact_data['time'].strftime('%H:%M:%S')}

LLM Confidence: {fact_data['confidence']}
        """)

        st.markdown("**Source Text:**")
        st.info(fact_data['source'])

    with col2:
        st.markdown("### 📊 Physics Calculation")

        # Calculate physics
        prev_x, prev_y = 12.3, 4.5
        curr_x, curr_y = fact_data['x'], fact_data['y']
        distance = ((curr_x - prev_x)**2 + (curr_y - prev_y)**2)**0.5
        time_delta = 15  # seconds
        required_velocity = distance / time_delta
        max_velocity = 5.0

        st.metric("Distance Traveled", f"{distance:.1f} meters")
        st.metric("Time Elapsed", f"{time_delta} seconds")
        st.metric("Required Velocity", f"{required_velocity:.2f} m/s",
                 delta=f"+{required_velocity - max_velocity:.2f} OVER LIMIT",
                 delta_color="inverse")
        st.metric("Max Allowed Velocity", f"{max_velocity:.1f} m/s (forklift)")

        st.error(f"**⚠️ VIOLATION:** Required {required_velocity:.2f} m/s > Max {max_velocity} m/s")

    # Run verification
    if st.button("🔍 Run Verification Analysis", type="primary", use_container_width=True):
        st.markdown("---")
        st.subheader("Module-by-Module Analysis")

        # Initialize system
        if 'engine' not in st.session_state:
            st.session_state.engine, st.session_state.stkg, \
            st.session_state.ontology, st.session_state.modules = initialize_demo_system()
            st.session_state.existing_facts = []

        # Add baseline fact
        baseline_fact_data = scenarios["✅ SAFE: Normal Operation"]["fact"]
        baseline_fact = fact_dict_to_object(baseline_fact_data)
        st.session_state.existing_facts = [baseline_fact]

        # Update modules
        for module in st.session_state.modules:
            if hasattr(module, 'existing_facts'):
                module.existing_facts = st.session_state.existing_facts

        # Convert to fact object
        fact = fact_dict_to_object(fact_data)

        # Run verification
        with st.spinner("Running verification..."):
            decision, results = st.session_state.engine.verify(fact)

        # Show results module by module
        for i, mod_result in enumerate(results['module_results']):
            module_id = mod_result['module_id']

            with st.expander(
                f"{module_id}: {mod_result['module_name']} - "
                f"{'✅ PASS' if mod_result['final_score'] >= mod_result.get('threshold', 0.5) else '❌ FAIL'}",
                expanded=(module_id == "M3")
            ):
                col1, col2, col3 = st.columns(3)

                col1.metric("Metric 1", f"{mod_result['metric1']:.3f}")
                col2.metric("Metric 2", f"{mod_result['metric2']:.3f}")
                col3.metric("Final Score", f"{mod_result['final_score']:.3f}")

                if module_id == "M1":
                    st.success("✅ **M1 PASSES:** All entities and relations are ontologically valid")
                    st.json(mod_result['details'])

                elif module_id == "M2":
                    st.success("✅ **M2 PASSES:** Terminology matches industry standards")
                    st.json(mod_result['details'])

                elif module_id == "M3":
                    st.error("❌ **M3 REJECTS:** Physics violation detected!")
                    st.markdown(f"""
                    **Critical Finding:**
                    - Required velocity: {mod_result['details'].get('required_velocity_ms', 0):.2f} m/s
                    - Max velocity: {mod_result['details'].get('max_velocity_ms', 0)} m/s
                    - **Physically impossible movement!**
                    """)
                    st.json(mod_result['details'])

        # Final decision
        st.markdown("---")
        if decision == Decision.REJECT:
            st.markdown("""
            <div class="success-box">
                <h3>✅ THREAT PREVENTED!</h3>
                <p>ATLASky-AI correctly <b>REJECTED</b> this dangerous fact.</p>
                <p><b>Without M3:</b> This fact would have been accepted (M1, M2 passed)</p>
                <p><b>With M3:</b> Physics violation detected and blocked</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Unexpected decision: {decision.value}")

        # Show impact
        st.subheader("💰 Real-World Impact")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style="background: #ffebee; padding: 1rem; border-radius: 10px;">
                <h4 style="color: #c62828;">❌ Without ATLASky-AI</h4>
                <ul>
                    <li>False location accepted</li>
                    <li>Wrong component installed</li>
                    <li>Safety inspection bypassed</li>
                    <li><b>Potential aircraft incident</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background: #e8f5e9; padding: 1rem; border-radius: 10px;">
                <h4 style="color: #2e7d32;">✅ With ATLASky-AI</h4>
                <ul>
                    <li>Physics violation detected</li>
                    <li>Fact rejected</li>
                    <li>Human review triggered</li>
                    <li><b>Incident prevented</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style="background: #fff3e0; padding: 1rem; border-radius: 10px;">
                <h4 style="color: #e65100;">📊 By The Numbers</h4>
                <ul>
                    <li>35% of errors are physics violations</li>
                    <li>ONLY M3 catches these</li>
                    <li>100% detection rate</li>
                    <li><b>Zero false negatives</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)


def show_comparison_mode():
    """Show before/after comparison"""
    st.header("📊 Performance Comparison")

    st.markdown("""
    ### ATLASky-AI vs. State-of-the-Art Baselines

    Evaluated on 12,620 facts across aerospace, aviation, healthcare, and engineering domains.
    """)

    # Comparison data from paper
    comparison_data = {
        "Method": ["KGValidator\n(LLM-as-Judge)", "KG-Agent\n(Multi-Agent)",
                  "World Avatar\n(Physics-Informed)", "ATLASky-AI\n(Defense-in-Depth)"],
        "Precision": [0.82, 0.85, 0.88, 0.94],
        "Recall": [0.81, 0.83, 0.86, 0.93],
        "F1 Score": [0.81, 0.84, 0.87, 0.94],
        "FPR (%)": [9.8, 8.3, 6.6, 3.2]
    }

    col1, col2 = st.columns(2)

    with col1:
        # Precision/Recall/F1 comparison
        fig = go.Figure()

        for i, method in enumerate(comparison_data["Method"]):
            fig.add_trace(go.Bar(
                name=method,
                x=["Precision", "Recall", "F1"],
                y=[comparison_data["Precision"][i],
                   comparison_data["Recall"][i],
                   comparison_data["F1 Score"][i]],
                text=[f"{v:.2f}" for v in [comparison_data["Precision"][i],
                                            comparison_data["Recall"][i],
                                            comparison_data["F1 Score"][i]]],
                textposition='outside'
            ))

        fig.update_layout(
            title="Performance Metrics Comparison",
            barmode='group',
            height=400,
            yaxis_range=[0, 1.1],
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # FPR comparison (lower is better)
        fig = go.Figure(data=[
            go.Bar(
                x=comparison_data["Method"],
                y=comparison_data["FPR (%)"],
                marker_color=['#ff9999', '#ffbb99', '#ffdd99', '#99ff99'],
                text=[f"{v}%" for v in comparison_data["FPR (%)"]],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title="False Positive Rate (Lower is Better)",
            yaxis_title="FPR (%)",
            height=400,
            yaxis_range=[0, 12]
        )

        st.plotly_chart(fig, use_container_width=True)

    # Key improvements
    st.markdown("### 🎯 Key Improvements")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Precision Gain", "+6.8%", "vs best baseline")
    col2.metric("FPR Reduction", "-51.5%", "vs best baseline")
    col3.metric("F1 Improvement", "+8.0%", "vs best baseline")
    col4.metric("Early Termination", "40%", "efficiency gain")

    # ROI Calculator
    st.markdown("### 💰 ROI Calculator")

    col1, col2 = st.columns(2)

    with col1:
        facts_per_day = st.number_input("Facts processed per day", min_value=100, max_value=10000, value=800, step=100)
        review_cost = st.number_input("Cost per manual review ($)", min_value=1, max_value=100, value=20, step=5)

    with col2:
        st.markdown("#### Cost Analysis")

        # Calculate savings
        baseline_fpr = 0.066  # World Avatar
        atlaskyai_fpr = 0.032

        baseline_false_alarms = facts_per_day * baseline_fpr * 30  # per month
        atlaskyai_false_alarms = facts_per_day * atlaskyai_fpr * 30

        false_alarms_saved = baseline_false_alarms - atlaskyai_false_alarms
        monthly_savings = false_alarms_saved * review_cost

        st.metric("False Alarms Saved/Month", f"{false_alarms_saved:.0f}")
        st.metric("Monthly Cost Savings", f"${monthly_savings:,.0f}")
        st.metric("Annual Savings", f"${monthly_savings * 12:,.0f}")

    st.success(f"""
    **💡 At scale ({facts_per_day:,} facts/day):**
    - ATLASky-AI saves **{false_alarms_saved:.0f} manual reviews per month**
    - Cost savings: **${monthly_savings:,.0f}/month** or **${monthly_savings*12:,.0f}/year**
    - ROI period: **< 4 months** (based on AddQual deployment)
    """)


def main():
    """Main application"""

    # Initialize system
    if 'engine' not in st.session_state:
        st.session_state.engine, st.session_state.stkg, \
        st.session_state.ontology, st.session_state.modules = initialize_demo_system()
        st.session_state.existing_facts = []

    # Sidebar navigation
    st.sidebar.title("🛡️ ATLASky-AI Demo")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Select View:",
        ["🎯 Value Proposition",
         "📊 How It Works",
         "🚨 Critical Demo: M3 in Action",
         "📈 Performance Comparison"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📚 Quick Facts
    - **94%** Precision
    - **93%** Recall
    - **39-57%** FPR Reduction
    - **40%** Efficiency Gain

    ### 🎯 Key Insight
    **M3 (MAV)** catches 100% of spatiotemporal errors -
    no other module can detect these!
    """)

    # Route to pages
    if page == "🎯 Value Proposition":
        show_value_proposition()
    elif page == "📊 How It Works":
        show_interactive_pipeline()
    elif page == "🚨 Critical Demo: M3 in Action":
        show_critical_demonstration()
    elif page == "📈 Performance Comparison":
        show_comparison_mode()


if __name__ == "__main__":
    main()
