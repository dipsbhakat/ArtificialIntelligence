@echo off

REM Advanced Trading Dashboard Startup Script for Windows

echo 🚀 Starting Advanced Trading Dashboard...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo 📝 Please edit .env file with your Azure OpenAI credentials before continuing.
        echo    Required variables:
        echo    - AZURE_OPENAI_KEY
        echo    - AZURE_OPENAI_ENDPOINT
        echo    - AZURE_OPENAI_DEPLOYMENT
        echo.
        pause
    ) else (
        echo ❌ .env.example file not found. Please create .env file manually.
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file found
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies. Please check your internet connection and try again.
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

echo 🚀 Starting Streamlit application...
echo 📱 Your browser should open automatically to http://localhost:8501
echo 🔄 If it doesn't open, manually navigate to: http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the application
echo.

REM Start the Streamlit app
streamlit run enhanced_trading_app.py --server.port 8501 --server.address 0.0.0.0

pause
