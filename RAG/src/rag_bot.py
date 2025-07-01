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

# Load environment variables
load_dotenv()


class RAGBot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def validate_api_key(self, api_key):
        """Validate OpenAI API key by making a test call"""
        if not api_key or api_key.strip() == "":
            return False, "API key is empty"
        
        try:
            # Test the API key with a minimal call
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Make a very small test request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True, "API key is valid"
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg:
                return False, "Invalid API key. Please check your key at https://platform.openai.com/api-keys"
            elif "insufficient_quota" in error_msg:
                return False, "API key valid but no credits. Please add billing at https://platform.openai.com/billing"
            else:
                return False, f"API key error: {error_msg}"
    
    def initialize_openai(self, api_key, provider="openai", azure_config=None):
        """Initialize OpenAI or Azure OpenAI with the provided API key and config"""
        if provider == "azure":
            # Azure config must be provided
            if not azure_config or not azure_config.get("api_key") or not azure_config.get("endpoint") or not azure_config.get("deployment") or not azure_config.get("embedding_deployment"):
                st.error("❌ Please provide Azure API key, endpoint, chat deployment name, and embedding deployment name.")
                return False
            os.environ["AZURE_OPENAI_API_KEY"] = azure_config["api_key"]
            os.environ["AZURE_OPENAI_ENDPOINT"] = azure_config["endpoint"]
            os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = azure_config["deployment"]
            os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = azure_config["embedding_deployment"]
            os.environ["AZURE_OPENAI_API_VERSION"] = azure_config.get("api_version", "2024-02-15-preview")
            try:
                from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
                self.embeddings = AzureOpenAIEmbeddings(azure_deployment=azure_config["embedding_deployment"])
                st.success("✅ Azure OpenAI API Key and deployments set!")
                return True
            except Exception as e:
                st.error(f"❌ Azure OpenAI error: {e}")
                return False
        else:
            # Validate the API key first
            is_valid, message = self.validate_api_key(api_key)
            if not is_valid:
                st.error(f"❌ {message}")
                return False
            os.environ["OPENAI_API_KEY"] = api_key
            self.embeddings = OpenAIEmbeddings()
            st.success("✅ OpenAI API Key validated and set!")
            return True
        
    def load_pdfs_from_directory(self, pdf_directory):
        """Load all PDFs from a directory"""
        if not os.path.exists(pdf_directory):
            st.error(f"Directory {pdf_directory} does not exist!")
            return []
            
        # Load PDFs using DirectoryLoader
        loader = DirectoryLoader(
            pdf_directory,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        
        try:
            documents = loader.load()
            st.success(f"Loaded {len(documents)} document pages from PDFs")
            return documents
        except Exception as e:
            st.error(f"Error loading PDFs: {str(e)}")
            return []
    
    def load_single_pdf(self, pdf_file):
        """Load a single PDF file"""
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(
                delete=False, suffix='.pdf'
            ) as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Load the PDF
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            st.success(f"Loaded {len(documents)} pages from {pdf_file.name}")
            return documents
        except Exception as e:
            st.error(f"Error loading PDF {pdf_file.name}: {str(e)}")
            return []
    
    def process_documents(self, documents):
        """Split documents into chunks and create vector store"""
        if not self.embeddings:
            st.error("OpenAI API key is not set or invalid. Please provide a valid key before processing documents.")
            return
        if not documents:
            st.warning("No documents to process!")
            return
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        st.info(f"Split documents into {len(chunks)} chunks")
        
        # Create vector store
        try:
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            st.success("Vector store created successfully!")
            
            # Create QA chain
            self.create_qa_chain()
            
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
    
    def create_qa_chain(self, provider="openai", azure_config=None):
        """Create the QA chain for answering questions"""
        if not self.vectorstore:
            st.error("Vector store not initialized!")
            return
        if provider == "azure":
            try:
                from langchain_openai import AzureChatOpenAI
                llm = AzureChatOpenAI(
                    azure_deployment=azure_config["deployment"],
                    temperature=0.7
                )
            except Exception as e:
                st.error(f"Azure LLM error: {e}")
                return
        else:
            llm = ChatOpenAI(
                temperature=0.7,
                model="gpt-3.5-turbo"
            )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=True,
            verbose=True
        )
        st.success("QA Chain created successfully!")
    
    def ask_question(self, question):
        """Ask a question and get an answer from the RAG system"""
        if not self.qa_chain:
            return "Please load documents first!", []
            
        try:
            result = self.qa_chain({"query": question})
            answer = result["result"]
            source_docs = result["source_documents"]
            
            return answer, source_docs
        except Exception as e:
            return f"Error processing question: {str(e)}", []


def main():
    st.set_page_config(
        page_title="LangChain RAG Bot",
        page_icon="🤖",
        layout="wide"
    )
    st.title("🤖 LangChain RAG Bot")
    st.markdown("Upload PDFs and ask questions about their content!")
    
    # Initialize session state
    if 'rag_bot' not in st.session_state:
        st.session_state.rag_bot = RAGBot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        provider = st.selectbox("Provider", ["OpenAI", "Azure OpenAI"], index=0)
        api_key = None
        azure_config = None
        if provider == "Azure OpenAI":
            azure_api_key = st.text_input("Azure API Key", type="password", value=os.getenv("AZURE_OPENAI_API_KEY", ""))
            azure_endpoint = st.text_input("Azure Endpoint", value=os.getenv("AZURE_OPENAI_ENDPOINT", ""))
            azure_deployment = st.text_input("Azure Chat Deployment Name", value=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", ""))
            azure_embedding_deployment = st.text_input("Azure Embedding Deployment Name", value=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""))
            azure_api_version = st.text_input("Azure API Version", value=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"))
            
            if azure_api_key and azure_endpoint and azure_deployment and azure_embedding_deployment:
                azure_config = {
                    "api_key": azure_api_key,
                    "endpoint": azure_endpoint,
                    "deployment": azure_deployment,
                    "embedding_deployment": azure_embedding_deployment,
                    "api_version": azure_api_version
                }
                st.session_state.rag_bot.initialize_openai(None, provider="azure", azure_config=azure_config)
        else:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", "")
            )
            
            if api_key:
                st.session_state.rag_bot.initialize_openai(api_key, provider="openai")
        
        st.header("Document Upload")
        
        # Option to choose upload method
        upload_method = st.radio(
            "Choose upload method:",
            ["Upload Files", "Load from Directory"]
        )
        
        if upload_method == "Upload Files":
            # File uploader
            uploaded_files = st.file_uploader(
                "Upload PDF files",
                type=['pdf'],
                accept_multiple_files=True
            )
            
            if uploaded_files and st.button("Process Uploaded Files"):
                if provider == "Azure OpenAI":
                    if not azure_config:
                        st.error("Please provide Azure OpenAI credentials first!")
                    else:
                        all_documents = []
                        for uploaded_file in uploaded_files:
                            documents = st.session_state.rag_bot.load_single_pdf(
                                uploaded_file
                            )
                            all_documents.extend(documents)
                        if all_documents:
                            st.session_state.rag_bot.process_documents(
                                all_documents
                            )
                else:
                    if not api_key:
                        st.error("Please provide OpenAI API Key first!")
                    else:
                        all_documents = []
                        for uploaded_file in uploaded_files:
                            documents = st.session_state.rag_bot.load_single_pdf(
                                uploaded_file
                            )
                            all_documents.extend(documents)
                        if all_documents:
                            st.session_state.rag_bot.process_documents(
                                all_documents
                            )
        
        else:
            # Directory path input
            pdf_directory = st.text_input(
                "PDF Directory Path",
                value="./pdfs"
            )
            
            if st.button("Load from Directory"):
                if provider == "Azure OpenAI":
                    if not azure_config:
                        st.error("Please provide Azure OpenAI credentials first!")
                    else:
                        documents = st.session_state.rag_bot.load_pdfs_from_directory(pdf_directory)
                        if documents:
                            st.session_state.rag_bot.process_documents(documents)
                else:
                    if not api_key:
                        st.error("Please provide OpenAI API Key first!")
                    else:
                        documents = st.session_state.rag_bot.load_pdfs_from_directory(pdf_directory)
                        if documents:
                            st.session_state.rag_bot.process_documents(documents)
    
    # Main chat interface
    st.header("Chat with your documents")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("View Sources"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Source {i+1}:**")
                        page_num = source.metadata.get('page', 'Unknown')
                        st.markdown(f"Page: {page_num}")
                        content_preview = source.page_content[:500]
                        st.markdown(f"Content: {content_preview}...")
                        st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        if not st.session_state.rag_bot.qa_chain:
            st.error("Please upload and process documents first!")
        else:
            # Add user message
            user_message = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_message)
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get bot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer, sources = st.session_state.rag_bot.\
                        ask_question(prompt)
                
                st.markdown(answer)
                
                if sources:
                    with st.expander("View Sources"):
                        for i, source in enumerate(sources):
                            st.markdown(f"**Source {i+1}:**")
                            page_num = source.metadata.get('page', 'Unknown')
                            st.markdown(f"Page: {page_num}")
                            content_preview = source.page_content[:500]
                            st.markdown(f"Content: {content_preview}...")
                            st.markdown("---")
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })


if __name__ == "__main__":
    main()
