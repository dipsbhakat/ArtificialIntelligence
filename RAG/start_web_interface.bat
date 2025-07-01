@echo off
echo 🤖 Starting RAG Bot Web Interface...
echo ========================================

REM Navigate to project directory
cd /d "c:\Users\dipeshbhakat\PersonalCode\RAG"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables to skip Streamlit prompts
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_SERVER_HEADLESS=true

echo ✅ Starting Streamlit on http://localhost:8501
echo 🌐 The web interface will open automatically
echo 💡 Press Ctrl+C to stop the server
echo.

REM Start Streamlit
streamlit run src/rag_bot.py --server.headless true --server.port 8501

pause
