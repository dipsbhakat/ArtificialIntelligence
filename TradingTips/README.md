# 🚀 Advanced Trading Dashboard

A comprehensive Python Streamlit trading application powered by Azure OpenAI for intelligent stock analysis, portfolio management, and trading insights.

## 🌟 Features

### 📊 Market Analysis
- **Real-time Stock Data**: Fetch live stock prices and historical data using Yahoo Finance
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Volume Analysis
- **Interactive Charts**: Candlestick charts with technical overlays using Plotly
- **AI-Powered Analysis**: Get intelligent buy/sell recommendations from Azure OpenAI

### 💼 Portfolio Management
- **Position Tracking**: Monitor your stock holdings with real-time P&L
- **Performance Metrics**: Track returns, win rates, and portfolio allocation
- **Sector Analysis**: Visualize portfolio diversification across sectors
- **Add/Remove Positions**: Easily manage your portfolio holdings

### 👁️ Watchlist Management
- **Stock Watchlist**: Track stocks you're interested in
- **Price Alerts**: Set price targets and stop-loss alerts
- **Top Movers**: View best and worst performers from your watchlist
- **Target Distance**: Monitor how close stocks are to your targets

### 🤖 AI Recommendations
- **Nifty 50/100 Analysis**: Get AI recommendations for top Indian stocks
- **Technical + Fundamental**: Combined analysis using multiple data points
- **Entry/Exit Prices**: Specific price recommendations with reasoning
- **Risk Assessment**: AI-powered risk evaluation for each recommendation

### 📰 News & Market Insights
- **Market Sentiment**: Real-time market sentiment analysis
- **Sector Performance**: Track sector-wise market movements
- **Economic Calendar**: Upcoming events that may impact markets
- **Stock-Specific News**: Get news related to specific stocks

### 📈 Backtesting Engine
- **Strategy Testing**: Test multiple trading strategies on historical data
- **Performance Metrics**: Sharpe ratio, max drawdown, win rate analysis
- **Strategy Comparison**: Compare different strategies side-by-side
- **Visual Results**: Interactive charts showing strategy performance

### 💱 Trade Execution (Simulated)
- **Order Management**: Place market, limit, stop-loss orders
- **Position Tracking**: Monitor current positions and P&L
- **Account Management**: Track cash balance and buying power
- **Order History**: View all past and pending orders

### 🛡️ Risk Management
- **Portfolio Risk Metrics**: Concentration risk, sector allocation
- **Position Sizing**: Calculate optimal position sizes based on risk
- **Risk Recommendations**: Get personalized risk management advice
- **Performance Analysis**: Track portfolio performance over time

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
   AZURE_OPENAI_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name_here
   ```

4. **Run the application**
   ```bash
   streamlit run enhanced_trading_app.py
   ```

5. **Access the dashboard**
   Open your browser and go to `http://localhost:8501`

## 🐳 Docker Deployment

### Build and Run Locally
```bash
docker build -t trading-app .
docker run -p 8501:8501 trading-app
```

### Deploy to Azure Container Registry
```bash
# Login to Azure
az login

# Create resource group
az group create --name tradingtips-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group tradingtips-rg --name tradingacr --sku Basic

# Login to ACR
az acr login --name tradingacr

# Build and push image
docker build -t tradingacr.azurecr.io/trading-app:latest .
docker push tradingacr.azurecr.io/trading-app:latest

# Create App Service Plan
az appservice plan create --name tradingtips-plan --resource-group tradingtips-rg --is-linux

# Create Web App
az webapp create --resource-group tradingtips-rg --plan tradingtips-plan --name tradingtips-app --deployment-container-image-name tradingacr.azurecr.io/trading-app:latest

# Configure environment variables
az webapp config appsettings set --resource-group tradingtips-rg --name tradingtips-app --settings AZURE_OPENAI_KEY="your_key" AZURE_OPENAI_ENDPOINT="your_endpoint" AZURE_OPENAI_DEPLOYMENT="your_deployment"
```

## 📁 Project Structure

```
TradingTips/
├── enhanced_trading_app.py      # Main Streamlit application
├── dashboard.py                 # Original simple dashboard
├── watchlist_manager.py         # Watchlist and alerts functionality
├── news_manager.py             # News and market insights
├── backtesting.py              # Strategy backtesting engine
├── trade_executor.py           # Trade execution and order management
├── risk_management.py          # Risk analysis and management
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🔧 Configuration

### Azure OpenAI Setup
1. Create an Azure OpenAI resource in Azure Portal
2. Deploy a GPT-4 or GPT-3.5-turbo model
3. Get your API key, endpoint, and deployment name
4. Add to `.env` file

### Stock Data
- Uses Yahoo Finance API (free)
- Supports Indian stocks (add .NS suffix, e.g., RELIANCE.NS)
- Real-time data with 15-minute delay

### Database
- Uses SQLite for local data storage
- Stores portfolio, watchlist, orders, and trading history
- Automatically created on first run

## 🔌 API Integrations

- **Yahoo Finance**: Stock data and financial information
- **Azure OpenAI**: AI-powered analysis and recommendations
- **Beautiful Soup**: Web scraping for news (when available)

## 📊 Trading Strategies (Backtesting)

1. **Simple Moving Average (SMA)**: Crossover strategy using 20/50 day SMAs
2. **RSI Strategy**: Oversold/overbought levels (30/70)
3. **MACD Strategy**: MACD line crossing signal line
4. **Bollinger Bands**: Mean reversion strategy
5. **Combined Strategy**: Multiple indicators for stronger signals

## ⚠️ Disclaimer

This application is for educational and research purposes only. It provides simulated trading functionality and should not be used for actual trading without proper testing and risk management. Always:

- Do your own research before making investment decisions
- Consider your risk tolerance and investment objectives
- Consult with financial advisors for professional advice
- Never invest more than you can afford to lose

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the existing GitHub issues
2. Create a new issue with detailed description
3. Provide error logs and steps to reproduce

## 🔮 Future Enhancements

- [ ] Real broker API integration (Zerodha, IIFL, etc.)
- [ ] Advanced charting with TradingView integration
- [ ] Machine learning-based price prediction
- [ ] Options trading analysis
- [ ] Social trading features
- [ ] Mobile app version
- [ ] Real-time WebSocket data feeds
- [ ] Advanced risk models (VaR, CVaR)

## 📈 Performance Notes

- Optimized for Indian stock markets (NSE/BSE)
- Handles 100+ stocks efficiently
- Real-time updates with caching
- Responsive web interface
- Mobile-friendly design

---

**Happy Trading! 📈🚀**
