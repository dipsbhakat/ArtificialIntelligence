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
        
        # Helper function to format values properly
        def format_value(value):
            if value is None or pd.isna(value):
                return 'N/A'
            elif isinstance(value, (int, float)):
                if abs(value) >= 1e9:
                    return f"{value/1e9:.2f}B"
                elif abs(value) >= 1e6:
                    return f"{value/1e6:.2f}M"
                elif abs(value) >= 1e3:
                    return f"{value/1e3:.2f}K"
                else:
                    return f"{value:.2f}"
            else:
                return str(value)
        
        return {
            'Name': str(info.get('longName', 'N/A')),
            'Current Price': format_value(info.get('currentPrice')),
            'Market Cap': format_value(info.get('marketCap')),
            'P/E Ratio': format_value(info.get('trailingPE')),
            'EPS': format_value(info.get('trailingEps')),
            'Book Value': format_value(info.get('bookValue')),
            'Debt to Equity': format_value(info.get('debtToEquity')),
            'ROE': format_value(info.get('returnOnEquity')),
            'ROA': format_value(info.get('returnOnAssets')),
            'Sector': str(info.get('sector', 'N/A')),
            'Industry': str(info.get('industry', 'N/A')),
            'Beta': format_value(info.get('beta')),
            '52W High': format_value(info.get('fiftyTwoWeekHigh')),
            '52W Low': format_value(info.get('fiftyTwoWeekLow')),
            'Dividend Yield': format_value(info.get('dividendYield')),
            'Volume': format_value(info.get('volume')),
            'Avg Volume': format_value(info.get('averageVolume'))
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
        return "❌ Azure OpenAI credentials not configured. Please check your .env file."
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2024-02-15-preview"
        )
        
        # Prepare data summary
        if df is None or df.empty:
            return "❌ No data available for analysis."
        
        latest_data = df.tail(5)
        current_price = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1] if 'SMA_20' in df and pd.notna(df['SMA_20'].iloc[-1]) else None
        sma_50 = df['SMA_50'].iloc[-1] if 'SMA_50' in df and pd.notna(df['SMA_50'].iloc[-1]) else None
        rsi = df['RSI'].iloc[-1] if 'RSI' in df and pd.notna(df['RSI'].iloc[-1]) else None
        macd = df['MACD'].iloc[-1] if 'MACD' in df and pd.notna(df['MACD'].iloc[-1]) else None
        
        if analysis_type == "comprehensive":
            prompt = f"""
            Analyze {symbol} stock with the following technical data:
            
            Current Price: ₹{current_price:.2f}
            20-day SMA: {f'₹{sma_20:.2f}' if sma_20 else 'N/A'}
            50-day SMA: {f'₹{sma_50:.2f}' if sma_50 else 'N/A'}
            RSI: {f'{rsi:.2f}' if rsi else 'N/A'}
            MACD: {f'{macd:.4f}' if macd else 'N/A'}
            
            Recent 5-day price data:
            {latest_data[['Close', 'Volume']].to_string()}
            
            Provide a comprehensive analysis including:
            1. Technical outlook (bullish/bearish/neutral)
            2. Key support and resistance levels
            3. Entry and exit recommendations
            4. Risk assessment
            5. Time horizon for the trade
            
            Format as a clear, structured response with specific price levels and reasoning.
            """
        else:
            prompt = f"""
            Quick technical analysis for {symbol}:
            Current Price: ₹{current_price:.2f}
            RSI: {f'{rsi:.2f}' if rsi else 'N/A'}
            
            Provide a concise BUY/SELL/HOLD recommendation with:
            - Target price
            - Stop loss
            - Brief rationale
            """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an expert stock analyst providing technical analysis for Indian stocks. Be specific with price levels and provide actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500 if analysis_type == "quick" else 1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        error_msg = str(e)
        if "unauthorized" in error_msg.lower():
            return "❌ Azure OpenAI authentication failed. Please check your API key."
        elif "not found" in error_msg.lower():
            return "❌ Azure OpenAI deployment not found. Please check your deployment name."
        elif "quota" in error_msg.lower():
            return "❌ Azure OpenAI quota exceeded. Please check your usage limits."
        else:
            return f"❌ Error getting AI analysis: {error_msg}"

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
            api_version="2024-02-15-preview"
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
            messages=[
                {"role": "system", "content": "You are an expert stock analyst providing recommendations for Indian stocks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error getting AI recommendations: {e}"


def get_filtered_stocks(sector_filter=None, market_cap_filter=None, pe_filter=None, price_range=None):
    """Get filtered stock recommendations based on criteria."""
    # Extended Nifty 50 stocks by sector
    stocks_by_sector = {
        "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
        "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
        "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS"],
        "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
        "Auto": ["M&M.NS", "MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS"],
        "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"],
        "Metals": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "COALINDIA.NS"],
        "Telecom": ["BHARTIARTL.NS", "JIO.NS"],
        "Finance": ["BAJFINANCE.NS", "HDFCLIFE.NS", "SBILIFE.NS"]
    }
    
    filtered_stocks = []
    
    try:
        # Get stocks based on sector filter
        if sector_filter and sector_filter != "All":
            stock_list = stocks_by_sector.get(sector_filter, [])
        else:
            stock_list = [stock for stocks in stocks_by_sector.values() for stock in stocks]
        
        for symbol in stock_list[:10]:  # Limit to 10 stocks for performance
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period="1mo")
                
                if hist.empty:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                market_cap = info.get('marketCap', 0)
                pe_ratio = info.get('trailingPE', 0)
                
                # Apply filters
                if price_range:
                    if current_price < price_range[0] or current_price > price_range[1]:
                        continue
                
                if market_cap_filter and market_cap_filter != "All":
                    if market_cap_filter == "Large Cap" and market_cap < 20000000000:  # 20B
                        continue
                    elif market_cap_filter == "Mid Cap" and (market_cap < 5000000000 or market_cap > 20000000000):
                        continue
                    elif market_cap_filter == "Small Cap" and market_cap > 5000000000:
                        continue
                
                if pe_filter and pe_ratio:
                    if pe_filter == "Low PE (<15)" and pe_ratio >= 15:
                        continue
                    elif pe_filter == "Medium PE (15-25)" and (pe_ratio < 15 or pe_ratio > 25):
                        continue
                    elif pe_filter == "High PE (>25)" and pe_ratio <= 25:
                        continue
                
                # Calculate additional metrics
                month_return = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                volume = hist['Volume'].iloc[-1] if not hist['Volume'].empty else 0
                
                filtered_stocks.append({
                    'Symbol': symbol,
                    'Company': info.get('longName', symbol.replace('.NS', ''))[:20],
                    'Price': f"₹{current_price:.2f}",
                    'Market Cap': f"₹{market_cap/1e9:.1f}B" if market_cap else "N/A",
                    'PE Ratio': f"{pe_ratio:.1f}" if pe_ratio else "N/A",
                    '1M Return': f"{month_return:.1f}%",
                    'Volume': f"{volume:,.0f}" if volume else "N/A",
                    'Sector': info.get('sector', 'N/A')
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(filtered_stocks)
    
    except Exception as e:
        st.error(f"Error filtering stocks: {e}")
        return pd.DataFrame()


def get_ai_stock_screener(criteria):
    """Get AI-powered stock screening based on specific criteria."""
    if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
        return "Azure OpenAI credentials not configured."
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2024-02-15-preview"
        )
        
        prompt = f"""
        As an expert stock analyst, recommend Indian stocks based on these criteria:
        
        Investment Strategy: {criteria.get('strategy', 'Growth')}
        Risk Tolerance: {criteria.get('risk', 'Medium')}
        Time Horizon: {criteria.get('time_horizon', '6-12 months')}
        Sector Preference: {criteria.get('sector', 'Any')}
        Investment Amount: {criteria.get('amount', '₹1-5 Lakhs')}
        
        Provide 3-5 specific stock recommendations with:
        1. Stock symbol and name
        2. Current price and target price
        3. Why it fits the criteria
        4. Risk assessment
        5. Entry strategy
        
        Focus on actionable insights for Indian stock market.
        """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an expert Indian stock market analyst providing personalized investment recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error getting AI screening: {e}"

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
        
        # Create tabs for different features
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Top Picks", "🔍 Stock Screener", "📊 Filtered Search", "💡 Smart Assistant"])
        
        with tab1:
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
        
        with tab2:
            st.subheader("🎯 Personalized Stock Screener")
            
            col1, col2 = st.columns(2)
            
            with col1:
                investment_strategy = st.selectbox(
                    "Investment Strategy",
                    ["Growth", "Value", "Dividend", "Momentum", "Conservative"]
                )
                
                risk_tolerance = st.selectbox(
                    "Risk Tolerance",
                    ["Low", "Medium", "High", "Very High"]
                )
                
                time_horizon = st.selectbox(
                    "Investment Time Horizon",
                    ["1-3 months", "3-6 months", "6-12 months", "1-2 years", "Long term (>2 years)"]
                )
            
            with col2:
                sector_preference = st.selectbox(
                    "Sector Preference",
                    ["Any", "Technology", "Banking", "FMCG", "Auto", "Pharma", "Energy", "Metals", "Telecom"]
                )
                
                investment_amount = st.selectbox(
                    "Investment Amount",
                    ["₹50K-1L", "₹1-5L", "₹5-10L", "₹10-25L", "₹25L+"]
                )
                
                market_condition = st.selectbox(
                    "Market Outlook",
                    ["Bullish", "Neutral", "Bearish", "Volatile"]
                )
            
            if st.button("🔍 Get Personalized Recommendations", type="primary"):
                criteria = {
                    'strategy': investment_strategy,
                    'risk': risk_tolerance,
                    'time_horizon': time_horizon,
                    'sector': sector_preference,
                    'amount': investment_amount,
                    'market_outlook': market_condition
                }
                
                with st.spinner("Analyzing your preferences and market conditions..."):
                    screening_results = get_ai_stock_screener(criteria)
                    st.markdown("### 🎯 Personalized Recommendations")
                    st.write(screening_results)
        
        with tab3:
            st.subheader("📊 Advanced Stock Filter")
            
            # Filter controls
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sector_filter = st.selectbox(
                    "Sector",
                    ["All", "Technology", "Banking", "Energy", "FMCG", "Auto", "Pharma", "Metals", "Telecom", "Finance"]
                )
            
            with col2:
                market_cap_filter = st.selectbox(
                    "Market Cap",
                    ["All", "Large Cap", "Mid Cap", "Small Cap"]
                )
            
            with col3:
                pe_filter = st.selectbox(
                    "P/E Ratio",
                    ["All", "Low PE (<15)", "Medium PE (15-25)", "High PE (>25)"]
                )
            
            with col4:
                price_range = st.slider(
                    "Price Range (₹)",
                    min_value=0,
                    max_value=5000,
                    value=(0, 5000),
                    step=50
                )
            
            # Additional filters
            col1, col2 = st.columns(2)
            
            with col1:
                show_only_profitable = st.checkbox("Show only profitable stocks (positive 1M return)")
            
            with col2:
                min_volume = st.number_input("Minimum Daily Volume", min_value=0, value=100000, step=50000)
            
            if st.button("🔍 Apply Filters", type="primary"):
                with st.spinner("Filtering stocks based on your criteria..."):
                    filtered_df = get_filtered_stocks(
                        sector_filter, 
                        market_cap_filter, 
                        pe_filter, 
                        price_range
                    )
                    
                    if not filtered_df.empty:
                        # Apply additional filters
                        if show_only_profitable:
                            try:
                                # Filter for positive returns
                                mask = filtered_df['1M Return'].str.rstrip('%').astype(float) > 0
                                filtered_df = filtered_df[mask]
                            except:
                                st.warning("Could not filter by profitability - some return data may be missing")
                        
                        if min_volume > 0:
                            try:
                                # Filter by minimum volume
                                filtered_df['Volume_Numeric'] = filtered_df['Volume'].str.replace(',', '').replace('N/A', '0').astype(float)
                                filtered_df = filtered_df[filtered_df['Volume_Numeric'] >= min_volume]
                                filtered_df = filtered_df.drop('Volume_Numeric', axis=1)
                            except:
                                st.warning("Could not filter by volume - some volume data may be missing")
                        
                        if not filtered_df.empty:
                            st.markdown("### 📊 Filtered Stock Results")
                            
                            # Display results with enhanced formatting
                            st.dataframe(
                                filtered_df.style.format({
                                    'Price': lambda x: x,
                                    'Market Cap': lambda x: x,
                                    'PE Ratio': lambda x: x,
                                    '1M Return': lambda x: x,
                                    'Volume': lambda x: x
                                }),
                                use_container_width=True,
                                height=400
                            )
                            
                            # Quick stats
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("📊 Total Stocks", len(filtered_df))
                            with col2:
                                try:
                                    profitable_count = len(filtered_df[filtered_df['1M Return'].str.rstrip('%').astype(float) > 0])
                                    st.metric("📈 Profitable", profitable_count)
                                except:
                                    st.metric("📈 Profitable", "N/A")
                            with col3:
                                try:
                                    avg_return = filtered_df['1M Return'].str.rstrip('%').astype(float).mean()
                                    st.metric("📊 Avg Return", f"{avg_return:.1f}%")
                                except:
                                    st.metric("📊 Avg Return", "N/A")
                            with col4:
                                sectors = filtered_df['Sector'].nunique()
                                st.metric("🏢 Sectors", sectors)
                            
                            # Download option
                            csv = filtered_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name=f"filtered_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                            
                            # Additional insights
                            with st.expander("🔍 Detailed Analysis"):
                                if len(filtered_df) > 0:
                                    # Sector distribution
                                    sector_counts = filtered_df['Sector'].value_counts()
                                    fig_sector = px.pie(
                                        values=sector_counts.values, 
                                        names=sector_counts.index,
                                        title="Sector Distribution"
                                    )
                                    st.plotly_chart(fig_sector, use_container_width=True)
                                    
                                    # Performance distribution
                                    try:
                                        returns = filtered_df['1M Return'].str.rstrip('%').astype(float)
                                        fig_returns = px.histogram(
                                            x=returns,
                                            title="1-Month Return Distribution",
                                            nbins=10
                                        )
                                        fig_returns.update_xaxis(title="1-Month Return (%)")
                                        fig_returns.update_yaxis(title="Number of Stocks")
                                        st.plotly_chart(fig_returns, use_container_width=True)
                                    except:
                                        st.info("Could not generate return distribution chart")
                        else:
                            st.warning("⚠️ No stocks found after applying all filters. Try relaxing some criteria.")
                    else:
                        st.warning("⚠️ No stocks found matching your criteria. Try adjusting the filters.")
                        
                        # Suggestions
                        st.info("""
                        **Try these suggestions:**
                        - Select "All" for sector or market cap filters
                        - Increase the price range
                        - Remove P/E ratio restrictions
                        - Decrease minimum volume requirements
                        """)
        
        with tab4:
            st.subheader("💡 Smart Investment Assistant")
            
            st.markdown("""
            Ask specific questions about investments, market conditions, or get tailored advice.
            """)
            
            # Quick action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📈 Best sectors for next quarter"):
                    query = "What are the best performing sectors in Indian stock market for the next quarter based on current trends?"
                    st.session_state['assistant_query'] = query
            
            with col2:
                if st.button("💰 Dividend-paying stocks"):
                    query = "Recommend top dividend-paying stocks in India with consistent dividend history and good yield."
                    st.session_state['assistant_query'] = query
            
            with col3:
                if st.button("⚡ Momentum stocks"):
                    query = "Identify momentum stocks in Indian market with strong price action and technical indicators."
                    st.session_state['assistant_query'] = query
            
            # Custom query input
            custom_query = st.text_area(
                "Ask your investment question:",
                value=st.session_state.get('assistant_query', ''),
                placeholder="e.g., Which stocks are best for long-term investment in current market conditions?"
            )
            
            if st.button("🤖 Get AI Insights", type="primary") and custom_query:
                with st.spinner("Analyzing your question..."):
                    try:
                        client = AzureOpenAI(
                            api_key=AZURE_OPENAI_KEY,
                            azure_endpoint=AZURE_OPENAI_ENDPOINT,
                            api_version="2024-02-15-preview"
                        )
                        
                        response = client.chat.completions.create(
                            model=AZURE_OPENAI_DEPLOYMENT,
                            messages=[
                                {"role": "system", "content": "You are an expert Indian stock market analyst. Provide specific, actionable investment advice with stock recommendations when appropriate."},
                                {"role": "user", "content": custom_query}
                            ],
                            max_tokens=1000,
                            temperature=0.7
                        )
                        
                        st.markdown("### 🎯 AI Investment Insights")
                        st.write(response.choices[0].message.content.strip())
                        
                    except Exception as e:
                        st.error(f"Error getting AI insights: {e}")
        
        # Market Overview (moved to bottom)
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
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nifty 50", f"{current_nifty:.2f}", f"{nifty_change:+.2f} ({nifty_change_pct:+.2f}%)")
                with col2:
                    sentiment = "Bullish 📈" if nifty_change_pct > 0 else "Bearish 📉" if nifty_change_pct < -1 else "Neutral ➡️"
                    st.metric("Market Sentiment", sentiment, "")
                with col3:
                    volatility = "High" if abs(nifty_change_pct) > 2 else "Medium" if abs(nifty_change_pct) > 1 else "Low"
                    st.metric("Volatility", volatility, "")
                with col4:
                    st.metric("Active Filters", "All Sectors", "")
        except Exception as e:
            st.warning("Could not fetch market data.")
        
        # Investment Tips
        with st.expander("💡 Investment Tips & Guidelines"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **📋 Key Investment Principles:**
                - Always do your own research (DYOR)
                - Diversify across sectors and market caps
                - Set clear entry and exit points
                - Use stop losses to manage risk
                - Review and rebalance regularly
                """)
            
            with col2:
                st.markdown("""
                **⚠️ Risk Management:**
                - Never invest more than you can afford to lose
                - Consider your risk tolerance and time horizon
                - Monitor market conditions and news
                - Avoid emotional trading decisions
                - Keep some cash reserves for opportunities
                """)
    
    elif selected == "News & Insights":
        create_news_ui()


if __name__ == "__main__":
    main()
