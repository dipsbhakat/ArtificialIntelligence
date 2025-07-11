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
from datetime import datetime
from streamlit_option_menu import option_menu


from news_manager import create_news_ui
from prediction_score import calculate_prediction_score

# Load environment variables
dotenv.load_dotenv()

# --- Configuration ---
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


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

def calculate_enhanced_technical_indicators(df):
    """Calculate enhanced technical indicators for better predictions."""
    try:
        # Existing indicators from calculate_technical_indicators
        df = calculate_technical_indicators(df)
        
        # Advanced momentum indicators
        df['Stoch_K'] = ((df['Close'] - df['Low'].rolling(14).min()) / 
                         (df['High'].rolling(14).max() - df['Low'].rolling(14).min())) * 100
        df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()
        
        # Williams %R
        highest_high = df['High'].rolling(window=14).max()
        lowest_low = df['Low'].rolling(window=14).min()
        df['Williams_R'] = -100 * (highest_high - df['Close']) / (highest_high - lowest_low)
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # Money Flow Index (MFI)
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        mfi_ratio = positive_flow / negative_flow
        df['MFI'] = 100 - (100 / (1 + mfi_ratio))
        
        # Commodity Channel Index (CCI)
        mad = typical_price.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())))
        df['CCI'] = (typical_price - typical_price.rolling(20).mean()) / (0.015 * mad)
        
        # Rate of Change (ROC)
        df['ROC'] = ((df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12)) * 100
        
        # Support and Resistance levels
        df['Resistance_20'] = df['High'].rolling(20).max()
        df['Support_20'] = df['Low'].rolling(20).min()
        df['Distance_to_Resistance'] = (df['Resistance_20'] - df['Close']) / df['Close'] * 100
        df['Distance_to_Support'] = (df['Close'] - df['Support_20']) / df['Close'] * 100
        
        # Price patterns
        df['Higher_High'] = ((df['High'] > df['High'].shift(1)) & (df['High'].shift(1) > df['High'].shift(2))).astype(int)
        df['Lower_Low'] = ((df['Low'] < df['Low'].shift(1)) & (df['Low'].shift(1) < df['Low'].shift(2))).astype(int)
        
        # Volatility indicators
        df['Volatility'] = df['Close'].pct_change().rolling(20).std() * np.sqrt(252)  # Annualized
        df['BB_Squeeze'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        return df
    except Exception as e:
        st.warning(f"Error calculating enhanced indicators: {e}")
        return df


def get_comprehensive_stock_analysis(symbol):
    """Get comprehensive analysis with fundamental and technical data."""
    try:
        stock = yf.Ticker(symbol)
        
        # Get stock info
        info = stock.info
        
        # Get historical data
        df = stock.history(period="1y")
        if df.empty:
            return None
        
        # Calculate enhanced indicators
        df = calculate_enhanced_technical_indicators(df)
        
        current_price = df['Close'].iloc[-1]
        
        # Technical analysis summary
        latest = df.iloc[-1]
        technical_signals = {
            'RSI': 'Overbought' if latest['RSI'] > 70 else 'Oversold' if latest['RSI'] < 30 else 'Neutral',
            'RSI_Value': latest['RSI'],
            'MACD_Signal': 'Bullish' if latest['MACD'] > latest['MACD_Signal'] else 'Bearish',
            'MACD_Value': latest['MACD'],
            'BB_Position': 'Upper' if current_price > latest['BB_Upper'] else 'Lower' if current_price < latest['BB_Lower'] else 'Middle',
            'Stochastic': 'Overbought' if latest['Stoch_K'] > 80 else 'Oversold' if latest['Stoch_K'] < 20 else 'Neutral',
            'Williams_R': 'Overbought' if latest['Williams_R'] > -20 else 'Oversold' if latest['Williams_R'] < -80 else 'Neutral',
            'MFI': 'Overbought' if latest['MFI'] > 80 else 'Oversold' if latest['MFI'] < 20 else 'Neutral',
            'CCI': 'Overbought' if latest['CCI'] > 100 else 'Oversold' if latest['CCI'] < -100 else 'Neutral',
            'Volume_Trend': 'High' if latest['Volume_Ratio'] > 1.5 else 'Normal',
            'Trend_Direction': 'Uptrend' if current_price > latest['SMA_50'] else 'Downtrend',
            'Volatility': 'High' if latest['Volatility'] > 0.3 else 'Medium' if latest['Volatility'] > 0.2 else 'Low'
        }
        
        # Support and Resistance
        support_resistance = {
            'support_20d': latest['Support_20'],
            'resistance_20d': latest['Resistance_20'],
            'distance_to_support': latest['Distance_to_Support'],
            'distance_to_resistance': latest['Distance_to_Resistance']
        }
        
        # Fundamental metrics
        fundamentals = {
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'debt_to_equity': info.get('debtToEquity'),
            'roe': info.get('returnOnEquity'),
            'profit_margin': info.get('profitMargins'),
            'market_cap': info.get('marketCap'),
            'beta': info.get('beta'),
            'dividend_yield': info.get('dividendYield')
        }
        
        # Price momentum analysis
        returns_1d = (current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
        returns_1w = (current_price - df['Close'].iloc[-6]) / df['Close'].iloc[-6] * 100 if len(df) >= 6 else 0
        returns_1m = (current_price - df['Close'].iloc[-21]) / df['Close'].iloc[-21] * 100 if len(df) >= 21 else 0
        returns_3m = (current_price - df['Close'].iloc[-63]) / df['Close'].iloc[-63] * 100 if len(df) >= 63 else 0
        
        momentum = {
            '1_day': returns_1d,
            '1_week': returns_1w,
            '1_month': returns_1m,
            '3_month': returns_3m
        }
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'technical_signals': technical_signals,
            'support_resistance': support_resistance,
            'fundamentals': fundamentals,
            'momentum': momentum,
            'company_info': {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
        }
        
    except Exception as e:
        st.error(f"Error in comprehensive analysis: {e}")
        return None


def get_ai_analysis(symbol, df, analysis_type="comprehensive"):
    """Get enhanced AI-powered stock analysis using Azure OpenAI."""
    if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
        return "❌ Azure OpenAI credentials not configured. Please check your .env file."
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2024-02-15-preview"
        )
        
        # Get comprehensive analysis data
        analysis_data = get_comprehensive_stock_analysis(symbol)
        
        if not analysis_data:
            return "❌ Could not gather comprehensive data for analysis."
        
        # Create enhanced prompt with all available data
        tech_signals = analysis_data['technical_signals']
        support_resistance = analysis_data['support_resistance']
        fundamentals = analysis_data['fundamentals']
        momentum = analysis_data['momentum']
        company_info = analysis_data['company_info']
        current_price = analysis_data['current_price']
        
        if analysis_type == "comprehensive":
            stoch_k_val = df['Stoch_K'].iloc[-1] if 'Stoch_K' in df.columns else 'N/A'
            prompt = f"""
            Perform a comprehensive analysis of {symbol} ({company_info['name']}) stock:
            
            CURRENT MARKET DATA:
            - Current Price: ₹{current_price:.2f}
            - Sector: {company_info['sector']}
            - Industry: {company_info['industry']}
            
            TECHNICAL INDICATORS:
            - RSI: {tech_signals['RSI']} (Value: {tech_signals['RSI_Value']:.1f})
            - MACD Signal: {tech_signals['MACD_Signal']} (Value: {tech_signals['MACD_Value']:.4f})
            - Bollinger Bands: Price at {tech_signals['BB_Position']} band
            - Stochastic: {tech_signals['Stochastic']} (Stoch_K: {stoch_k_val})
            - Williams %R: {tech_signals['Williams_R']}
            - Money Flow Index: {tech_signals['MFI']}
            - CCI: {tech_signals['CCI']}
            - Volume Trend: {tech_signals['Volume_Trend']}
            - Overall Trend: {tech_signals['Trend_Direction']}
            - Volatility: {tech_signals['Volatility']}
            
            SUPPORT & RESISTANCE:
            - 20-day Support: ₹{support_resistance['support_20d']:.2f} (Distance: {support_resistance['distance_to_support']:.1f}%)
            - 20-day Resistance: ₹{support_resistance['resistance_20d']:.2f} (Distance: {support_resistance['distance_to_resistance']:.1f}%)
            
            MOMENTUM ANALYSIS:
            - 1-Day Return: {momentum['1_day']:.2f}%
            - 1-Week Return: {momentum['1_week']:.2f}%
            - 1-Month Return: {momentum['1_month']:.2f}%
            - 3-Month Return: {momentum['3_month']:.2f}%
            
            FUNDAMENTAL METRICS:
            - P/E Ratio: {fundamentals['pe_ratio']}
            - P/B Ratio: {fundamentals['pb_ratio']}
            - Debt-to-Equity: {fundamentals['debt_to_equity']}
            - ROE: {fundamentals['roe']}
            - Profit Margin: {fundamentals['profit_margin']}
            - Beta: {fundamentals['beta']}
            - Dividend Yield: {fundamentals['dividend_yield']}
            
            Based on this comprehensive data, provide:
            
            1. **RECOMMENDATION**: Clear BUY/SELL/HOLD with confidence level (1-10)
            2. **TARGET PRICES**: Conservative, moderate, and aggressive targets
            3. **RISK MANAGEMENT**: Stop-loss levels and position sizing
            4. **ENTRY STRATEGY**: Optimal entry points and timing
            5. **TIME HORIZON**: Short-term (1-4 weeks) and medium-term (1-3 months) outlook
            6. **KEY CATALYSTS**: Events or factors that could drive price movement
            7. **RISK FACTORS**: Major risks to watch
            
            Provide specific price levels, percentages, and actionable insights.
            Consider the convergence/divergence of technical and fundamental factors.
            """
        else:
            # Quick analysis with key metrics
            prompt = f"""
            Quick analysis for {symbol}:
            
            Current Price: ₹{current_price:.2f}
            RSI: {tech_signals['RSI']} ({tech_signals['RSI_Value']:.1f})
            MACD: {tech_signals['MACD_Signal']}
            Trend: {tech_signals['Trend_Direction']}
            Support: ₹{support_resistance['support_20d']:.2f}
            Resistance: ₹{support_resistance['resistance_20d']:.2f}
            1-Month Return: {momentum['1_month']:.1f}%
            
            Provide:
            - BUY/SELL/HOLD recommendation with confidence (1-10)
            - Target price and stop loss
            - Key reason for recommendation
            - Risk level (Low/Medium/High)
            """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an expert Indian stock analyst with 15+ years experience. Provide specific, actionable insights with exact price levels. Consider both technical and fundamental factors. Be confident but realistic in your predictions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800 if analysis_type == "quick" else 1500,
            temperature=0.6
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
    """Get AI recommendations for Nifty 50 stocks with enhanced prediction scoring."""
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
        
        # Get enhanced data for top stocks with prediction scores
        stock_analysis = []
        for symbol in nifty_stocks[:5]:  # Analyze top 5 for performance
            try:
                # Get stock data with technical indicators
                df = get_stock_data_with_indicators(symbol, period="3mo")
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    month_return = ((current_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                    
                    # Calculate prediction score
                    pred_score, recommendation = calculate_prediction_score(df)
                    
                    # Get recent trend
                    week_return = ((current_price - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100 if len(df) >= 5 else 0
                    
                    # Technical indicators summary
                    rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
                    macd = df['MACD'].iloc[-1] if 'MACD' in df.columns else 0
                    
                    stock_analysis.append({
                        'symbol': symbol,
                        'price': current_price,
                        'month_return': month_return,
                        'week_return': week_return,
                        'prediction_score': pred_score,
                        'recommendation': recommendation,
                        'rsi': rsi,
                        'macd': macd
                    })
            except Exception as e:
                st.warning(f"Could not analyze {symbol}: {str(e)}")
                continue
        
        if not stock_analysis:
            return "Unable to analyze stocks at this time. Please try again later."
        
        # Sort by prediction score
        stock_analysis.sort(key=lambda x: x['prediction_score'], reverse=True)
        
        # Create enhanced analysis text
        analysis_text = "**Current Market Analysis:**\n\n"
        for i, stock in enumerate(stock_analysis):
            analysis_text += f"{i+1}. **{stock['symbol']}** - Price: ₹{stock['price']:.2f}\n"
            analysis_text += f"   - Prediction Score: {stock['prediction_score']}/100 ({stock['recommendation']})\n"
            analysis_text += f"   - 1M Return: {stock['month_return']:.1f}% | 1W Return: {stock['week_return']:.1f}%\n"
            analysis_text += f"   - RSI: {stock['rsi']:.1f} | MACD: {stock['macd']:.4f}\n\n"
        
        # Enhanced AI prompt with prediction scores
        prompt = f"""
        As an expert Indian stock market analyst, analyze the following comprehensive stock data with prediction scores:

        {analysis_text}

        Based on this technical analysis and prediction scoring (0-100 scale), provide your TOP 3 STOCK RECOMMENDATIONS for the next 1-3 months:

        For EACH recommendation, provide:
        1. **Stock Name & Symbol**
        2. **Current Analysis** (why this stock is recommended)
        3. **Target Price** (realistic based on current price and trends)
        4. **Stop Loss** (risk management level)
        5. **Investment Rationale** (fundamental + technical reasons)
        6. **Risk Level** (Low/Medium/High)
        7. **Time Horizon** (Short/Medium/Long term outlook)
        8. **Key Catalysts** (what could drive the stock higher)

        Consider:
        - Technical indicators (RSI, MACD, moving averages)
        - Prediction scores and recommendations
        - Recent price momentum and volume
        - Market sentiment and sector trends
        - Risk-reward ratio

        Present each recommendation in a clear, structured format with specific actionable insights.
        """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a senior equity research analyst with 15+ years of experience in Indian stock markets. Provide detailed, actionable investment recommendations with specific price targets and risk assessments."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.6
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
    """Get AI-powered stock screening based on specific criteria with prediction scores."""
    if not all([AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
        return "Azure OpenAI credentials not configured."
    
    # Expanded stock universe based on sector preference
    sector_stocks = {
        'Technology': ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
        'Banking': ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
        'FMCG': ["HINDUNILVR.NS", "NESTLEIND.NS", "ITC.NS", "BRITANNIA.NS"],
        'Auto': ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS"],
        'Pharma': ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"],
        'Energy': ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS"],
        'Any': ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "INFY.NS"]
    }
    
    sector = criteria.get('sector', 'Any')
    stocks_to_analyze = sector_stocks.get(sector, sector_stocks['Any'])
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2024-02-15-preview"
        )
        
        # Analyze stocks with prediction scores
        stock_analysis = []
        for symbol in stocks_to_analyze[:6]:  # Analyze top 6 stocks
            try:
                df = get_stock_data_with_indicators(symbol, period="3mo")
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    pred_score, recommendation = calculate_prediction_score(df)
                    
                    # Calculate performance metrics
                    month_return = ((current_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                    volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility
                    
                    stock_analysis.append({
                        'symbol': symbol,
                        'price': current_price,
                        'prediction_score': pred_score,
                        'recommendation': recommendation,
                        'month_return': month_return,
                        'volatility': volatility
                    })
            except Exception as e:
                continue
        
        if not stock_analysis:
            return "Unable to analyze stocks for the selected criteria. Please try again."
        
        # Sort by prediction score and filter based on criteria
        stock_analysis.sort(key=lambda x: x['prediction_score'], reverse=True)
        
        # Filter based on risk tolerance
        risk_tolerance = criteria.get('risk', 'Medium')
        if risk_tolerance == 'Low':
            stock_analysis = [s for s in stock_analysis if s['volatility'] < 25]
        elif risk_tolerance == 'High':
            stock_analysis = [s for s in stock_analysis if s['prediction_score'] >= 60]
        
        # Create analysis summary
        analysis_summary = f"**Screening Results for {sector} Sector:**\n\n"
        for i, stock in enumerate(stock_analysis[:5]):
            analysis_summary += f"{i+1}. **{stock['symbol']}** - ₹{stock['price']:.2f}\n"
            analysis_summary += f"   - Prediction Score: {stock['prediction_score']}/100 ({stock['recommendation']})\n"
            analysis_summary += f"   - 3M Return: {stock['month_return']:.1f}% | Volatility: {stock['volatility']:.1f}%\n\n"
        
        # Enhanced prompt with prediction data
        prompt = f"""
        As an expert Indian stock analyst, provide personalized recommendations based on:

        **Investment Criteria:**
        - Strategy: {criteria.get('strategy', 'Growth')}
        - Risk Tolerance: {criteria.get('risk', 'Medium')}
        - Time Horizon: {criteria.get('time_horizon', '6-12 months')}
        - Sector: {criteria.get('sector', 'Any')}
        - Investment Amount: {criteria.get('amount', '₹1-5L')}
        - Market Outlook: {criteria.get('market_outlook', 'Neutral')}

        **Stock Analysis with Prediction Scores:**
        {analysis_summary}

        Provide your TOP 3-4 PERSONALIZED RECOMMENDATIONS with:

        1. **Stock Selection & Rationale** (why it matches the criteria)
        2. **Current Price & Target Price** (realistic based on analysis)
        3. **Investment Strategy** (entry points, position sizing)
        4. **Risk Assessment** (specific to user's risk tolerance)
        5. **Time Horizon Fit** (short/medium/long term outlook)
        6. **Sector Analysis** (why this sector fits current market)
        7. **Action Plan** (when to buy, hold, review)

        Consider the prediction scores, volatility, and user's specific requirements.
        Provide actionable, personalized advice with specific entry and exit strategies.
        """
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": f"You are a certified financial planner specializing in Indian equities. Provide personalized investment advice for {risk_tolerance} risk investors with {criteria.get('time_horizon', '6-12 months')} investment horizon."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.6
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
    
    st.title("🚀 Advanced Trading Dashboard")
    st.markdown("*AI-Powered Stock Analysis & Market Insights*")
    
    # Sidebar navigation
    with st.sidebar:
        selected = option_menu(
            "Trading Dashboard",
            ["Market Analysis", "AI Recommendations", "Advanced Predictions", "News & Insights"],
            icons=['graph-up', 'robot', 'brain', 'newspaper'],
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
                **Enhanced Features:**
                - AI-powered prediction scoring (0-100)
                - Technical indicator analysis
                - Target prices & stop losses
                - Risk assessment & recommendations
                - Comprehensive investment rationale
                - Real-time market sentiment
                """)
                
                st.success("""
                **Prediction Score Guide:**
                - 75-100: Strong Buy
                - 65-74: Buy  
                - 55-64: Weak Buy
                - 45-54: Hold
                - 25-44: Sell
                - 0-24: Strong Sell
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
    
    elif selected == "Advanced Predictions":
        st.header("🧠 Advanced Prediction Engine")
        st.markdown("*Enhanced AI predictions with comprehensive technical and fundamental analysis*")
        
        # Input section
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            symbol = st.text_input("Enter Stock Symbol for Advanced Analysis", value="RELIANCE.NS")
        with col2:
            prediction_type = st.selectbox("Prediction Type", ["Comprehensive", "Quick", "Multi-Timeframe"])
        with col3:
            confidence_threshold = st.slider("Min Confidence", 50, 95, 75)
        
        if symbol and st.button("🚀 Generate Advanced Prediction", type="primary"):
            with st.spinner("Running advanced analysis..."):
                
                # Get comprehensive analysis
                analysis_data = get_comprehensive_stock_analysis(symbol)
                
                if analysis_data:
                    current_price = analysis_data['current_price']
                    tech_signals = analysis_data['technical_signals']
                    support_resistance = analysis_data['support_resistance']
                    fundamentals = analysis_data['fundamentals']
                    momentum = analysis_data['momentum']
                    company_info = analysis_data['company_info']
                    
                    # Display key metrics dashboard
                    st.subheader(f"📊 {company_info['name']} Analysis Dashboard")
                    
                    # Key metrics row
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Current Price", f"₹{current_price:.2f}")
                    with col2:
                        rsi_color = "🔴" if tech_signals['RSI_Value'] > 70 else "🟢" if tech_signals['RSI_Value'] < 30 else "🟡"
                        st.metric("RSI", f"{tech_signals['RSI_Value']:.1f} {rsi_color}")
                    with col3:
                        trend_color = "🟢" if tech_signals['Trend_Direction'] == 'Uptrend' else "🔴"
                        st.metric("Trend", f"{tech_signals['Trend_Direction']} {trend_color}")
                    with col4:
                        momentum_color = "🟢" if momentum['1_month'] > 0 else "🔴"
                        st.metric("1M Return", f"{momentum['1_month']:.1f}% {momentum_color}")
                    with col5:
                        vol_color = "🔴" if tech_signals['Volatility'] == 'High' else "🟡" if tech_signals['Volatility'] == 'Medium' else "🟢"
                        st.metric("Volatility", f"{tech_signals['Volatility']} {vol_color}")
                    
                    # Technical signals overview
                    st.subheader("⚡ Technical Signals Summary")
                    
                    signal_cols = st.columns(4)
                    signals = [
                        ("RSI", tech_signals['RSI']),
                        ("MACD", tech_signals['MACD_Signal']),
                        ("Stochastic", tech_signals['Stochastic']),
                        ("Williams %R", tech_signals['Williams_R'])
                    ]
                    
                    for i, (indicator, signal) in enumerate(signals):
                        with signal_cols[i]:
                            color = "🟢" if signal in ['Neutral', 'Bullish'] else "🔴" if signal in ['Overbought', 'Bearish'] else "🟡"
                            st.metric(indicator, f"{signal} {color}")
                    
                    # Support and Resistance levels
                    st.subheader("📈 Key Levels")
                    
                    level_cols = st.columns(4)
                    with level_cols[0]:
                        st.metric("Support", f"₹{support_resistance['support_20d']:.2f}", 
                                f"{support_resistance['distance_to_support']:.1f}% away")
                    with level_cols[1]:
                        st.metric("Resistance", f"₹{support_resistance['resistance_20d']:.2f}", 
                                f"{support_resistance['distance_to_resistance']:.1f}% away")
                    with level_cols[2]:
                        pe_ratio = fundamentals.get('pe_ratio', 'N/A')
                        st.metric("P/E Ratio", pe_ratio if pe_ratio != 'N/A' else 'N/A')
                    with level_cols[3]:
                        beta = fundamentals.get('beta', 'N/A')
                        beta_str = f"{beta:.2f}" if isinstance(beta, (int, float)) else 'N/A'
                        st.metric("Beta", beta_str)
                    
                    # Enhanced AI Analysis
                    st.subheader("🤖 Enhanced AI Prediction")
                    
                    # Get stock data for AI analysis
                    df = get_stock_data_with_indicators(symbol, "1y")
                    if df is not None:
                        df = calculate_enhanced_technical_indicators(df)
                        
                        analysis = get_ai_analysis(symbol, df, prediction_type.lower())
                        
                        # Display AI analysis in a nice format
                        st.markdown("### 🎯 AI Analysis Results")
                        st.write(analysis)
                        
                        # Additional insights based on convergence of signals
                        st.subheader("🔍 Signal Convergence Analysis")
                        
                        # Count bullish vs bearish signals
                        bullish_signals = 0
                        total_signals = 0
                        
                        signal_analysis = {
                            'RSI': tech_signals['RSI'] in ['Oversold', 'Neutral'],
                            'MACD': tech_signals['MACD_Signal'] == 'Bullish',
                            'Trend': tech_signals['Trend_Direction'] == 'Uptrend',
                            'Momentum': momentum['1_month'] > 0,
                            'Volume': tech_signals['Volume_Trend'] == 'High'
                        }
                        
                        for signal, is_bullish in signal_analysis.items():
                            total_signals += 1
                            if is_bullish:
                                bullish_signals += 1
                        
                        signal_strength = (bullish_signals / total_signals) * 100
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Signal Strength", f"{signal_strength:.0f}%")
                        with col2:
                            overall_sentiment = "Bullish" if signal_strength > 60 else "Bearish" if signal_strength < 40 else "Neutral"
                            sentiment_color = "🟢" if overall_sentiment == "Bullish" else "🔴" if overall_sentiment == "Bearish" else "🟡"
                            st.metric("Overall Sentiment", f"{overall_sentiment} {sentiment_color}")
                        with col3:
                            confidence = min(95, max(50, signal_strength + 10))
                            conf_color = "🟢" if confidence >= confidence_threshold else "🟡"
                            st.metric("Confidence", f"{confidence:.0f}% {conf_color}")
                        
                        # Risk assessment
                        st.subheader("⚠️ Risk Assessment")
                        
                        risk_factors = []
                        if tech_signals['Volatility'] == 'High':
                            risk_factors.append("High volatility increases position risk")
                        if fundamentals.get('pe_ratio') and fundamentals['pe_ratio'] > 30:
                            risk_factors.append("High P/E ratio suggests overvaluation")
                        if tech_signals['RSI'] == 'Overbought':
                            risk_factors.append("RSI indicates overbought conditions")
                        if momentum['1_month'] < -10:
                            risk_factors.append("Strong negative momentum in past month")
                        
                        if risk_factors:
                            for risk in risk_factors:
                                st.warning(f"⚠️ {risk}")
                        else:
                            st.success("✅ No major risk factors identified")
                        
                        # Recommendation summary
                        with st.expander("📋 Quick Recommendation Summary"):
                            if signal_strength > 70:
                                st.success(f"""
                                **Strong BUY Signal** 
                                - Signal Strength: {signal_strength:.0f}%
                                - Confidence: {confidence:.0f}%
                                - Target: ₹{support_resistance['resistance_20d']:.2f}
                                - Stop Loss: ₹{support_resistance['support_20d']:.2f}
                                """)
                            elif signal_strength > 50:
                                st.info(f"""
                                **Moderate BUY Signal**
                                - Signal Strength: {signal_strength:.0f}%
                                - Confidence: {confidence:.0f}%
                                - Consider partial position
                                """)
                            elif signal_strength < 30:
                                st.error(f"""
                                **SELL/AVOID Signal**
                                - Signal Strength: {signal_strength:.0f}%
                                - Multiple bearish indicators
                                - Consider exit or avoid entry
                                """)
                            else:
                                st.warning(f"""
                                **HOLD/NEUTRAL**
                                - Signal Strength: {signal_strength:.0f}%
                                - Mixed signals, wait for clearer direction
                                """)
                else:
                    st.error("Could not fetch comprehensive analysis data.")
        
        # Educational content
        with st.expander("📚 Understanding Advanced Predictions"):
            st.markdown("""
            **Our Advanced Prediction Engine analyzes 20+ indicators:**
            
            **Technical Indicators:**
            - RSI, MACD, Stochastic, Williams %R
            - Money Flow Index (MFI), CCI, Rate of Change
            - Support/Resistance levels, Bollinger Bands
            - Volume analysis and momentum indicators
            
            **Fundamental Metrics:**
            - P/E Ratio, P/B Ratio, Debt-to-Equity
            - ROE, Profit Margins, Beta
            - Market Cap, Dividend Yield
            
            **Signal Convergence:**
            - Combines multiple timeframes
            - Weighs technical vs fundamental signals
            - Provides confidence scoring
            - Risk assessment integration
            
            **Confidence Levels:**
            - 90%+: Very High (strong convergence)
            - 80-90%: High (good agreement)
            - 70-80%: Medium (moderate signals)
            - 60-70%: Low (weak signals)
            - <60%: Very Low (conflicting signals)
            """)
    
    elif selected == "News & Insights":
        create_news_ui()


if __name__ == "__main__":
    main()
