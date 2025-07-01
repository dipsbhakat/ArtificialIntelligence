# 🤖 LangChain RAG Bot

A powerful Retrieval-Augmented Generation (RAG) bot built with LangChain that can process PDF documents and answer questions about their content using OpenAI's GPT models.

## 🚀 Features

- **📄 PDF Processing**: Automatically loads and processes PDF documents
- **🧠 Intelligent Retrieval**: Uses OpenAI embeddings and ChromaDB for semantic search
- **💬 Interactive Chat**: Beautiful Streamlit web interface with chat history
- **🔍 Source Citations**: Shows which document sections were used for answers
- **⚙️ Configurable**: Easy customization of models, chunk sizes, and retrieval settings
- **🖥️ Dual Interface**: Both web UI and command-line versions
- **📱 Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Windows PowerShell (for Windows users)

## 🛠️ Installation & Setup

### 1. Clone or Download the Project
```bash
# If you have git installed
git clone <your-repo-url>
cd RAG

# Or download and extract the ZIP file
```

### 2. Set Up Virtual Environment
The virtual environment has already been created for you! To activate it:

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
All required packages have been installed! If you need to reinstall them:
```bash
pip install -r requirements.txt
```

### 4. Configure OpenAI API Key
Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Or you can enter it directly in the web interface when running the bot.

### 5. Add Your PDF Documents
Place your PDF files in the `pdfs/` directory:
```
pdfs/
├── document1.pdf
├── document2.pdf
└── research_paper.pdf
```

## 🎯 Usage

### Web Interface (Recommended)
1. Activate the virtual environment (if not already active)
2. Run the Streamlit app:
   ```bash
   streamlit run src/rag_bot.py
   ```
3. Open your browser to `http://localhost:8501`
4. Enter your OpenAI API key in the sidebar
5. Upload PDFs or load from the `pdfs/` directory
6. Start asking questions!

### Command Line Interface
For a simple CLI version:
```bash
python src/cli_bot.py
```

### Quick Start Script (Windows)
Double-click `start_rag_bot.bat` to automatically:
- Activate the virtual environment
- Install any missing dependencies
- Start the web interface

## 🔧 Configuration

Edit `src/config.py` to customize:

- **Model Settings**: Change GPT model, temperature, max tokens
- **Text Processing**: Adjust chunk size and overlap
- **Retrieval**: Modify number of retrieved chunks
- **Database**: Change vector store settings

Example configurations:
```python
# Use GPT-4 for better quality (costs more)
OPENAI_MODEL = "gpt-4"

# Increase chunk size for longer documents
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

# Retrieve more context for complex questions
RETRIEVAL_K = 6
```

## 💡 Usage Tips

### For Best Results:
- Use text-based PDFs (not scanned images)
- Keep individual files under 50MB
- Use descriptive filenames
- Ask specific questions rather than very broad ones

### Example Questions:
- "What are the main conclusions in the research paper?"
- "Summarize the key findings from all documents"
- "What does the manual say about troubleshooting?"
- "Compare the methodologies used in different papers"

## 🏗️ Project Structure

```
RAG/
├── src/
│   ├── rag_bot.py      # Main Streamlit web interface
│   ├── cli_bot.py      # Command line version
│   └── config.py       # Configuration settings
├── pdfs/               # Directory for PDF files
│   └── README.md       # Instructions for adding PDFs
├── venv/               # Virtual environment (already set up)
├── chroma_db/          # Vector database (created automatically)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── start_rag_bot.bat  # Windows launcher script
└── README.md          # This file
```

## 🔍 How It Works

1. **Document Loading**: PDFs are loaded and split into manageable chunks
2. **Embedding Creation**: OpenAI creates vector embeddings for each chunk
3. **Vector Storage**: Embeddings are stored in ChromaDB for fast retrieval
4. **Question Processing**: User questions are embedded and matched against stored chunks
5. **Answer Generation**: GPT generates answers based on retrieved relevant chunks
6. **Source Citation**: Original document sections are provided as references

## 🚨 Troubleshooting

### Common Issues:

**"OpenAI API Key not found"**
- Make sure you've set the API key in `.env` or the web interface
- Check that your API key is valid and has credits

**"No documents found"**
- Ensure PDF files are in the `pdfs/` directory
- Check that files are actually PDF format
- Verify files aren't password-protected

**"Error loading PDFs"**
- Some PDFs may be image-based (scanned documents)
- Try converting to text-based PDFs first
- Check file permissions

**"ChromaDB errors"**
- Delete the `chroma_db/` directory and restart
- Ensure you have write permissions in the project folder

**"Streamlit port already in use"**
- Use a different port: `streamlit run src/rag_bot.py --server.port 8502`
- Or stop other Streamlit processes

### Performance Tips:
- Smaller chunk sizes = more precise answers but slower processing
- Larger chunk sizes = faster processing but potentially less precise
- More retrieved chunks (k value) = better context but higher costs

## 📊 Monitoring Costs

The bot uses OpenAI's API which charges based on usage:
- **Embedding creation**: ~$0.0001 per 1K tokens
- **Chat completions**: ~$0.002 per 1K tokens (GPT-3.5-turbo)
- **GPT-4**: ~$0.03 per 1K tokens (higher quality, higher cost)

Monitor your usage at [OpenAI's usage dashboard](https://platform.openai.com/usage).

## 🔐 Security Notes

- Keep your OpenAI API key secure and never commit it to version control
- The `.env` file is gitignored for security
- Vector databases are stored locally (not sent to external services)
- Consider using environment variables for production deployments

## 🤝 Contributing

Feel free to:
- Add new document loaders (Word, PowerPoint, etc.)
- Implement different embedding models
- Add more advanced retrieval strategies
- Improve the user interface
- Add support for other LLM providers

## 📝 License

This project is open source. Feel free to modify and distribute as needed.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify your OpenAI API key is valid
4. Check the terminal/console for error messages

---

**Happy document chatting! 🚀📚**
