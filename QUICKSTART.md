# ATLASky-AI Demo - Quick Start Guide

## 🚀 Running the Demo

### Option 1: Using the startup script
```bash
./run_demo.sh
```

### Option 2: Direct Streamlit command
```bash
streamlit run app.py
```

### Option 3: With custom port
```bash
streamlit run app.py --server.port 8502
```

The demo will automatically open in your default web browser at `http://localhost:8501`

## 📋 Demo Walkthrough

### 1. Overview Page
Start here to understand the system architecture:
- Three-stage pipeline explanation
- Five verification modules (M1-M5)
- Key performance metrics

### 2. Single Fact Verification
Try the interactive verification:
- Select from 5 pre-configured sample facts
- See real-time verification decisions
- Explore detailed module breakdowns
- View score progression visualizations

**Recommended order:**
1. Fact 1 (Valid) - Should ACCEPT with early termination
2. Fact 5 (Physics violation) - Should REJECT, M3 catches it
3. Fact 4 (Low confidence) - Should REJECT, multiple failures

### 3. Batch Processing
Process all sample facts at once:
- See aggregate statistics
- Analyze decision distribution
- Examine module activation patterns
- Compare computational costs

### 4. Module Deep Dive
Explore each verification module:
- **M1 (LOV)**: How ontology validation works
- **M2 (POV)**: Industry standards checking
- **M3 (MAV)**: Physics-based verification ⭐ **Most Critical**
- **M4 (WSV)**: External source corroboration
- **M5 (ESV)**: Embedding-based anomaly detection

### 5. Performance Metrics
Compare with baselines:
- 94% Precision vs. 88% (best baseline)
- 39-57% FPR reduction
- Computational cost breakdown
- Efficiency gains from early termination

## 🎯 Key Demonstrations

### Physics Violation Detection (M3 - MAV)
The most critical capability - only M3 can catch these:

**Example:** Fact 5 in Single Verification
- Entity moves 100+ meters in 45 seconds
- Required velocity: >2.2 m/s
- Exceeds max velocity (5 m/s is limit for manual/forklift)
- **M1, M2, M4, M5 all pass** - only M3 detects the violation!

This demonstrates why spatiotemporal verification is essential.

### Early Termination Efficiency

**Example:** Fact 1 in Single Verification
- High confidence (0.95)
- Perfect ontology compliance
- M1 score exceeds threshold (0.75)
- **Decision: ACCEPT after M1 only**
- Skips M2-M5 → 40% computation savings

### Multi-Threat Detection

**Example:** Fact 4 in Single Verification
- Low LLM confidence (0.45)
- Vague source information
- Multiple module failures
- **Comprehensive rejection** from semantic + physics checks

## 🔍 Understanding the Visualization

### Module Score Bars
- **Green bars**: Activated (score ≥ threshold)
- **Gray bars**: Not activated (score < threshold)
- **Red dashed line**: Global threshold (Θ = 0.75)

### Decision Logic
```
Cumulative Confidence >= 0.75  →  ACCEPT
Cumulative Confidence >= 0.65  →  REVIEW
Cumulative Confidence <  0.65  →  REJECT
```

### Cost Metrics
- **Latency**: Time per module (ms)
- **Cost**: API/compute cost per fact ($)
- **Activation Rate**: % of facts that trigger module

## 📊 Expected Results

When running batch processing on all 5 sample facts:

**Decision Distribution:**
- Accepts: 2 (40%)
- Rejects: 3 (60%)
- Reviews: 0 (0%)

**Module Activation:**
- M1 (LOV): ~100% (always runs first)
- M2 (POV): ~60% (some early terminations)
- M3 (MAV): ~40% (critical for physics)
- M4 (WSV): ~20% (expensive, selective)
- M5 (ESV): ~20% (most expensive, rare)

**Performance:**
- Average latency: ~150-250ms
- Total cost: ~$0.015 for 5 facts
- Early termination: 40% of facts

## 💡 Tips for Your Presentation

1. **Start with Overview**: Explain the three-stage pipeline and five modules

2. **Show Single Verification**: Use Fact 5 to demonstrate M3's criticality
   - Show how M1, M2 pass (semantic validity)
   - Show M3 catches the physics violation
   - Emphasize: "Only 35% of errors are spatiotemporal, but NO other module can catch them"

3. **Run Batch Processing**: Show scalability and aggregate metrics

4. **Deep Dive M3**: Explain spatiotemporal inconsistency detection
   - Spatial consistency (ψ_s)
   - Temporal consistency (ψ_t)
   - Velocity constraints

5. **Show Performance Comparison**: Emphasize FPR reduction
   - ATLASky-AI: 3.2% FPR
   - Best baseline: 6.6% FPR
   - **Translate to real impact:** At 10,500 facts, that's 452 fewer false alarms

## 🐛 Troubleshooting

### Port already in use
```bash
streamlit run app.py --server.port 8502
```

### Module import errors
Make sure you're in the project root directory:
```bash
cd /home/user/atlaski
python test_verification.py  # Should pass
```

### Missing dependencies
```bash
pip install -r requirements.txt
```

## 📝 Customization

### Modify Parameters
In the Streamlit sidebar (future feature):
- Global threshold (Θ)
- Review margin (ε)
- Module weights (w_i)
- Module thresholds (θ_i)

### Add Custom Facts
Edit `app.py`, function `create_sample_facts()` to add your own examples.

### Change Domain
Modify the ontology in `initialize_demo_system()`:
- Entity classes
- Relation types
- Standard terminology
- Physics constraints

## 📚 Related Files

- `app.py` - Main Streamlit interface
- `src/models/stkg.py` - Data structures
- `src/modules/verification.py` - Verification modules
- `src/modules/rmmve.py` - RMMVe engine
- `test_verification.py` - Unit tests
- `README.md` - Full documentation

## 🎓 Paper Sections Demonstrated

- **Section 3.1**: Data Preprocessing
- **Section 3.2**: LLM Extraction
- **Section 3.3**: TruthFlow Verification
- **Section 3.3.1**: RMMVe with 5 modules
- **Section 4**: Experimental evaluation
- **Table 5**: Performance comparison
- **Table 6**: Module activation rates
- **Algorithm 1**: RMMVe execution flow

## ✨ Next Steps

After the demo, consider:
1. Deploying with real aerospace/healthcare data
2. Integrating actual LLM extraction (Stage 2)
3. Enabling AAIC adaptation for production
4. Adding domain-specific ontologies
5. Connecting to external knowledge sources

---

**For questions or issues, refer to README.md or contact the development team.**
