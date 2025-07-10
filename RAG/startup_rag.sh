#!/bin/bash
echo "Starting LangChain RAG Bot on Azure App Service..."

# Set environment
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Go to app directory
cd /home/site/wwwroot

# Install dependencies with correct versions
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
echo "Verifying installations..."
python -c "import streamlit; print('Streamlit installed:', streamlit.__version__)"
python -c "import openai; print('OpenAI installed:', openai.__version__)"
python -c "import langchain; print('LangChain installed:', langchain.__version__)"

# Start the main RAG application
echo "Starting RAG Bot on port ${WEBSITES_PORT:-8080}..."
exec python -m streamlit run src/rag_bot.py \
    --server.port=${WEBSITES_PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
