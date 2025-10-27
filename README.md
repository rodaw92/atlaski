# ATLASky-AI: Defense-in-Depth Verification Framework

**Preventing AI Hallucinations in Safety-Critical Spatiotemporal Knowledge Graphs**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)

---

## 🎯 The Problem

Large Language Models (LLMs) can extract knowledge graphs **100x faster** than humans, but they introduce dangerous errors:

- **📝 Content Hallucination (42%)**: Fabricated facts with no source evidence
- **⚡ Spatiotemporal Inconsistency (35%)**: Facts that violate physics laws
- **🔄 Semantic Drift (23%)**: Systematic misapplication of terminology

**In aerospace and healthcare domains, these errors can be FATAL.**

## ✅ Our Solution

**ATLASky-AI** implements Defense-in-Depth verification through five specialized modules:

| Module | Name | Detects | Critical? |
|--------|------|---------|-----------|
| **M1** | LOV (Lexical-Ontological) | Semantic Drift | ✓ |
| **M2** | POV (Protocol-Ontology) | Content Hallucination | ✓ |
| **M3** | MAV (Motion-Aware) | **Spatiotemporal Inconsistency** | **⭐ IRREPLACEABLE** |
| **M4** | WSV (Web-Source) | Content Hallucination | ✓ |
| **M5** | ESV (Embedding Similarity) | Drift + Hallucination | ✓ |

### Why M3 is Critical

**100% of spatiotemporal errors are caught ONLY by M3.** Even if M1, M2, M4, M5 all pass a fact, M3 can reject it for violating physics constraints. Without M3, 35% of errors go undetected.

## 📊 Performance

| Metric | ATLASky-AI | Best Baseline | Improvement |
|--------|------------|---------------|-------------|
| **Precision** | **94%** | 88% | +6.8% |
| **Recall** | **93%** | 86% | +8.1% |
| **FPR** | **3.2%** | 6.6% | **-51.5%** |

**Real Impact:** 39-57% FPR reduction = **452 fewer false alarms** at 10,500 facts, **ROI < 4 months**

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch demo
streamlit run app.py
```

Demo opens at `http://localhost:8501`

## 🎬 Demo Features

### 1. 🎯 Value Proposition
- Problem + Solution overview
- Key performance metrics
- Business case

### 2. 📊 How It Works
- 3-stage pipeline visualization
- Module comparison matrix
- Defense-in-Depth explanation

### 3. 🚨 Critical Demo: M3 in Action
**The killer feature:**

**Scenario:** Turbine blade claimed to move 100m in 15 seconds
- Required velocity: 6.7 m/s > Max 5.0 m/s
- M1, M2, M4, M5: All PASS ✅
- M3: REJECTS ❌ (physics violation!)

**Without ATLASky-AI:** False location → Wrong component → **Aircraft incident**
**With ATLASky-AI:** Physics violation detected → Fact rejected → **Incident prevented**

### 4. 📈 Performance Comparison
- Visual baseline comparison
- Interactive ROI calculator
- Cost savings analysis

## 📁 Project Structure

```
atlaski/
├── app.py                      # Enhanced Streamlit demo
├── test_verification.py       # Unit tests
├── src/
│   ├── models/stkg.py         # 4D STKG data structures
│   └── modules/
│       ├── verification.py    # Five verification modules
│       └── rmmve.py          # RMMVe engine
└── docs/
    ├── README.md              # This file
    ├── QUICKSTART.md         # Demo guide
    └── ENHANCEMENTS.md       # What changed and why
```

## 💡 Key Insight

> **M3 (MAV) catches 100% of spatiotemporal errors - no other module can detect these!**

This is the core value proposition: 35% of errors are physics violations that pass all semantic checks.

## 🎓 Paper Implementation

| Paper Section | Implementation |
|--------------|----------------|
| Definition 1-3 | `src/models/stkg.py` |
| Equations 6-8 | `src/modules/verification.py`, `rmmve.py` |
| Algorithm 1 | `src/modules/rmmve.py::verify()` |
| Table 5 | `app.py::show_comparison_mode()` |

## 🎤 10-Minute Demo Script

**For conference presentations:**

1. **Value Proposition (2 min)** - Show problem + solution
2. **How It Works (2 min)** - Pipeline + module matrix
3. **Critical Demo (4 min)** - M3 catches physics violation
4. **Performance (2 min)** - Comparison + ROI calculator

**Key talking point:** "Without M3, this dangerous fact would be accepted. M3 is irreplaceable."

## 📊 Results Summary

- **94% precision, 93% recall** on 12,620 facts
- **39-57% FPR reduction** vs. state-of-the-art
- **40% early termination** efficiency gain
- **87% cost reduction** in production (AddQual deployment)
- **ROI < 4 months**

## 🔧 Domain Adaptation

Deploy in new domains (2-4 weeks):
1. Define ontology (50-200 entity classes, 20-50 relations)
2. Load industry standards (STEP AP242, HL7 FHIR, ISA-95)
3. Specify physics constraints (max velocities, facility geometry)
4. Set source credibility weights
5. Train embeddings (10K+ historical facts)

## 📝 Citation

```bibtex
@article{atlaskyai2025,
  title={ATLASky-AI: Defense-in-Depth Verification for 4D Spatiotemporal Knowledge Graphs},
  author={[Your Name]},
  year={2025}
}
```

## 📧 Contact

Questions or collaboration: [your email]

---

**💡 Tagline:** *"Preventing the aircraft incident that didn't happen because M3 caught the physics violation."*
