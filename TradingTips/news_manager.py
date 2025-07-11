"""
News and Market Insights Module for Trading App
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import List, Dict
import yfinance as yf
import re


class NewsManager:
    """Fetch and manage financial news and market insights."""
    
    def __init__(self):
        self.news_sources = {
            'economic_times': 'https://economictimes.indiatimes.com/markets',
            'business_standard': 'https://www.business-standard.com/markets',
            'moneycontrol': 'https://www.moneycontrol.com/news/business/markets/'
        }
    
    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """Fetch latest market news from various sources."""
        news_items = []
        
        try:
            # Try to fetch from Economic Times (simplified approach)
            url = "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse RSS feed or HTML content
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')[:limit]
                
                for item in items:
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    description = item.find('description')
                    
                    if title and link:
                        news_items.append({
                            'title': title.text.strip(),
                            'link': link.text.strip(),
                            'source': 'Economic Times',
                            'published': pub_date.text.strip() if pub_date else 'N/A',
                            'description': description.text.strip() if description else 'N/A'
                        })
            
        except Exception as e:
            st.warning(f"Could not fetch news from Economic Times: {e}")
        
        # If we couldn't get news, provide sample news
        if not news_items:
            news_items = self.get_sample_news()
        
        return news_items[:limit]
    
    def get_sample_news(self) -> List[Dict]:
        """Provide sample news when live feeds are not available."""
        return [
            {
                'title': 'Nifty 50 hits new high as banking stocks rally',
                'source': 'Market Update',
                'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'description': 'Banking sector leads the charge with HDFC Bank and ICICI Bank gaining over 3%',
                'link': '#'
            },
            {
                'title': 'IT stocks under pressure on global slowdown fears',
                'source': 'Sector News',
                'published': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
                'description': 'TCS, Infosys, and Wipro decline as clients reduce IT spending',
                'link': '#'
            },
            {
                'title': 'RBI policy decision awaited by markets',
                'source': 'Economic News',
                'published': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
                'description': 'Markets expecting status quo on interest rates in upcoming policy meet',
                'link': '#'
            },
            {
                'title': 'Foreign investors turn buyers in Indian equities',
                'source': 'Investment Flow',
                'published': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M'),
                'description': 'FIIs invest ₹2,500 crores in the last week amid global uncertainty',
                'link': '#'
            },
            {
                'title': 'Crude oil prices impact energy stocks',
                'source': 'Commodity News',
                'published': (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
                'description': 'ONGC and Reliance respond to volatile crude oil movements',
                'link': '#'
            }
        ]
    
    def get_sector_performance(self) -> Dict:
        """Get sector-wise performance data."""
        sectors = {
            'Banking': ['^NSEBANK', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS'],
            'IT': ['^NIFTIT', 'TCS.NS', 'INFY.NS', 'WIPRO.NS'],
            'Auto': ['^CNXAUTO', 'MARUTI.NS', 'M&M.NS', 'TATAMOTORS.NS'],
            'Pharma': ['^CNXPHARMA', 'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS'],
            'Energy': ['^CNXENERGY', 'RELIANCE.NS', 'ONGC.NS', 'BPCL.NS']
        }
        
        sector_data = {}
        
        for sector, symbols in sectors.items():
            try:
                # Get sector index (first symbol)
                index_symbol = symbols[0]
                stock = yf.Ticker(index_symbol)
                hist = stock.history(period='5d')
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[0]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    sector_data[sector] = {
                        'index': index_symbol,
                        'current_price': current_price,
                        'change_pct': change_pct,
                        'trend': 'Bullish' if change_pct > 1 else 'Bearish' if change_pct < -1 else 'Neutral'
                    }
                else:
                    sector_data[sector] = {
                        'index': index_symbol,
                        'current_price': 0,
                        'change_pct': 0,
                        'trend': 'No Data'
                    }
            
            except Exception as e:
                sector_data[sector] = {
                    'index': index_symbol,
                    'current_price': 0,
                    'change_pct': 0,
                    'trend': 'Error'
                }
        
        return sector_data
    
    def get_market_sentiment(self) -> Dict:
        """Analyze market sentiment based on various indicators."""
        try:
            # Get Nifty 50 data
            nifty = yf.Ticker('^NSEI')
            nifty_hist = nifty.history(period='30d')
            
            if nifty_hist.empty:
                return {'sentiment': 'Unknown', 'confidence': 0}
            
            # Calculate various sentiment indicators
            current_price = nifty_hist['Close'].iloc[-1]
            sma_20 = nifty_hist['Close'].rolling(20).mean().iloc[-1]
            sma_50 = nifty_hist['Close'].rolling(50).mean().iloc[-1] if len(nifty_hist) >= 50 else sma_20
            
            # RSI calculation
            delta = nifty_hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Volume trend
            avg_volume = nifty_hist['Volume'].rolling(20).mean().iloc[-1]
            current_volume = nifty_hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            # Sentiment calculation
            sentiment_score = 0
            
            # Price vs Moving Averages
            if current_price > sma_20:
                sentiment_score += 1
            if current_price > sma_50:
                sentiment_score += 1
            if sma_20 > sma_50:
                sentiment_score += 1
            
            # RSI
            if 30 < current_rsi < 70:
                sentiment_score += 1
            elif current_rsi < 30:
                sentiment_score -= 1  # Oversold (potentially bullish)
            elif current_rsi > 70:
                sentiment_score -= 1  # Overbought (potentially bearish)
            
            # Volume
            if volume_ratio > 1.2:
                sentiment_score += 1
            
            # Determine sentiment
            if sentiment_score >= 3:
                sentiment = 'Bullish'
                confidence = min(sentiment_score * 20, 100)
            elif sentiment_score <= 1:
                sentiment = 'Bearish'
                confidence = min(abs(sentiment_score - 5) * 20, 100)
            else:
                sentiment = 'Neutral'
                confidence = 60
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'rsi': current_rsi,
                'price_vs_sma20': 'Above' if current_price > sma_20 else 'Below',
                'volume_trend': 'High' if volume_ratio > 1.2 else 'Normal'
            }
        
        except Exception as e:
            return {'sentiment': 'Unknown', 'confidence': 0, 'error': str(e)}
    
    def get_stock_news(self, symbol: str) -> List[Dict]:
        """Get news specific to a stock symbol."""
        # This is a simplified implementation
        # In production, you'd use news APIs like Alpha Vantage, NewsAPI, etc.
        
        company_name = self.get_company_name(symbol)
        
        # Sample stock-specific news
        sample_news = [
            {
                'title': f'{company_name} reports strong quarterly results',
                'source': 'Company News',
                'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'description': f'Revenue and profit margins show improvement for {company_name}',
                'relevance': 'High'
            },
            {
                'title': f'Analysts upgrade {company_name} target price',
                'source': 'Analyst Report',
                'published': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M'),
                'description': f'Major brokerages revise upward targets for {symbol}',
                'relevance': 'Medium'
            }
        ]
        
        return sample_news
    
    def get_company_name(self, symbol: str) -> str:
        """Get company name from stock symbol."""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info.get('longName', symbol)
        except:
            return symbol
    
    def get_economic_calendar(self) -> List[Dict]:
        """Get upcoming economic events."""
        # Sample economic calendar events
        today = datetime.now()
        
        events = [
            {
                'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'event': 'RBI Monetary Policy Decision',
                'importance': 'High',
                'expected': 'No change in repo rate',
                'previous': '6.50%'
            },
            {
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'event': 'CPI Inflation Data',
                'importance': 'High',
                'expected': '5.2%',
                'previous': '5.1%'
            },
            {
                'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                'event': 'Industrial Production',
                'importance': 'Medium',
                'expected': '3.1%',
                'previous': '2.8%'
            },
            {
                'date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
                'event': 'FII/DII Investment Data',
                'importance': 'Medium',
                'expected': 'Positive inflows',
                'previous': '₹1,200 Cr inflow'
            }
        ]
        
        return events


def create_news_ui():
    """Create Streamlit UI for news and insights."""
    st.header("📰 Market News & Insights")
    
    news_manager = NewsManager()
    
    # Market sentiment overview
    sentiment_data = news_manager.get_market_sentiment()
    
    st.subheader("📊 Market Sentiment Analysis")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sentiment_color = {
            'Bullish': 'green',
            'Bearish': 'red',
            'Neutral': 'orange',
            'Unknown': 'gray'
        }
        st.markdown(
            f"**Sentiment:** <span style='color: {sentiment_color.get(sentiment_data['sentiment'], 'gray')}'>"
            f"{sentiment_data['sentiment']}</span>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.metric("Confidence", f"{sentiment_data.get('confidence', 0):.0f}%")
    
    with col3:
        if 'rsi' in sentiment_data:
            st.metric("RSI", f"{sentiment_data['rsi']:.1f}")
    
    with col4:
        if 'volume_trend' in sentiment_data:
            st.metric("Volume", sentiment_data['volume_trend'])
    
    # Latest News
    st.subheader("📰 Latest Market News")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        news_count = st.selectbox("Number of articles", [5, 10, 15, 20], index=1)
    
    if st.button("Refresh News"):
        st.session_state["force_news_refresh"] = True

    # Only fetch news if not cached or refresh requested
    if "news_cache" not in st.session_state or st.session_state.get("force_news_refresh", False):
        st.session_state["news_cache"] = news_manager.get_market_news(news_count)
        st.session_state["force_news_refresh"] = False
    news_items = st.session_state["news_cache"]

    for i, news in enumerate(news_items):
        with st.expander(f"📄 {news['title']}", expanded=(i == 0)):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Source:** {news['source']}")
                st.write(f"**Published:** {news['published']}")
                if news['description'] != 'N/A':
                    st.write(f"**Summary:** {news['description']}")
            with col2:
                if news['link'] != '#':
                    st.markdown(f"[Read Full Article]({news['link']})")
    
    # Sector Performance
    st.subheader("📈 Sector Performance")
    
    sector_data = news_manager.get_sector_performance()
    
    if sector_data:
        sector_df = pd.DataFrame(sector_data).T
        sector_df.reset_index(inplace=True)
        sector_df.columns = ['Sector', 'Index', 'Price', 'Change %', 'Trend']
        
        # Color code the trend
        def color_trend(val):
            if val == 'Bullish':
                return 'color: green'
            elif val == 'Bearish':
                return 'color: red'
            else:
                return 'color: orange'
        
        def color_change(val):
            try:
                if float(val) > 0:
                    return 'color: green'
                elif float(val) < 0:
                    return 'color: red'
                return 'color: black'
            except:
                return 'color: black'
        
        styled_sector_df = sector_df.style.applymap(
            color_trend, subset=['Trend']
        ).applymap(
            color_change, subset=['Change %']
        )
        
        st.dataframe(styled_sector_df, use_container_width=True)
    
    # Economic Calendar
    st.subheader("📅 Economic Calendar")
    
    calendar_events = news_manager.get_economic_calendar()
    
    for event in calendar_events:
        importance_color = {
            'High': 'red',
            'Medium': 'orange',
            'Low': 'green'
        }
        
        with st.expander(
            f"📅 {event['event']} - {event['date']} "
            f"({event['importance']} Importance)"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Expected:** {event['expected']}")
                st.write(f"**Previous:** {event['previous']}")
            with col2:
                st.markdown(
                    f"**Importance:** <span style='color: {importance_color[event['importance']]}'>"
                    f"{event['importance']}</span>",
                    unsafe_allow_html=True
                )
    
    # Stock-specific news search
    st.subheader("🔍 Stock-Specific News")
    
    symbol_input = st.text_input("Enter stock symbol for specific news", placeholder="e.g., RELIANCE.NS")
    
    if symbol_input:
        stock_news = news_manager.get_stock_news(symbol_input)
        
        if stock_news:
            for news in stock_news:
                with st.expander(f"📰 {news['title']}"):
                    st.write(f"**Source:** {news['source']}")
                    st.write(f"**Published:** {news['published']}")
                    st.write(f"**Description:** {news['description']}")
                    st.write(f"**Relevance:** {news['relevance']}")
        else:
            st.info(f"No specific news found for {symbol_input}")
