import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
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
        # Auto-initialize with Azure OpenAI if environment variables are present
        self.initialize_azure_openai()
        
    def initialize_azure_openai(self):
        """Initialize Azure OpenAI with environment variables"""
        try:
            # Check if all required Azure OpenAI environment variables are present
            required_vars = [
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_ENDPOINT", 
                "AZURE_OPENAI_DEPLOYMENT_NAME",
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                st.error(f"❌ Missing Azure OpenAI environment variables: {', '.join(missing_vars)}")
                return False
                
            # Initialize Azure OpenAI embeddings
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY")
            )
            
            st.success("✅ Azure OpenAI initialized successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Azure OpenAI initialization error: {e}")
            return False
    
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
            st.error("Azure OpenAI is not initialized. Please check your environment variables.")
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
        
        with st.spinner("Splitting documents into chunks..."):
            chunks = text_splitter.split_documents(documents)
            st.info(f"Split into {len(chunks)} chunks")
        
        # Create vector store
        with st.spinner("Creating vector store..."):
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            st.success("Vector store created successfully!")
        
        # Create QA chain
        self.create_qa_chain()
    
    def create_qa_chain(self):
        """Create the QA chain using Azure OpenAI"""
        if not self.vectorstore:
            st.error("Vector store not created. Please process documents first.")
            return
            
        try:
            # Create Azure OpenAI LLM instance
            llm = AzureChatOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                temperature=0.7
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
                return_source_documents=True,
                verbose=True
            )
            st.success("QA Chain created successfully!")
            
        except Exception as e:
            st.error(f"❌ Error creating QA chain: {e}")
    
    def ask_question(self, question):
        """Ask a question and get an answer from the RAG system"""
        if not self.qa_chain:
            return "Please load documents first!", []
            
        try:
            # Use the newer invoke method instead of deprecated __call__
            result = self.qa_chain.invoke({"query": question})
            answer = result["result"]
            source_docs = result["source_documents"]
            
            return answer, source_docs
        except Exception as e:
            return f"Error processing question: {str(e)}", []


def main():
    st.set_page_config(
        page_title="Azure RAG Bot",
        page_icon="🤖",
        layout="wide"
    )
    st.title("🤖 Azure RAG Bot")
    st.markdown("Upload PDFs and ask questions about their content using Azure OpenAI!")
    
    # Initialize session state
    if 'rag_bot' not in st.session_state:
        st.session_state.rag_bot = AzureRAGBot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Show Azure OpenAI configuration
        st.subheader("Azure OpenAI Configuration")
        st.text(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', 'Not set')}")
        st.text(f"Chat Model: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'Not set')}")
        st.text(f"Embedding Model: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'Not set')}")
        
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
                if not st.session_state.rag_bot.embeddings:
                    st.error("Azure OpenAI not initialized. Please check environment variables.")
                else:
                    all_documents = []
                    for uploaded_file in uploaded_files:
                        documents = st.session_state.rag_bot.load_single_pdf(uploaded_file)
                        all_documents.extend(documents)
                    if all_documents:
                        st.session_state.rag_bot.process_documents(all_documents)
        
        else:
            # Directory path input
            pdf_directory = st.text_input(
                "PDF Directory Path",
                value="./pdfs"
            )
            
            if st.button("Load from Directory"):
                if not st.session_state.rag_bot.embeddings:
                    st.error("Azure OpenAI not initialized. Please check environment variables.")
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
                    answer, sources = st.session_state.rag_bot.ask_question(prompt)
                
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
