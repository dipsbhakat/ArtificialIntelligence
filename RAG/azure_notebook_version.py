# Azure AI Studio Notebook Version
# Copy this entire content to a new notebook in Azure AI Studio

# Cell 1: Install Dependencies
# !pip install streamlit langchain langchain-openai langchain-community chromadb pypdf python-dotenv

# Cell 2: Import Libraries and Setup
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
import tempfile

# Cell 3: Set Environment Variables (Replace with your actual values)
os.environ["AZURE_OPENAI_API_KEY"] = "your-actual-api-key-here"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://liftr-platorm-service.cognitiveservices.azure.com/"
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4.1"
os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = "text-embedding-ada-002"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"

# Cell 4: RAGBot Class (Copy your entire RAGBot class here)
class RAGBot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def initialize_openai(self, api_key=None, provider="azure", azure_config=None):
        """Initialize Azure OpenAI with environment variables"""
        if provider == "azure":
            azure_config = {
                "api_key": os.environ["AZURE_OPENAI_API_KEY"],
                "endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
                "deployment": os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
                "embedding_deployment": os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
                "api_version": os.environ["AZURE_OPENAI_API_VERSION"]
            }
            
            try:
                from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
                self.embeddings = AzureOpenAIEmbeddings(
                    azure_deployment=azure_config["embedding_deployment"],
                    api_version=azure_config["api_version"],
                    azure_endpoint=azure_config["endpoint"],
                    api_key=azure_config["api_key"]
                )
                print("✅ Azure OpenAI initialized successfully!")
                return True
            except Exception as e:
                print(f"❌ Azure OpenAI error: {e}")
                return False
        return False
    
    def load_pdfs_from_directory(self, pdf_directory="./pdfs"):
        """Load all PDFs from a directory"""
        if not os.path.exists(pdf_directory):
            print(f"Directory {pdf_directory} does not exist!")
            return []
            
        loader = DirectoryLoader(
            pdf_directory,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        
        try:
            documents = loader.load()
            print(f"✅ Loaded {len(documents)} document pages from PDFs")
            return documents
        except Exception as e:
            print(f"❌ Error loading PDFs: {str(e)}")
            return []
    
    def process_documents(self, documents):
        """Split documents into chunks and create vector store"""
        if not self.embeddings:
            print("❌ Embeddings not initialized!")
            return False
        if not documents:
            print("⚠️ No documents to process!")
            return False
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"📄 Split documents into {len(chunks)} chunks")
        
        # Create vector store
        try:
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            print("✅ Vector store created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating vector store: {str(e)}")
            return False
    
    def create_qa_chain(self):
        """Create the QA chain for answering questions"""
        if not self.vectorstore:
            print("❌ Vector store not initialized!")
            return False
            
        try:
            from langchain_openai import AzureChatOpenAI
            
            llm = AzureChatOpenAI(
                azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                temperature=0.7,
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_key=os.environ["AZURE_OPENAI_API_KEY"]
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
                return_source_documents=True,
                verbose=True
            )
            
            print("✅ QA Chain created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating QA chain: {str(e)}")
            return False
    
    def ask_question(self, question):
        """Ask a question and get an answer from the RAG system"""
        if not self.qa_chain:
            return "Please initialize the system first!", []
            
        try:
            result = self.qa_chain.invoke({"query": question})
            answer = result["result"]
            source_docs = result["source_documents"]
            return answer, source_docs
        except Exception as e:
            return f"Error processing question: {str(e)}", []

# Cell 5: Initialize and Test
print("🚀 Initializing RAG Bot...")
bot = RAGBot()

# Initialize Azure OpenAI
if bot.initialize_openai():
    print("✅ Ready to load documents!")
else:
    print("❌ Failed to initialize. Check your environment variables.")

# Cell 6: Load Documents (Choose one option)

# Option A: Load from directory
documents = bot.load_pdfs_from_directory("./pdfs")  # Make sure you have PDFs in this folder

# Option B: Load specific file (uncomment if you want to use this)
# from langchain_community.document_loaders import PyPDFLoader
# loader = PyPDFLoader("path/to/your/file.pdf")
# documents = loader.load()

if documents:
    if bot.process_documents(documents):
        if bot.create_qa_chain():
            print("🎉 RAG Bot is ready! You can now ask questions.")

# Cell 7: Ask Questions
def ask_question(question):
    """Helper function to ask questions"""
    answer, sources = bot.ask_question(question)
    print(f"\n❓ Question: {question}")
    print(f"\n🤖 Answer: {answer}")
    if sources:
        print(f"\n📚 Sources:")
        for i, source in enumerate(sources[:2]):  # Show first 2 sources
            page = source.metadata.get('page', 'Unknown')
            content = source.page_content[:200] + "..."
            print(f"  {i+1}. Page {page}: {content}")
    print("-" * 80)

# Example questions (uncomment to test)
# ask_question("What is this document about?")
# ask_question("What are the main topics covered?")
# ask_question("What are the key findings?")

print("\n✅ Setup complete! Use ask_question('your question here') to interact with your documents.")
