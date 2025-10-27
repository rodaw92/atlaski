# ATLASky-AI Demo Interface

A Streamlit-based demonstration of the ATLASky-AI framework for verifying LLM-generated knowledge in 4D Spatiotemporal Knowledge Graphs.

## Overview

ATLASky-AI implements a Defense-in-Depth verification framework that addresses three critical error classes in LLM-generated knowledge:

1. **Content Hallucination** - Fabricated facts with no source evidence
2. **Spatiotemporal Inconsistency** - Facts that violate physical laws
3. **Semantic Drift** - Systematic misapplication of terminology

## Architecture

The system implements a three-stage pipeline:

### Stage 1: Data Preprocessing
- Normalizes heterogeneous raw data
- Temporal alignment and spatial validation
- Schema standardization

### Stage 2: LLM-Based Extraction
- Domain-specialized prompts
- Structured fact extraction
- Confidence-weighted output

### Stage 3: TruthFlow Verification
Five specialized modules with early termination:
- **M1 (LOV)**: Lexical-Ontological Verification → Semantic Drift
- **M2 (POV)**: Protocol-Ontology Verification → Hallucination
- **M3 (MAV)**: Motion-Aware Verification → ST-Inconsistency ⭐ **CRITICAL**
- **M4 (WSV)**: Web-Source Verification → Hallucination
- **M5 (ESV)**: Embedding Similarity Verification → Drift + Hallucination

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
cd /home/user/atlaski
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Configure OpenAI API key for LLM features:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Running the Demo

Launch the Streamlit interface:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Demo Features

### 1. Overview
- System architecture explanation
- Module descriptions and targets
- Performance metrics summary

### 2. Single Fact Verification
- Step-by-step verification of individual facts
- Detailed module score breakdown
- Visual score progression
- Real-time decision making

### 3. Batch Processing
- Process multiple facts simultaneously
- Aggregate statistics and metrics
- Decision distribution analysis
- Module activation patterns

### 4. Module Deep Dive
- Detailed exploration of each verification module
- Dual-metric explanations
- Parameter configurations
- Implementation details

### 5. Performance Metrics
- Comparison with state-of-the-art baselines
- Computational cost analysis
- Efficiency gains visualization
- FPR reduction demonstration

## Key Results

- **94%** Precision, **93%** Recall
- **39-57%** FPR reduction vs. best baseline
- **40%** early termination rate (efficiency)
- **248ms** average latency with early termination

## Project Structure

```
atlaski/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── src/
│   ├── models/
│   │   └── stkg.py            # STKG data structures
│   └── modules/
│       ├── verification.py    # Verification modules (M1-M5)
│       └── rmmve.py          # RMMVe engine
├── data/                      # Example datasets (generated in demo)
└── config/                    # Configuration files
```

## Sample Facts

The demo includes 5 pre-configured sample facts demonstrating different scenarios:

1. **Valid High-Confidence Fact** - Should ACCEPT
2. **Minor Physics Violation** - May REVIEW or REJECT
3. **Valid Inspection Record** - Should ACCEPT
4. **Low-Confidence Hallucination** - Should REJECT
5. **Critical Physics Violation** - Should REJECT (velocity exceeds limits)

## Module Parameters

Each module has adaptive parameters:
- **θ_i** (Activation Threshold): Minimum score to contribute to decision
- **α_i** (Balance Factor): Weight between Metric 1 and Metric 2
- **w_i** (Trust Weight): Module's influence on final confidence

These parameters are tuned by the Autonomous Adaptive Intelligence Cycle (AAIC) in production deployments.

## Verification Decision Logic

```
If cumulative_confidence >= Θ (0.75):
    → ACCEPT

Else if cumulative_confidence >= Θ - ε (0.65):
    → REVIEW (human review)

Else:
    → REJECT
```

Early termination occurs if cumulative confidence reaches Θ before all modules execute.

## Citation

If you use this framework in your research, please cite:

```bibtex
@article{atlaskyai2025,
  title={ATLASky-AI: Defense-in-Depth Verification for 4D Spatiotemporal Knowledge Graphs},
  author={[Your Name]},
  journal={[Conference/Journal]},
  year={2025}
}
```

## License

[Specify your license]

## Contact

For questions or issues, please open an issue on GitHub or contact [your email].

## Acknowledgments

This work demonstrates verification techniques for safety-critical digital twin applications in aerospace, healthcare, manufacturing, and logistics domains.
