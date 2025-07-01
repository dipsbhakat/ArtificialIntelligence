# PowerShell script to activate RAG Bot environment

Write-Host ""
Write-Host "🤖 Activating RAG Bot Environment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Set-Location "c:\Users\dipeshbhakat\PersonalCode\RAG"

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host "✅ All packages installed and ready" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 You can now run:" -ForegroundColor Yellow
Write-Host "   - streamlit run src/rag_bot.py    (Web interface)" -ForegroundColor White
Write-Host "   - python src/cli_bot.py          (Command line)" -ForegroundColor White
Write-Host "   - python test_setup.py           (Test installation)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Don't forget to:" -ForegroundColor Cyan
Write-Host "   1. Set your OpenAI API key in .env file" -ForegroundColor White
Write-Host "   2. Add PDF files to the pdfs/ directory" -ForegroundColor White
Write-Host ""
