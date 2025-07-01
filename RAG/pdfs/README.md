# PDF Files Directory

Place your PDF files in this directory. The RAG bot will automatically load and process all PDF files from here.

## Supported Formats
- PDF files (.pdf)
- Multiple files supported
- Subdirectories are scanned recursively

## Tips
- Use descriptive filenames
- Keep files under 50MB each for better performance
- Avoid password-protected PDFs
- Text-based PDFs work better than image-only PDFs

## Example Structure
```
pdfs/
├── document1.pdf
├── document2.pdf
├── research/
│   ├── paper1.pdf
│   └── paper2.pdf
└── manuals/
    └── user_guide.pdf
```

After adding your PDF files, use either:
- The web interface: `streamlit run src/rag_bot.py`
- The CLI version: `python src/cli_bot.py`
