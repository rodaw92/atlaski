#!/bin/bash
# Launch the ATLASky-AI Streamlit Demo

echo "🚀 Starting ATLASky-AI Demo Interface..."
echo ""
echo "The demo will open in your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the demo"
echo ""

streamlit run app.py --server.port 8501 --server.headless true
