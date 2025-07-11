# 🚀 Advanced Trading Dashboard

A streamlined AI-powered stock analysis and market insights dashboard built with Streamlit and Azure OpenAI.

## ✨ Features

### 📊 Market Analysis
- **Real-time Stock Data**: Live stock prices and historical data using Yahoo Finance
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Interactive Charts**: Candlestick charts with technical overlays using Plotly
- **Comprehensive Stock Info**: P/E ratio, market cap, sector, financial metrics
- **AI-Powered Analysis**: Get intelligent buy/sell recommendations from Azure OpenAI

### 🤖 AI Recommendations  
- **Nifty 50 Analysis**: AI-powered stock recommendations for top Indian stocks
- **Target Prices**: Specific entry/exit price recommendations
- **Risk Assessment**: AI evaluation of investment risk levels
- **Investment Rationale**: Detailed reasoning for each recommendation
- **Market Sentiment**: Current market conditions and outlook

### 📰 News & Insights
- **Latest Market News**: Real-time market news and analysis
- **Stock-Specific News**: Get news related to specific stocks
- **Market Sentiment**: Sentiment analysis from news sources
- **Economic Calendar**: Upcoming events that may impact markets

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Azure OpenAI account with API credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TradingTips.git
   cd TradingTips
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_KEY=your_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4o
   ```

4. **Run the application**
   ```bash
   streamlit run enhanced_trading_app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 🖼️ Screenshots

The dashboard includes three main sections:

1. **Market Analysis** - Technical charts and AI analysis for any stock
2. **AI Recommendations** - Get top stock picks with targets and rationale  
3. **News & Insights** - Latest market news and sentiment analysis

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data**: Yahoo Finance API (yfinance)
- **AI**: Azure OpenAI GPT-4
- **Visualization**: Plotly
- **Database**: SQLite (for minimal data storage)

## 📈 Usage Examples

### Market Analysis
1. Enter a stock symbol (e.g., "RELIANCE.NS")
2. Select time period and analysis type
3. View interactive charts with technical indicators
4. Get AI-powered analysis and recommendations

### AI Recommendations
1. Click "Get Top AI Picks" 
2. View AI-recommended stocks with targets
3. Review risk assessment and rationale
4. Check market sentiment overview

### News & Insights
1. Browse latest market news
2. Search for stock-specific news
3. Monitor market sentiment indicators

## 🔧 Configuration

### Environment Variables
- `AZURE_OPENAI_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint
- `AZURE_OPENAI_DEPLOYMENT`: Your deployment name (e.g., "gpt-4o")

### Stock Symbols
Use Yahoo Finance format for Indian stocks:
- `RELIANCE.NS` for Reliance Industries
- `TCS.NS` for Tata Consultancy Services
- `HDFCBANK.NS` for HDFC Bank
- `^NSEI` for Nifty 50 Index

## 🚨 Disclaimer

This application is for educational and research purposes only. The AI recommendations and analysis provided should not be considered as financial advice. Always do your own research and consider consulting with a qualified financial advisor before making investment decisions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please create an issue in the GitHub repository.

---

**Happy Trading! 📈**
