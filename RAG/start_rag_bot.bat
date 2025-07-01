@echo off
echo Starting LangChain RAG Bot...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting the RAG Bot web interface...
echo Open your browser to http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run src/rag_bot.py

pause
