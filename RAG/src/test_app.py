import streamlit as st
import os

def main():
    st.set_page_config(
        page_title="Azure RAG Bot - Test",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 Azure RAG Bot - Connection Test")
    
    # Test environment variables
    st.header("Environment Variables Check")
    
    env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Only show first few characters for security
            display_value = value[:8] + "..." if len(value) > 8 else value
            st.success(f"✅ {var}: {display_value}")
        else:
            st.error(f"❌ {var}: Not set")
    
    # Test imports
    st.header("Module Import Test")
    
    try:
        from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
        st.success("✅ LangChain Azure OpenAI imports successful")
    except Exception as e:
        st.error(f"❌ LangChain Azure OpenAI import error: {e}")
    
    try:
        from langchain_community.vectorstores import Chroma
        st.success("✅ ChromaDB import successful")
    except Exception as e:
        st.error(f"❌ ChromaDB import error: {e}")
    
    try:
        from langchain.chains import RetrievalQA
        st.success("✅ RetrievalQA import successful")
    except Exception as e:
        st.error(f"❌ RetrievalQA import error: {e}")
    
    # Test Azure OpenAI connection
    st.header("Azure OpenAI Connection Test")
    
    if st.button("Test Azure OpenAI Connection"):
        try:
            embeddings = AzureOpenAIEmbeddings(
                azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY")
            )
            
            # Test with a simple text
            test_result = embeddings.embed_query("test")
            st.success(f"✅ Azure OpenAI embeddings working! Embedding dimension: {len(test_result)}")
            
        except Exception as e:
            st.error(f"❌ Azure OpenAI connection error: {e}")
    
    st.info("💡 If all tests pass, the Azure RAG Bot should work correctly!")

if __name__ == "__main__":
    main()
