"""
Simple test script to validate the trading application setup
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported."""
    required_modules = [
        'streamlit',
        'yfinance', 
        'pandas',
        'plotly',
        'numpy',
        'sqlite3',
        'datetime',
        'os'
    ]
    
    optional_modules = [
        'openai',
        'requests', 
        'beautifulsoup4',
        'streamlit_option_menu',
        'st_aggrid'
    ]
    
    print("🧪 Testing Trading Dashboard Dependencies")
    print("=" * 50)
    
    success_count = 0
    total_count = len(required_modules) + len(optional_modules)
    
    print("\n📦 Required Modules:")
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} - {e}")
    
    print("\n📦 Optional Modules:")
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"⚠️  {module} - {e}")
    
    print(f"\n📊 Summary: {success_count}/{total_count} modules available")
    
    if success_count >= len(required_modules):
        print("🎉 All required dependencies are available!")
        return True
    else:
        print("❌ Some required dependencies are missing. Please run: pip install -r requirements.txt")
        return False

def test_basic_functionality():
    """Test basic functionality of the trading modules."""
    print("\n🔧 Testing Basic Functionality")
    print("=" * 50)
    
    try:
        # Test database initialization
        from trade_executor import TradeExecutor
        executor = TradeExecutor()
        print("✅ Database initialization works")
        
        # Test risk management
        from risk_management import RiskManager
        risk_manager = RiskManager()
        print("✅ Risk management module works")
        
        # Test basic stock data fetch (if yfinance is available)
        import yfinance as yf
        stock = yf.Ticker("RELIANCE.NS")
        data = stock.history(period="5d")
        if not data.empty:
            print("✅ Stock data fetching works")
        else:
            print("⚠️  Stock data fetch returned empty (may be network issue)")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def check_environment():
    """Check environment setup."""
    print("\n🌍 Environment Check")
    print("=" * 50)
    
    import os
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        # Check if Azure OpenAI credentials are set
        from dotenv import load_dotenv
        load_dotenv()
        
        azure_key = os.getenv('AZURE_OPENAI_KEY')
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        
        if azure_key and azure_endpoint and azure_deployment:
            print("✅ Azure OpenAI credentials are configured")
        else:
            print("⚠️  Azure OpenAI credentials not fully configured")
            print("   Please update .env file with your credentials")
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and add your credentials")

def main():
    """Run all tests."""
    print("🚀 Advanced Trading Dashboard - System Check")
    print("=" * 60)
    
    imports_ok = test_imports()
    
    if imports_ok:
        functionality_ok = test_basic_functionality()
        check_environment()
        
        print("\n" + "=" * 60)
        if imports_ok and functionality_ok:
            print("🎉 System check complete! You can now run the trading dashboard.")
            print("💡 Run: streamlit run enhanced_trading_app.py")
        else:
            print("⚠️  Some issues found. Please resolve them before running the app.")
    else:
        print("\n❌ Critical dependencies missing. Please install requirements first.")
        print("💡 Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
