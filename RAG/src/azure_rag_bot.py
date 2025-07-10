# Azure AI Studio optimized version
import os
import streamlit as st
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
import tempfile

# Load environment variables
load_dotenv()

class AzureRAGBot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        # Use Azure managed identity when possible
        self.use_managed_identity = self._check_managed_identity()
        
    def _check_managed_identity(self):
        """Check if running in Azure with managed identity"""
        try:
            credential = DefaultAzureCredential()
            return True
        except:
            return False
    
    def initialize_azure_openai(self, api_key=None, endpoint=None, chat_deployment=None, embedding_deployment=None, api_version=None):
        """Initialize Azure OpenAI with explicit parameters or environment variables"""
        
        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "https://liftr-platorm-service.cognitiveservices.azure.com/")
        self.chat_deployment = chat_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
        self.embedding_deployment = embedding_deployment or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not all([self.api_key, self.endpoint, self.chat_deployment, self.embedding_deployment]):
            st.error("❌ Missing Azure OpenAI configuration. Please set environment variables or provide parameters.")
            return False
            
        try:
            from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
            
            # Initialize embeddings
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=self.embedding_deployment,
                api_version=self.api_version,
                azure_endpoint=self.endpoint,
                api_key=self.api_key
            )
            
            st.success("✅ Azure OpenAI initialized successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Azure OpenAI initialization error: {e}")
            return False
    
    def load_documents(self, files=None, directory=None):
        """Load documents from files or directory"""
        documents = []
        
        if files:
            for file in files:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    loader = PyPDFLoader(tmp_file_path)
                    docs = loader.load()
                    documents.extend(docs)
                    os.unlink(tmp_file_path)
                    
                except Exception as e:
                    st.error(f"Error loading {file.name}: {e}")
                    
        elif directory and os.path.exists(directory):
            loader = DirectoryLoader(
                directory,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                show_progress=True
            )
            documents = loader.load()
            
        return documents
    
    def create_vectorstore(self, documents):
        """Create vector store from documents"""
        if not self.embeddings:
            st.error("Embeddings not initialized!")
            return False
            
        if not documents:
            st.warning("No documents to process!")
            return False
            
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        st.info(f"Split into {len(chunks)} chunks")
        
        # Create vector store
        try:
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            st.success("✅ Vector store created!")
            return True
            
        except Exception as e:
            st.error(f"Error creating vector store: {e}")
            return False
    
    def create_qa_chain(self):
        """Create QA chain"""
        if not self.vectorstore:
            st.error("Vector store not initialized!")
            return False
            
        try:
            from langchain_openai import AzureChatOpenAI
            
            llm = AzureChatOpenAI(
                azure_deployment=self.chat_deployment,
                api_version=self.api_version,
                temperature=0.7,
                azure_endpoint=self.endpoint,
                api_key=self.api_key
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
                return_source_documents=True,
                verbose=True
            )
            
            st.success("✅ QA Chain created!")
            return True
            
        except Exception as e:
            st.error(f"Error creating QA chain: {e}")
            return False
    
    def ask_question(self, question):
        """Ask question and get answer"""
        if not self.qa_chain:
            return "Please initialize the system first!", []
            
        try:
            result = self.qa_chain.invoke({"query": question})
            return result["result"], result["source_documents"]
        except Exception as e:
            return f"Error: {e}", []

def main():
    st.set_page_config(
        page_title="Azure RAG Bot",
        page_icon="☁️",
        layout="wide"
    )
    
    st.title("☁️ Azure AI Studio RAG Bot")
    st.markdown("Enterprise RAG solution powered by Azure OpenAI")
    
    # Initialize bot
    if 'bot' not in st.session_state:
        st.session_state.bot = AzureRAGBot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Azure OpenAI settings
        st.subheader("Azure OpenAI")
        
        # Auto-detect or manual configuration
        if st.button("🔄 Auto-Initialize with Environment"):
            success = st.session_state.bot.initialize_azure_openai()
            if success:
                st.success("Ready to use!")
        
        st.markdown("---")
        
        # Manual configuration
        with st.expander("Manual Configuration"):
            api_key = st.text_input("API Key", type="password")
            endpoint = st.text_input("Endpoint", value="https://liftr-platorm-service.cognitiveservices.azure.com/")
            chat_deployment = st.text_input("Chat Deployment", value="gpt-4.1")
            embedding_deployment = st.text_input("Embedding Deployment", value="text-embedding-ada-002")
            api_version = st.text_input("API Version", value="2024-12-01-preview")
            
            if st.button("Initialize Manually"):
                success = st.session_state.bot.initialize_azure_openai(
                    api_key, endpoint, chat_deployment, embedding_deployment, api_version
                )
        
        st.markdown("---")
        
        # Document upload
        st.subheader("📄 Documents")
        
        upload_tab = st.radio("Upload Method", ["Files", "Directory"])
        
        if upload_tab == "Files":
            uploaded_files = st.file_uploader(
                "Upload PDFs", 
                type=['pdf'], 
                accept_multiple_files=True
            )
            
            if uploaded_files and st.button("Process Files"):
                documents = st.session_state.bot.load_documents(files=uploaded_files)
                if documents:
                    if st.session_state.bot.create_vectorstore(documents):
                        st.session_state.bot.create_qa_chain()
        
        else:
            directory = st.text_input("PDF Directory", value="./pdfs")
            
            if st.button("Load Directory"):
                documents = st.session_state.bot.load_documents(directory=directory)
                if documents:
                    if st.session_state.bot.create_vectorstore(documents):
                        st.session_state.bot.create_qa_chain()
    
    # Main chat interface
    st.header("💬 Chat with Documents")
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Source {i+1}:**")
                        st.markdown(f"Page: {source.metadata.get('page', 'Unknown')}")
                        st.markdown(f"Content: {source.page_content[:300]}...")
                        st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("Ask about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources = st.session_state.bot.ask_question(prompt)
            
            st.markdown(answer)
            
            if sources:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(sources):
                        st.markdown(f"**Source {i+1}:**")
                        st.markdown(f"Page: {source.metadata.get('page', 'Unknown')}")
                        st.markdown(f"Content: {source.page_content[:300]}...")
                        st.markdown("---")
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

if __name__ == "__main__":
    main()
