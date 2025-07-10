#!/bin/bash

# Simple startup script for Azure App Service
echo "Starting Azure RAG Bot..."
echo "Current working directory: $(pwd)"
echo "Available files: $(ls -la)"

# Set Python path
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Create directories
mkdir -p /home/site/wwwroot/chroma_db

# Change to app directory
cd /home/site/wwwroot

# Check if the main app file exists
if [ ! -f "src/azure_rag_app.py" ]; then
    echo "ERROR: src/azure_rag_app.py not found!"
    echo "Files in src/: $(ls -la src/ 2>/dev/null || echo 'src/ directory not found')"
    exit 1
fi

echo "Found main app file. Starting Streamlit..."

# Start Streamlit with explicit Python path and verbose output
exec python -m streamlit run src/azure_rag_app.py \
    --server.port=${WEBSITES_PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
