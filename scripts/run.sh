#!/bin/bash
# ScholAR Startup Script

echo "======================================"
echo "  ScholAR - Autonomous Research Agent"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check if requirements are installed
echo "📦 Checking dependencies..."
python3 -c "import streamlit; import pandas; import plotly; import networkx; print('✓ All dependencies installed')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✓ Dependencies installed successfully"
    else
        echo "✗ Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "🚀 Starting ScholAR..."
echo "Opening: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run Streamlit app
streamlit run streamlit_app.py
