"""
Configuration settings for the RAG Bot
"""

# OpenAI Settings
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4" for better quality
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1000

# Text Splitting Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Settings
RETRIEVAL_K = 4  # Number of similar chunks to retrieve
SEARCH_TYPE = "similarity"  # or "mmr" for maximum marginal relevance

# Vector Database Settings
PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "rag_documents"

# File Settings
PDF_DIRECTORY = "./pdfs"
SUPPORTED_EXTENSIONS = [".pdf"]

# Streamlit Settings
PAGE_TITLE = "LangChain RAG Bot"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# Display Settings
MAX_CONTENT_PREVIEW = 500  # Characters to show in source preview
SHOW_PROGRESS = True
VERBOSE = True
