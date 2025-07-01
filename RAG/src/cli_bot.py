"""
Simple CLI version of the RAG bot for testing without Streamlit
"""

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()


def main():
    print("🤖 LangChain RAG Bot - CLI Version")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set your OPENAI_API_KEY in the .env file")
        return
    
    # Initialize components
    print("🔧 Initializing components...")
    embeddings = OpenAIEmbeddings()
    
    # Load PDFs from directory
    pdf_directory = "./pdfs"
    print(f"📁 Loading PDFs from {pdf_directory}...")
    
    if not os.path.exists(pdf_directory):
        print(f"❌ Directory {pdf_directory} does not exist!")
        print("Please create the 'pdfs' directory and add your PDF files.")
        return
    
    # Check if there are PDF files
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in the pdfs directory!")
        print("Please add some PDF files to the 'pdfs' directory.")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files: {', '.join(pdf_files)}")
    
    # Load documents
    loader = DirectoryLoader(
        pdf_directory,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    
    try:
        documents = loader.load()
        print(f"✅ Loaded {len(documents)} document pages")
    except Exception as e:
        print(f"❌ Error loading PDFs: {str(e)}")
        return
    
    # Split documents
    print("✂️ Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} text chunks")
    
    # Create vector store
    print("🗄️ Creating vector store...")
    try:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        print("✅ Vector store created successfully!")
    except Exception as e:
        print(f"❌ Error creating vector store: {str(e)}")
        return
    
    # Create QA chain
    print("🔗 Creating QA chain...")
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        return_source_documents=True
    )
    print("✅ QA chain ready!")
    
    # Interactive Q&A loop
    print("\n" + "=" * 50)
    print("🎯 Ready for questions! Type 'quit' to exit.")
    print("=" * 50)
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        try:
            print("🤔 Thinking...")
            result = qa_chain({"query": question})
            answer = result["result"]
            sources = result["source_documents"]
            
            print(f"\n🤖 Answer:")
            print("-" * 30)
            print(answer)
            
            if sources:
                print(f"\n📖 Sources ({len(sources)} found):")
                print("-" * 30)
                for i, source in enumerate(sources, 1):
                    page = source.metadata.get('page', 'Unknown')
                    print(f"Source {i} (Page {page}): {source.page_content[:200]}...")
                    print()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
