# 🚀 Quick Start Guide

## ✅ Environment Setup Complete!

Your LangChain RAG Bot is now fully set up with:
- ✅ Virtual environment created and activated
- ✅ All Python packages installed
- ✅ Project structure created
- ✅ Configuration files ready

## 🏃‍♂️ Quick Start (3 Steps)

### Step 1: Set Your OpenAI API Key
Edit the `.env` file and replace `your_openai_api_key_here` with your actual API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 2: Add PDF Files
Place your PDF documents in the `pdfs/` folder:
```
pdfs/
├── your_document1.pdf
├── your_document2.pdf
└── any_research_paper.pdf
```

### Step 3: Start the Bot
Run this command:
```bash
streamlit run src/rag_bot.py
```

Then open your browser to: `http://localhost:8501`

## 🖥️ Available Commands

### Activate Environment (for future sessions):
```bash
# Windows Command Prompt
activate_env.bat

# Windows PowerShell  
.\activate_env.ps1

# Manual activation
venv\Scripts\activate
```

### Run the Bot:
```bash
# Web interface (recommended)
streamlit run src/rag_bot.py

# Command line interface
python src/cli_bot.py

# Test installation
python test_setup.py
```

## 💡 Pro Tips

1. **Best PDF Types**: Text-based PDFs work better than scanned images
2. **File Size**: Keep PDFs under 50MB for better performance  
3. **Questions**: Ask specific questions for better answers
4. **API Costs**: Monitor usage at https://platform.openai.com/usage

## 🆘 If Something Goes Wrong

1. **Run the test**: `python test_setup.py`
2. **Check your API key** in the `.env` file
3. **Ensure PDFs are in the right folder**
4. **Restart the virtual environment**

## 🎯 Example Questions to Try

- "What are the main points in these documents?"
- "Summarize the key findings"
- "What methodology was used in the research?"
- "Compare the conclusions from different papers"

---

**Your RAG Bot is ready! 🤖📚**
