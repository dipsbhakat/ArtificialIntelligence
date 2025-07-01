@echo off
echo.
echo 🤖 Activating RAG Bot Environment
echo ========================================
echo.

REM Navigate to the project directory
cd /d "c:\Users\dipeshbhakat\PersonalCode\RAG"

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✅ Virtual environment activated
echo ✅ All packages installed and ready
echo.
echo 🚀 You can now run:
echo    - streamlit run src/rag_bot.py    (Web interface)
echo    - python src/cli_bot.py          (Command line)
echo    - python test_setup.py           (Test installation)
echo.
echo 💡 Don't forget to:
echo    1. Set your OpenAI API key in .env file
echo    2. Add PDF files to the pdfs/ directory
echo.

REM Keep the command prompt open
cmd /k
