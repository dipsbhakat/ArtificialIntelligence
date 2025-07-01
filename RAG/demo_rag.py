"""
Demo script to show how the RAG bot processes questions
This simulates the RAG process without requiring API calls
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def demo_rag_process():
    """Demonstrate the RAG document processing without API calls"""
    
    print("🤖 RAG Bot Demo - Document Processing")
    print("=" * 50)
    
    # Check if sample PDF exists
    pdf_path = "pdfs/sample_ai_healthcare_research.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Sample PDF not found at {pdf_path}")
        return
    
    print(f"📄 Loading PDF: {pdf_path}")
    
    # Load the PDF
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        print(f"✅ Successfully loaded {len(documents)} pages")
        
        # Show first page content preview
        if documents:
            first_page = documents[0]
            print(f"\n📖 First page preview (first 300 characters):")
            print("-" * 50)
            print(first_page.page_content[:300] + "...")
            print("-" * 50)
            
        # Split documents into chunks
        print(f"\n✂️ Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} text chunks")
        
        # Show chunk example
        if chunks:
            print(f"\n📝 Example chunk (first 200 characters):")
            print("-" * 50)
            print(chunks[0].page_content[:200] + "...")
            print("-" * 50)
            
        print(f"\n🎯 Sample questions you could ask:")
        sample_questions = [
            "What are the key findings about AI in healthcare?",
            "What accuracy did AI achieve in diagnostic imaging?",
            "How much faster is AI drug discovery?",
            "What are the main challenges mentioned?",
            "What are the recommendations for implementation?"
        ]
        
        for i, question in enumerate(sample_questions, 1):
            print(f"{i}. {question}")
        
        print(f"\n💡 To use the full RAG system:")
        print("1. Open the web interface at http://localhost:8501")
        print("2. Enter your OpenAI API key in the sidebar")
        print("3. Load the PDF using 'Load from Directory'")
        print("4. Ask questions in the chat interface")
        
    except Exception as e:
        print(f"❌ Error loading PDF: {e}")

if __name__ == "__main__":
    demo_rag_process()
