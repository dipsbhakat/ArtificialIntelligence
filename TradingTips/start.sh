#!/bin/bash

# Advanced Trading Dashboard Startup Script

echo "🚀 Starting Advanced Trading Dashboard..."
echo "=================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python is not installed. Please install Python 3.8 or higher."
        exit 1
    else
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python"
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip is not installed. Please install pip."
        exit 1
    else
        PIP_CMD="pip3"
    fi
else
    PIP_CMD="pip"
fi

echo "✅ pip found"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your Azure OpenAI credentials before continuing."
        echo "   Required variables:"
        echo "   - AZURE_OPENAI_KEY"
        echo "   - AZURE_OPENAI_ENDPOINT" 
        echo "   - AZURE_OPENAI_DEPLOYMENT"
        echo ""
        read -p "Press Enter after updating .env file..."
    else
        echo "❌ .env.example file not found. Please create .env file manually."
        exit 1
    fi
else
    echo "✅ .env file found"
fi

# Install dependencies
echo "📦 Installing dependencies..."
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found in PATH. Trying to install..."
    $PIP_CMD install streamlit
fi

echo "🚀 Starting Streamlit application..."
echo "📱 Your browser should open automatically to http://localhost:8501"
echo "🔄 If it doesn't open, manually navigate to: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the application"
echo ""

# Start the Streamlit app
streamlit run enhanced_trading_app.py --server.port 8501 --server.address 0.0.0.0
