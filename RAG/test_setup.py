"""
Quick test script to verify the RAG bot setup
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    try:
        import langchain
        print("✅ langchain imported successfully")
    except ImportError as e:
        print(f"❌ langchain import failed: {e}")
        return False
    
    try:
        from langchain_community.document_loaders import PyPDFLoader
        print("✅ langchain_community imported successfully")
    except ImportError as e:
        print(f"❌ langchain_community import failed: {e}")
        return False
    
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        print("✅ langchain_openai imported successfully")
    except ImportError as e:
        print(f"❌ langchain_openai import failed: {e}")
        return False
    
    try:
        import streamlit
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import chromadb
        print("✅ chromadb imported successfully")
    except ImportError as e:
        print(f"❌ chromadb import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def check_environment():
    """Check Python environment details"""
    print("\n🔍 Environment Information:")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directories:")
    
    directories = ['pdfs', 'src']
    for dir_name in directories:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
    
    files = ['requirements.txt', '.env', 'src/rag_bot.py', 'src/cli_bot.py']
    for file_name in files:
        if os.path.exists(file_name):
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")

def main():
    print("🤖 RAG Bot Setup Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Check environment
    check_environment()
    
    # Check directories and files
    check_directories()
    
    print("\n" + "=" * 50)
    if imports_ok:
        print("🎉 Setup test PASSED! Your RAG bot is ready to use.")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to the .env file")
        print("2. Place PDF files in the pdfs/ directory")
        print("3. Run: streamlit run src/rag_bot.py")
    else:
        print("❌ Setup test FAILED! Please check the error messages above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
