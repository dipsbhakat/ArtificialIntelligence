# LangChain RAG Bot

A Retrieval-Augmented Generation (RAG) bot built with LangChain that can load content from PDFs and answer questions about them.

## Features

- 📄 Load multiple PDF files or entire directories of PDFs
- 🤖 Interactive chat interface using Streamlit
- 🧠 Uses OpenAI GPT models for intelligent responses
- 🔍 Shows source documents for transparency
- 💾 Persistent vector database with ChromaDB
- 🖥️ Both web UI and CLI versions available

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key**
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Add it to the `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

3. **Add PDF Files**
   - Place your PDF files in the `pdfs/` directory, or
   - Upload files directly through the web interface

## Usage

### Web Interface (Recommended)

Run the Streamlit app:
```bash
streamlit run src/rag_bot.py
```

Then:
1. Enter your OpenAI API key in the sidebar
2. Upload PDF files or load from the `pdfs/` directory
3. Wait for processing to complete
4. Start asking questions about your documents!

### Command Line Interface

For testing without the web interface:
```bash
python src/cli_bot.py
```

Make sure to:
1. Set your OpenAI API key in `.env`
2. Add PDF files to the `pdfs/` directory

## How It Works

1. **Document Loading**: PDFs are loaded and parsed using PyPDFLoader
2. **Text Splitting**: Documents are split into manageable chunks
3. **Embeddings**: Text chunks are converted to vector embeddings using OpenAI
4. **Vector Storage**: Embeddings are stored in ChromaDB for fast retrieval
5. **Question Answering**: User questions are matched against relevant chunks
6. **Response Generation**: GPT generates answers based on retrieved context

## Project Structure

```
RAG/
├── src/
│   ├── rag_bot.py      # Streamlit web interface
│   └── cli_bot.py      # Command line interface
├── pdfs/               # Directory for PDF files
├── chroma_db/          # Vector database (created automatically)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## Configuration

You can modify the following settings in the code:

- **Chunk Size**: Adjust `chunk_size` in `RecursiveCharacterTextSplitter`
- **Chunk Overlap**: Adjust `chunk_overlap` for better context preservation
- **Retrieval Count**: Change `k` parameter in retriever for more/fewer sources
- **Model**: Switch between different OpenAI models (gpt-3.5-turbo, gpt-4, etc.)
- **Temperature**: Adjust creativity vs. factualness of responses

## Troubleshooting

**ImportError**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

**OpenAI API Error**: Verify your API key is correct and has sufficient credits.

**PDF Loading Issues**: Ensure PDFs are not password-protected or corrupted.

**Memory Issues**: For large documents, consider reducing chunk size or processing fewer files at once.

## Cost Considerations

This bot uses OpenAI's API which charges per token:
- Embeddings: ~$0.0001 per 1K tokens
- GPT-3.5-turbo: ~$0.001 per 1K tokens
- GPT-4: ~$0.01 per 1K tokens

For cost optimization:
- Use gpt-3.5-turbo instead of gpt-4
- Reduce chunk overlap
- Limit the number of retrieved documents

## License

MIT License - feel free to modify and use for your projects!
