import streamlit as st
import yfinance as yf
import pandas as pd
import os
from openai import AzureOpenAI
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# --- Configuration ---
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Model deployment name


def get_nifty50_tickers():
    """Return static list of Nifty 50 tickers (July 2025)."""
    return [
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
        "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
        "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
        "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
        "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
        "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LTIM.NS",
        "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
        "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
        "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
        "TECHM.NS", "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"
    ]


def get_nifty_next50_tickers():
    """Return static list of Nifty Next 50 tickers (July 2025)."""
    return [
        "ABB.NS", "ADANIGREEN.NS", "ADANITRANS.NS", "ALKEM.NS", "AMBUJACEM.NS",
        "AUROPHARMA.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BERGEPAINT.NS", "BIOCON.NS",
        "BOSCHLTD.NS", "CANBK.NS", "CHOLAFIN.NS", "COLPAL.NS", "DABUR.NS",
        "DIXON.NS", "GAIL.NS", "GODREJCP.NS", "HAVELLS.NS", "ICICIGI.NS",
        "ICICIPRULI.NS", "IGL.NS", "INDIGO.NS", "INDUSTOWER.NS", "IOC.NS",
        "JINDALSTEL.NS", "LTI.NS", "LUPIN.NS", "MARICO.NS", "MCDOWELL-N.NS",
        "MOTHERSON.NS", "MUTHOOTFIN.NS", "NAUKRI.NS", "PAYTM.NS", "PIDILITIND.NS",
        "PIIND.NS", "PNB.NS", "POLYCAB.NS", "RECLTD.NS", "SAIL.NS",
        "SBICARD.NS", "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "TORNTPHARM.NS",
        "TRENT.NS", "TVSMOTOR.NS", "UBL.NS", "VEDL.NS", "VOLTAS.NS", "ZOMATO.NS"
    ]


def get_nifty100_tickers():
    """Return static Nifty 100 ticker list (Nifty 50 + Nifty Next 50)."""
    return get_nifty50_tickers() + get_nifty_next50_tickers()


def get_llm_recommendation(stock, df):
    """Get entry/exit recommendation for a single stock from Azure OpenAI."""
    if not (AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT):
        return "Azure OpenAI credentials not set."
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2023-05-15"
    )
    prompt = (
        f"Analyze the following price data for {stock} and suggest entry and exit prices for short-term trading. "
        f"Be definite: Respond only with 'Buy at <price>, Exit at <price>' and a one-line reason.\n"
        f"Data (last 5 days):\n{df[['Open', 'High', 'Low', 'Close']].to_string(index=True)}"
    )
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        content = response.choices[0].message.content if response.choices and response.choices[0].message else None
        return content.strip() if content else "No response from LLM."
    except Exception as e:
        return f"Error: {e}"


def get_fundamental_data(ticker):
    """Fetch key fundamental metrics for a stock using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'P/E': info.get('trailingPE'),
            'EPS': info.get('trailingEps'),
            'Market Cap': info.get('marketCap'),
            'ROE': info.get('returnOnEquity'),
            'Debt/Equity': info.get('debtToEquity'),
            'Book Value': info.get('bookValue'),
            'Sector': info.get('sector')
        }
    except Exception:
        return {}


# --- Streamlit UI ---
st.title("LLM-Powered Nifty 100 Stock Recommendations")
st.write(
    "Get actionable buy/sell recommendations for all Nifty 100 stocks "
    "using Azure OpenAI and market data.\n"
    "The system analyzes patterns and suggests entry/exit points."
)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "Select analysis start date:",
        pd.Timestamp.today() - pd.Timedelta(days=7),
        min_value=pd.Timestamp.today() - pd.Timedelta(days=365),
        max_value=pd.Timestamp.today()
    )
with col2:
    end_date = st.date_input(
        "Select analysis end date:",
        pd.Timestamp.today(),
        min_value=start_date,
        max_value=pd.Timestamp.today() + pd.Timedelta(days=30)
    )

col3, col4 = st.columns(2)
with col3:
    profit_pct = st.number_input(
        "Target profit percentage (%)", min_value=1, max_value=100, value=10
    )
with col4:
    holding_days = st.number_input(
        "Holding period (days)", min_value=1, max_value=90, value=30
    )

with st.spinner("Fetching Nifty 100 stock data..."):
    tickers = get_nifty100_tickers()
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date + pd.Timedelta(days=1),
        group_by='ticker',
        progress=False
    )
    if data is not None and not data.empty:
        available = [
            t for t in data.columns.get_level_values(0).unique()
            if not data[t].dropna().empty
        ]
        st.info(
            f"✅ Data fetched: {len(available)}/100 Nifty stocks analyzed"
        )
        if len(available) < 100:
            missing = set(tickers) - set(available)
            st.warning(
                f"No data for: {', '.join(sorted(missing))}"
            )
    else:
        st.warning(
            "⚠️ Check if selected date range includes trading days."
        )


def get_llm_top_picks(data, start_date, end_date, profit_pct, holding_days):
    """
    Get buy recommendations for all Nifty 100 stocks with technical and fundamental analysis.
    """
    if not (
        AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT
    ):
        return "Azure OpenAI credentials not set."
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2023-05-15"
    )
    summary = ""
    tickers = (
        data.columns.get_level_values(0).unique()
        if hasattr(data.columns, 'get_level_values')
        else data.columns.unique()
    )
    for ticker in tickers:
        df = data[ticker].dropna()
        if df.empty or len(df) < 5:
            summary += (
                f"\nTicker: {ticker}\nNo data available for selected range.\n"
            )
            continue
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        volume_ma = None
        if 'Volume' in df:
            df['Volume_MA'] = df['Volume'].rolling(window=5).mean()
            volume_ma = (
                df['Volume_MA'].iloc[-1]
                if not df['Volume_MA'].isna().all()
                else None
            )
        ohlc_data = (
            df[['Open', 'High', 'Low', 'Close']]
            .tail(5)
            .to_string(index=True)
        )
        sma_val = (
            df['SMA_5'].iloc[-1]
            if not df['SMA_5'].isna().all()
            else float('nan')
        )
        # Fetch fundamental data
        fundamentals = get_fundamental_data(ticker)
        fundamentals_str = ', '.join(
            f"{k}: {v}" for k, v in fundamentals.items() if v is not None
        )
        summary += (
            f"\nTicker: {ticker}\n"
            + "Recent price action:\n"
            + ohlc_data
            + "\nTechnicals:\n"
            + f"5-day SMA: {sma_val:.2f}\n"
            + (f"5-day Volume MA: {volume_ma:.0f}\n" if volume_ma else "")
            + (
                f"Fundamentals: {fundamentals_str}\n"
                if fundamentals_str else "Fundamentals: Not available\n"
            )
            + "\n"
        )
    prompt = (
        f"You are a stock market analyst.\n"
        f"Analyze these Nifty 100 stocks and their recent price, technical, "
        f"and fundamental data.\n\n"
        f"Task: Recommend stocks likely to give at least {profit_pct}% profit "
        f"in {holding_days} days.\n\n"
        "Response format for each stock (if no recommendation, say "
        "'No recommendation'):\n"
        "'Buy at <price> on <entry date>, Exit at <price> on <exit date>' "
        "followed by one-line technical and/or fundamental reason.\n\n"
        f"Analysis period: {start_date} to {end_date}\n\n"
        "Data:\n"
        f"{summary}\n\n"
    )
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        content = (
            response.choices[0].message.content
            if response.choices and response.choices[0].message
            else None
        )
        return content.strip() if content else "No response from LLM."
    except Exception as e:
        return f"Error: {e}"


def get_llm_top_3_picks(data, start_date, end_date, profit_pct, holding_days):
    """
    Get top 3 most probable buy recommendations for Nifty 100 stocks
    using technical and fundamental analysis.
    """
    if not (
        AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT
    ):
        return "Azure OpenAI credentials not set."
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2023-05-15"
    )
    summary = ""
    tickers = (
        data.columns.get_level_values(0).unique()
        if hasattr(data.columns, 'get_level_values')
        else data.columns.unique()
    )
    for ticker in tickers:
        df = data[ticker].dropna()
        if df.empty or len(df) < 5:
            summary += (
                f"\nTicker: {ticker}\nNo data available for selected range.\n"
            )
            continue
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        volume_ma = None
        if 'Volume' in df:
            df['Volume_MA'] = df['Volume'].rolling(window=5).mean()
            volume_ma = (
                df['Volume_MA'].iloc[-1]
                if not df['Volume_MA'].isna().all()
                else None
            )
        ohlc_data = (
            df[['Open', 'High', 'Low', 'Close']]
            .tail(5)
            .to_string(index=True)
        )
        sma_val = (
            df['SMA_5'].iloc[-1]
            if not df['SMA_5'].isna().all()
            else float('nan')
        )
        # Fetch fundamental data
        fundamentals = get_fundamental_data(ticker)
        fundamentals_str = ', '.join(
            f"{k}: {v}" for k, v in fundamentals.items() if v is not None
        )
        summary += (
            f"\nTicker: {ticker}\n"
            + "Recent price action:\n"
            + ohlc_data
            + "\nTechnicals:\n"
            + f"5-day SMA: {sma_val:.2f}\n"
            + (f"5-day Volume MA: {volume_ma:.0f}\n" if volume_ma else "")
            + (
                f"Fundamentals: {fundamentals_str}\n"
                if fundamentals_str else "Fundamentals: Not available\n"
            )
            + "\n"
        )
    prompt = (
        f"You are a stock market analyst.\n"
        f"Analyze these Nifty 100 stocks and their recent price, technical, "
        f"and fundamental data.\n\n"
        f"Task: Recommend the top 3 stocks most likely to achieve at least "
        f"{profit_pct}% profit in {holding_days} days.\n\n"
        "For each, provide: 'Buy at <price> on <entry date>, Exit at <price> "
        "on <exit date>' and a one-line technical and/or fundamental "
        "reason.\n\n"
        f"Analysis period: {start_date} to {end_date}\n\n"
        "Data:\n"
        f"{summary}\n\n"
        "Format your response as:\n"
        "1. <TICKER> - Buy at <price> on <date>, Exit at <price> on <date>. "
        "<reason>\n"
        "2. <TICKER> - Buy at <price> on <date>, Exit at <price> on <date>. "
        "<reason>\n"
        "3. <TICKER> - Buy at <price> on <date>, Exit at <price> on <date>. "
        "<reason>\n"
    )
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        content = (
            response.choices[0].message.content
            if response.choices and response.choices[0].message
            else None
        )
        return content.strip() if content else "No response from LLM."
    except Exception as e:
        return f"Error: {e}"


if data is not None and not data.empty:
    if st.button("Get Recommendations for All 100 Stocks"):
        with st.spinner("Analyzing stocks using Azure OpenAI..."):
            recommendations = get_llm_top_picks(
                data, start_date, end_date, profit_pct, holding_days
            )
            st.success("📈 Recommendations:")
            st.write(recommendations)
            st.info(
                "Note: These are AI-generated recommendations. "
                "Please conduct your own research."
            )
    if st.button("Get Top 3 Most Probable Recommendations"):
        with st.spinner("Analyzing stocks using Azure OpenAI..."):
            top_3_recommendations = get_llm_top_3_picks(
                data, start_date, end_date, profit_pct, holding_days
            )
            st.success("📈 Top 3 Most Probable Recommendations:")
            st.write(top_3_recommendations)
            st.info(
                "Note: These are AI-generated recommendations. "
                "Please conduct your own research."
            )
else:
    st.error(
        "Failed to fetch stock data. Please try a different date range "
        "or check your internet connection."
    )
