# ATLASky-AI Project Structure

## Overview
This document provides a complete overview of all files in the ATLASky-AI demo implementation.

## File Structure

```
atlaski/
│
├── README.md                           # Main project documentation
├── QUICKSTART.md                       # Quick start guide for running the demo
├── PROJECT_STRUCTURE.md               # This file - project structure documentation
│
├── requirements.txt                    # Python dependencies
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore patterns
│
├── app.py                             # Main Streamlit application [PRIMARY FILE]
├── run_demo.sh                        # Startup script for launching demo
├── test_verification.py               # Unit tests for verification pipeline
│
├── src/                               # Source code directory
│   ├── __init__.py                   # Package initialization
│   │
│   ├── models/                       # Data models
│   │   ├── __init__.py              # Models package init
│   │   └── stkg.py                  # 4D STKG data structures [CORE]
│   │
│   └── modules/                      # Verification modules
│       ├── __init__.py              # Modules package init
│       ├── verification.py          # Five verification modules (M1-M5) [CORE]
│       └── rmmve.py                # RMMVe verification engine [CORE]
│
├── config/                           # Configuration directory (empty - for future use)
└── data/                            # Data directory (empty - generated at runtime)
```

## Core Files Description

### 1. Application Files

#### `app.py` (1,200+ lines)
**Purpose:** Main Streamlit web interface
**Key Components:**
- System initialization with demo configuration
- Five navigation pages:
  1. Overview - Architecture and metrics
  2. Single Fact Verification - Interactive fact verification
  3. Batch Processing - Multiple facts with statistics
  4. Module Deep Dive - Detailed module exploration
  5. Performance Metrics - Comparison with baselines
- Sample fact generation
- Visualization functions
- Session state management

**Key Functions:**
- `initialize_demo_system()` - Sets up ontology, modules, and RMMVe engine
- `create_sample_facts()` - Generates 5 sample facts for demonstration
- `show_single_verification()` - Interactive single fact verification
- `show_batch_processing()` - Batch verification with statistics
- `show_module_deep_dive()` - Module details and explanations
- `show_performance_metrics()` - Performance comparisons

### 2. Core Implementation

#### `src/models/stkg.py` (400+ lines)
**Purpose:** 4D Spatiotemporal Knowledge Graph data structures
**Implements:** Definition 1, 2, 3 from the paper

**Key Classes:**
- `EntityClass` - Enum for entity types
- `RelationType` - Enum for relation types
- `SpatiotemporalCoordinate` - (x, y, z, t) representation
- `Entity` - Versioned entities with attributes
- `Fact` - Triple (s, r, o) with coordinates and confidence
- `DomainOntology` - Ontology (C, R_o, A) with constraints
- `PhysicsConstraints` - Physical consistency predicates (Ψ, ψ_s, ψ_t)
- `STKG` - Complete knowledge graph (V, E, O, T, Ψ)

**Key Methods:**
- `spatial_consistency()` - Definition 2 implementation
- `temporal_consistency()` - Definition 3 implementation
- `check_consistency()` - Combined physics validation

#### `src/modules/verification.py` (500+ lines)
**Purpose:** Five verification modules (M1-M5)
**Implements:** Section 3.3.1 from the paper

**Key Classes:**
- `VerificationModule` - Base class with dual-metric design
- `LOV_Module` (M1) - Lexical-Ontological Verification
- `POV_Module` (M2) - Protocol-Ontology Verification
- `MAV_Module` (M3) - Motion-Aware Verification [CRITICAL]
- `WSV_Module` (M4) - Web-Source Verification
- `ESV_Module` (M5) - Embedding Similarity Verification
- `VerificationResult` - Module output dataclass

**Each Module Implements:**
- `_compute_metric1()` - First validation metric
- `_compute_metric2()` - Second validation metric
- `compute_score()` - Equation 6: S_i(d_k) = conf_k × [α_i·M1 + (1-α_i)·M2]

#### `src/modules/rmmve.py` (200+ lines)
**Purpose:** Ranked Multi-Modal Verification Engine
**Implements:** Algorithm 1 from the paper

**Key Classes:**
- `Decision` - Enum (ACCEPT, REJECT, REVIEW)
- `RMMVeEngine` - Verification orchestrator

**Key Methods:**
- `verify()` - Main verification logic with early termination
  - Sequential module execution
  - Activation threshold checking
  - Cumulative confidence computation (Equation 7)
  - Early termination logic
  - Final decision (Equation 8)
- `batch_verify()` - Process multiple facts
- `get_statistics()` - Compute aggregate metrics

### 3. Testing & Documentation

#### `test_verification.py` (100+ lines)
**Purpose:** Unit tests for verification pipeline
**Tests:**
- Module initialization
- Fact creation
- Verification decisions
- Early termination
- Low confidence handling

#### `README.md`
**Purpose:** Complete project documentation
**Sections:**
- Architecture overview
- Installation instructions
- Module descriptions
- Key results
- Citation information

#### `QUICKSTART.md`
**Purpose:** Step-by-step demo guide
**Sections:**
- Running instructions
- Demo walkthrough
- Key demonstrations
- Expected results
- Troubleshooting

#### `PROJECT_STRUCTURE.md` (this file)
**Purpose:** Complete file inventory and documentation

### 4. Configuration Files

#### `requirements.txt`
**Purpose:** Python package dependencies
**Key Packages:**
- streamlit (web interface)
- pandas, numpy (data processing)
- plotly (visualization)
- scikit-learn, scipy (ML utilities)
- pydantic (data validation)

#### `.env.example`
**Purpose:** Environment variable template
**Variables:**
- OPENAI_API_KEY (optional for LLM features)
- OPENAI_MODEL
- DEBUG_MODE

#### `.gitignore`
**Purpose:** Git exclusion patterns
**Excludes:**
- Python cache files
- Virtual environments
- IDE files
- Environment variables
- Generated data

### 5. Utility Scripts

#### `run_demo.sh`
**Purpose:** Convenient demo launcher
**Function:** Starts Streamlit server with proper configuration

## Implementation Mapping to Paper

### Paper Section → Implementation File

| Paper Section | Implementation |
|---------------|----------------|
| Definition 1 (STKG) | `src/models/stkg.py::STKG` |
| Definition 2 (Spatial Consistency) | `src/models/stkg.py::PhysicsConstraints.spatial_consistency()` |
| Definition 3 (Temporal Consistency) | `src/models/stkg.py::PhysicsConstraints.temporal_consistency()` |
| Definition 4-6 (Error Classes) | `src/modules/verification.py` (module targets) |
| Equation 6 (Module Score) | `src/modules/verification.py::VerificationModule.compute_score()` |
| Equation 7 (Cumulative Confidence) | `src/modules/rmmve.py::RMMVeEngine.verify()` |
| Equation 8 (Decision Rule) | `src/modules/rmmve.py::RMMVeEngine.verify()` |
| Algorithm 1 (RMMVe) | `src/modules/rmmve.py::RMMVeEngine.verify()` |
| M1 (LOV) | `src/modules/verification.py::LOV_Module` |
| M2 (POV) | `src/modules/verification.py::POV_Module` |
| M3 (MAV) | `src/modules/verification.py::MAV_Module` |
| M4 (WSV) | `src/modules/verification.py::WSV_Module` |
| M5 (ESV) | `src/modules/verification.py::ESV_Module` |
| Table 5 (Results) | `app.py::show_performance_metrics()` |
| Table 6 (Costs) | `app.py::show_performance_metrics()` |

## Code Statistics

### Lines of Code
- **Total Python:** ~2,500 lines
- **Core Implementation:** ~1,100 lines
  - STKG Models: ~400 lines
  - Verification Modules: ~500 lines
  - RMMVe Engine: ~200 lines
- **Application UI:** ~1,200 lines
- **Tests & Utils:** ~200 lines

### Key Features Implemented
- ✅ Complete STKG data model with versioning
- ✅ Physics-based consistency checking (ψ_s, ψ_t)
- ✅ Five verification modules with dual metrics
- ✅ Early termination logic
- ✅ Batch processing
- ✅ Interactive Streamlit UI
- ✅ Visualization and metrics
- ✅ Sample data generation
- ✅ Unit tests

### Features NOT Implemented (Scope Limitations)
- ❌ Actual LLM extraction (Stage 2) - using pre-generated facts
- ❌ AAIC adaptation logic - parameters are static
- ❌ Real web search (M4) - using simulated results
- ❌ Real embedding computation (M5) - using simulated similarities
- ❌ Production database integration
- ❌ Multi-user support

## Usage Examples

### Run Complete Demo
```bash
./run_demo.sh
# Or: streamlit run app.py
```

### Run Tests
```bash
python test_verification.py
```

### Import as Library
```python
from src.models.stkg import Fact, Entity, EntityClass
from src.modules.verification import MAV_Module
from src.modules.rmmve import RMMVeEngine

# Create fact, run verification
engine = RMMVeEngine(modules=[...])
decision, details = engine.verify(fact)
```

## Customization Points

### 1. Add New Domain
Edit `app.py::initialize_demo_system()`:
- Define new entity classes
- Add relation types
- Update ontology constraints
- Modify standard terminology

### 2. Add New Sample Facts
Edit `app.py::create_sample_facts()`:
- Add fact dictionaries
- Specify coordinates and confidence
- Set expected outcomes

### 3. Tune Parameters
Modify in `initialize_demo_system()`:
- Global threshold (Θ)
- Review margin (ε)
- Module weights (w_i)
- Module thresholds (θ_i)
- Balance factors (α_i)

### 4. Add New Verification Module
Create new class in `src/modules/verification.py`:
- Inherit from `VerificationModule`
- Implement `_compute_metric1()` and `_compute_metric2()`
- Add to module list in `initialize_demo_system()`

## Dependencies Graph

```
app.py
 ├─ src.models.stkg
 └─ src.modules.verification
     └─ src.models.stkg
 └─ src.modules.rmmve
     └─ src.modules.verification
         └─ src.models.stkg
```

## Performance Characteristics

### Memory Usage
- ~50 MB baseline (Streamlit + libraries)
- ~100 KB per fact stored
- ~5 MB for module initialization

### Computational Complexity
- **Per Fact:** O(M × N) where M=modules, N=existing facts
- **Batch:** O(K × M × N) where K=batch size
- **Early Termination:** Reduces to O(k × M × N) where k<K

### Latency
- Minimum: 5 ms (M1 only, early termination)
- Average: 150-250 ms (2-3 modules)
- Maximum: 990 ms (all 5 modules)

## Future Enhancements

### Short Term
1. Add parameter tuning UI
2. Export verification reports
3. Import custom datasets
4. Real-time performance monitoring

### Medium Term
1. Implement AAIC adaptation
2. Add actual LLM integration
3. Real web search for M4
4. Real embeddings for M5

### Long Term
1. Multi-domain support
2. Production database backends
3. API endpoints
4. Distributed processing

---

**Document Version:** 1.0
**Last Updated:** 2025-10-27
**Total Implementation Time:** ~4 hours
**Estimated Review Time:** 30 minutes
