"""
Simple script to test OpenAI API key validity
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def test_api_key():
    """Test if the OpenAI API key is valid"""
    
    print("🔑 Testing OpenAI API Key")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ No API key found in .env file")
        print("💡 Please edit the .env file and add your OpenAI API key:")
        print("   OPENAI_API_KEY=sk-your-actual-key-here")
        return False
    
    print(f"🔍 Found API key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Make a simple test call
        print("🧪 Testing API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, just testing the API key"}],
            max_tokens=10
        )
        
        print("✅ API key is VALID!")
        print(f"📝 Test response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API key is INVALID!")
        print(f"🚨 Error: {str(e)}")
        
        if "401" in str(e):
            print("\n💡 Common solutions:")
            print("1. Check if your API key is correctly copied")
            print("2. Verify your OpenAI account has billing set up")
            print("3. Make sure the key hasn't expired")
            print("4. Get a new key from: https://platform.openai.com/api-keys")
        
        return False

def manual_key_test():
    """Allow manual API key entry for testing"""
    print("\n" + "=" * 40)
    print("🔧 Manual API Key Testing")
    print("=" * 40)
    
    api_key = input("Enter your OpenAI API key to test: ").strip()
    
    if not api_key:
        print("❌ No key entered")
        return
    
    try:
        client = OpenAI(api_key=api_key)
        
        print("🧪 Testing manually entered key...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        
        print("✅ Manually entered key is VALID!")
        print(f"💾 You can save this key to .env file:")
        print(f"   OPENAI_API_KEY={api_key}")
        
    except Exception as e:
        print(f"❌ Manually entered key is INVALID!")
        print(f"🚨 Error: {str(e)}")

if __name__ == "__main__":
    success = test_api_key()
    
    if not success:
        print("\n" + "=" * 40)
        choice = input("Would you like to test a key manually? (y/n): ").strip().lower()
        if choice == 'y':
            manual_key_test()
    
    print("\n" + "=" * 40)
    print("📖 How to get a valid OpenAI API key:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key and paste it in the .env file")
    print("5. Make sure your account has billing set up")
    print("=" * 40)
