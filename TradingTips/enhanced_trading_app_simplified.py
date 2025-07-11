import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from openai import AzureOpenAI
import dotenv
from datetime import datetime, timedelta
import sqlite3
import json
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder
import requests
from bs4 import BeautifulSoup

# Import custom modules
from news_manager import create_news_ui

# Load environment variables
dotenv.load_dotenv()

# --- Configuration ---
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Database setup
def init_database():
    """Initialize SQLite database for trading app."""
    conn = sqlite3.connect('trading_app.db')
    cursor = conn.cursor()
    
    # Basic table for any future needs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            data_type TEXT NOT NULL,
            data_value TEXT,
            created_date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Technical Analysis Functions
def calculate_technical_indicators(df):
    """Calculate various technical indicators."""
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    
    return df

def get_stock_data_with_indicators(symbol, period="1y"):
    """Fetch stock data and calculate technical indicators."""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        if df.empty:
            return None
        df = calculate_technical_indicators(df)
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None

def get_detailed_stock_info(symbol):
    """Get comprehensive stock information."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'Name': info.get('longName', 'N/A'),
            'Current Price': info.get('currentPrice', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'EPS': info.get('trailingEps', 'N/A'),
            'Book Value': info.get('bookValue', 'N/A'),
            'Debt to Equity': info.get('debtToEquity', 'N/A'),
            'ROE': info.get('returnOnEquity', 'N/A'),
            'ROA': info.get('returnOnAssets', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            '52W High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52W Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'Volume': info.get('volume', 'N/A'),
            'Avg Volume': info.get('averageVolume', 'N/A')
        }
    except Exception as e:
        st.error(f"Error fetching info for {symbol}: {e}")
        return {}

def create_candlestick_chart(df, symbol):
    """Create an interactive candlestick chart with technical indicators."""
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=(f'{symbol} Price Action', 'Volume', 'MACD', 'RSI'),
        vertical_spacing=0.05,
        row_heights=[0.5, 0.15, 0.15, 0.15]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Moving averages
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='orange')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='red')),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', line=dict(color='gray', dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', line=dict(color='gray', dash='dash')),
        row=1, col=1
    )
    
    # Volume
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='lightblue'),
        row=2, col=1
    )
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='red')),
        row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram', marker_color='green'),
        row=3, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
        row=4, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=4, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=4, col=1)
    
    fig.update_layout(
        title=f'{symbol} Technical Analysis',
        xaxis_rangeslider_visible=False,
        height=800
    )
    
    return fig

def get_ai_analysis(symbol, df, analysis_type="comprehensive"):
    """Get AI-powered stock analysis using Azure OpenAI."""
    if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
        return "Azure OpenAI credentials not configured."
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2023-05-15"
        )
        
        # Prepare data summary
        latest_data = df.tail(5)
        current_price = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1] if 'SMA_20' in df else None
        sma_50 = df['SMA_50'].iloc[-1] if 'SMA_50' in df else None
        rsi = df['RSI'].iloc[-1] if 'RSI' in df else None
        macd = df['MACD'].iloc[-1] if 'MACD' in df else None
        
        if analysis_type == "comprehensive":
            prompt = f"""
            Analyze {symbol} stock with the following data:
            
            Current Price: {current_price:.2f}
            20-day SMA: {sma_20:.2f if sma_20 else 'N/A'}
            50-day SMA: {sma_50:.2f if sma_50 else 'N/A'}
            RSI: {rsi:.2f if rsi else 'N/A'}
            MACD: {macd:.4f if macd else 'N/A'}
            
            Recent 5-day data:
            {latest_data[['Open', 'High', 'Low', 'Close', 'Volume']].to_string()}
            
            Provide a comprehensive analysis including:
            1. Technical outlook (bullish/bearish/neutral)
            2. Key support and resistance levels
            3. Entry and exit recommendations
            4. Risk assessment
            5. Time horizon for the trade
            
            Be specific with price levels and reasoning.
            """
        else:
            prompt = f"""
            Quick analysis for {symbol}:
            Current Price: {current_price:.2f}
            RSI: {rsi:.2f if rsi else 'N/A'}
            
            Provide: BUY/SELL/HOLD recommendation with target price and stop loss.
            """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500 if analysis_type == "quick" else 1000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error getting AI analysis: {e}"

def get_nifty_top_picks():
    """Get AI recommendations for Nifty 50 stocks."""
    if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
        return "Azure OpenAI credentials not configured."
    
    # Sample Nifty 50 stocks for analysis
    nifty_stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
        "INFY.NS", "ITC.NS", "SBIN.NS", "BAJFINANCE.NS", "BHARTIARTL.NS"
    ]
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2023-05-15"
        )
        
        # Get basic data for top stocks
        stock_data = []
        for symbol in nifty_stocks[:5]:  # Analyze top 5 for performance
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1mo")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    month_return = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                    stock_data.append(f"{symbol}: Price ₹{current_price:.2f}, 1M Return: {month_return:.1f}%")
            except:
                continue
        
        prompt = f"""
        Based on current market conditions and the following Nifty 50 stock data:
        
        {chr(10).join(stock_data)}
        
        Provide your top 3 stock recommendations for the next 1-3 months with:
        1. Stock name and symbol
        2. Target price
        3. Stop loss
        4. Investment rationale
        5. Risk level (Low/Medium/High)
        
        Consider technical analysis, fundamental strength, and market sentiment.
        """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error getting AI recommendations: {e}"

# Main Application
def main():
    st.set_page_config(
        page_title="Advanced Trading Dashboard",
        page_icon="📈",
        layout="wide"
    )
    
    # Initialize database
    init_database()
    
    st.title("🚀 Advanced Trading Dashboard")
    st.markdown("*AI-Powered Stock Analysis & Market Insights*")
    
    # Sidebar navigation
    with st.sidebar:
        selected = option_menu(
            "Trading Dashboard",
            ["Market Analysis", "AI Recommendations", "News & Insights"],
            icons=['graph-up', 'robot', 'newspaper'],
            menu_icon="cast",
            default_index=0
        )
    
    if selected == "Market Analysis":
        st.header("📊 Market Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS)", value="RELIANCE.NS")
            period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        
        with col2:
            analysis_type = st.radio("Analysis Type", ["Quick", "Comprehensive"])
        
        if symbol:
            # Get stock data
            df = get_stock_data_with_indicators(symbol, period)
            
            if df is not None and not df.empty:
                # Display current info
                info = get_detailed_stock_info(symbol)
                
                # Key metrics row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Price", f"₹{info.get('Current Price', 'N/A')}")
                with col2:
                    st.metric("P/E Ratio", info.get('P/E Ratio', 'N/A'))
                with col3:
                    market_cap = info.get('Market Cap', 'N/A')
                    if market_cap != 'N/A' and isinstance(market_cap, (int, float)):
                        st.metric("Market Cap", f"₹{market_cap:,}")
                    else:
                        st.metric("Market Cap", "N/A")
                with col4:
                    rsi_val = df['RSI'].iloc[-1] if 'RSI' in df else 0
                    rsi_color = "red" if rsi_val > 70 else "green" if rsi_val < 30 else "normal"
                    st.metric("RSI", f"{rsi_val:.1f}", delta_color=rsi_color)
                
                # Technical chart
                st.plotly_chart(create_candlestick_chart(df, symbol), use_container_width=True)
                
                # AI Analysis
                st.subheader("🤖 AI Analysis")
                if st.button("Generate Analysis"):
                    with st.spinner("Analyzing..."):
                        analysis = get_ai_analysis(symbol, df, analysis_type.lower())
                        st.write(analysis)
                
                # Detailed info
                with st.expander("📋 Detailed Stock Information"):
                    info_df = pd.DataFrame(list(info.items()), columns=['Metric', 'Value'])
                    st.dataframe(info_df, use_container_width=True)
            else:
                st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")
    
    elif selected == "AI Recommendations":
        st.header("🤖 AI-Powered Recommendations")
        
        st.markdown("""
        Get AI-powered stock recommendations based on technical analysis, 
        fundamental data, and current market conditions.
        """)
        
        # Nifty 50 Analysis
        st.subheader("📈 Nifty 50 Top Picks")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🔍 Get Top AI Picks", type="primary"):
                with st.spinner("Analyzing Nifty 50 stocks..."):
                    recommendations = get_nifty_top_picks()
                    st.markdown("### 🎯 AI Recommendations")
                    st.write(recommendations)
        
        with col2:
            st.info("""
            **Features:**
            - Top 3 stock picks
            - Target prices
            - Stop loss levels
            - Risk assessment
            - Investment rationale
            """)
        
        # Market Overview
        st.subheader("📊 Market Overview")
        
        # Quick market metrics
        try:
            # Get Nifty 50 data
            nifty = yf.Ticker("^NSEI")
            nifty_data = nifty.history(period="5d")
            
            if not nifty_data.empty:
                current_nifty = nifty_data['Close'].iloc[-1]
                prev_close = nifty_data['Close'].iloc[-2] if len(nifty_data) > 1 else current_nifty
                nifty_change = current_nifty - prev_close
                nifty_change_pct = (nifty_change / prev_close) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nifty 50", f"{current_nifty:.2f}", f"{nifty_change:+.2f} ({nifty_change_pct:+.2f}%)")
                with col2:
                    st.metric("Market Sentiment", "Analyzing...", "")
                with col3:
                    st.metric("Volatility", "Medium", "")
        except Exception as e:
            st.warning("Could not fetch market data.")
        
        # Investment Tips
        with st.expander("💡 Investment Tips"):
            st.markdown("""
            **Key Points to Remember:**
            - Always do your own research before investing
            - Diversify your portfolio across sectors
            - Set stop losses to manage risk
            - Consider your investment time horizon
            - Review and rebalance regularly
            """)
    
    elif selected == "News & Insights":
        create_news_ui()


if __name__ == "__main__":
    main()
