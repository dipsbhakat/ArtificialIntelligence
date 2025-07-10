# LLM-Powered Nifty Top Stocks Dashboard

This dashboard fetches Nifty top stocks, analyzes them using Azure OpenAI, and provides entry/exit price suggestions.

## How to Run

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set your Azure OpenAI credentials as environment variables.
3. Run the dashboard:
   ```sh
   streamlit run dashboard.py
   ```

## Configuration
- Requires Azure OpenAI API key and endpoint.
- Fetches Nifty top stocks using yfinance.
