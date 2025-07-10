#!/bin/bash

echo "=== Azure RAG Bot Startup Script ==="
echo "Current working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Set environment
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Go to app directory
cd /home/site/wwwroot

# List files for debugging
echo "Files in wwwroot:"
ls -la

echo "Files in src:"
ls -la src/ 2>/dev/null || echo "src directory not found"

# Create necessary directories
mkdir -p chroma_db

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify Streamlit installation
echo "Verifying Streamlit installation..."
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"

# Check if hello.py exists, if not create it
if [ ! -f "src/hello.py" ]; then
    echo "Creating hello.py..."
    mkdir -p src
    cat > src/hello.py << 'EOF'
import streamlit as st
import os

st.title("🟢 Hello Azure!")
st.success("If you can see this, Streamlit is working on Azure App Service!")

st.subheader("Environment Check")
azure_vars = {k: v for k, v in os.environ.items() if 'AZURE' in k}
if azure_vars:
    st.write("Azure environment variables found:")
    for key, value in azure_vars.items():
        display_value = value[:10] + "..." if len(value) > 10 else value
        st.write(f"- {key}: {display_value}")
else:
    st.write("No Azure environment variables found")

st.subheader("System Info")
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"Python executable: {os.sys.executable}")
EOF
fi

# Start Streamlit
echo "Starting Streamlit..."
exec python -m streamlit run src/hello.py \
    --server.port=${WEBSITES_PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableXsrfProtection=false
