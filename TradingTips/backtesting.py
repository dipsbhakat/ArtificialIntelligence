"""
Backtesting Module for Trading Strategies
"""

import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sqlite3


class BacktestEngine:
    """Backtesting engine for trading strategies."""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.results = {}
    
    def load_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Load historical data for backtesting."""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                return None
            
            # Calculate technical indicators
            df = self.calculate_indicators(df)
            return df
        
        except Exception as e:
            st.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for strategy."""
        # Moving averages
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
    
    def simple_moving_average_strategy(self, df: pd.DataFrame, 
                                     short_window: int = 20, 
                                     long_window: int = 50) -> pd.DataFrame:
        """Simple Moving Average Crossover Strategy."""
        df = df.copy()
        
        # Calculate signals
        df['Signal'] = 0
        df['Position'] = 0
        
        # Generate signals
        df.loc[df[f'SMA_{short_window}'] > df[f'SMA_{long_window}'], 'Signal'] = 1
        df.loc[df[f'SMA_{short_window}'] < df[f'SMA_{long_window}'], 'Signal'] = -1
        
        # Calculate positions
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def rsi_strategy(self, df: pd.DataFrame, 
                    oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
        """RSI-based trading strategy."""
        df = df.copy()
        
        df['Signal'] = 0
        df['Position'] = 0
        
        # Buy when RSI < oversold, sell when RSI > overbought
        df.loc[df['RSI'] < oversold, 'Signal'] = 1
        df.loc[df['RSI'] > overbought, 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def macd_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD-based trading strategy."""
        df = df.copy()
        
        df['Signal'] = 0
        df['Position'] = 0
        
        # Buy when MACD crosses above signal line
        df.loc[df['MACD'] > df['MACD_Signal'], 'Signal'] = 1
        df.loc[df['MACD'] < df['MACD_Signal'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def bollinger_bands_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bollinger Bands mean reversion strategy."""
        df = df.copy()
        
        df['Signal'] = 0
        df['Position'] = 0
        
        # Buy when price touches lower band, sell when touches upper band
        df.loc[df['Close'] <= df['BB_Lower'], 'Signal'] = 1
        df.loc[df['Close'] >= df['BB_Upper'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def combined_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combined strategy using multiple indicators."""
        df = df.copy()
        
        df['Signal'] = 0
        df['Position'] = 0
        
        # Multiple conditions for stronger signals
        buy_conditions = (
            (df['SMA_20'] > df['SMA_50']) &
            (df['RSI'] < 70) &
            (df['MACD'] > df['MACD_Signal']) &
            (df['Close'] > df['BB_Lower'])
        )
        
        sell_conditions = (
            (df['SMA_20'] < df['SMA_50']) |
            (df['RSI'] > 80) |
            (df['MACD'] < df['MACD_Signal']) |
            (df['Close'] < df['BB_Lower'])
        )
        
        df.loc[buy_conditions, 'Signal'] = 1
        df.loc[sell_conditions, 'Signal'] = -1
        
        df['Position'] = df['Signal'].diff()
        
        return df
    
    def calculate_returns(self, df: pd.DataFrame, 
                         commission: float = 0.001) -> Dict:
        """Calculate strategy returns and performance metrics."""
        df = df.copy()
        
        # Initialize portfolio
        df['Holdings'] = 0
        df['Cash'] = self.initial_capital
        df['Total_Value'] = self.initial_capital
        df['Returns'] = 0
        
        cash = self.initial_capital
        holdings = 0
        
        # Process each trading signal
        for i in range(1, len(df)):
            if df['Position'].iloc[i] == 2:  # Buy signal
                if cash > 0:
                    shares_to_buy = int(cash / df['Close'].iloc[i])
                    cost = shares_to_buy * df['Close'].iloc[i]
                    commission_cost = cost * commission
                    
                    if cash >= cost + commission_cost:
                        holdings += shares_to_buy
                        cash -= (cost + commission_cost)
            
            elif df['Position'].iloc[i] == -2:  # Sell signal
                if holdings > 0:
                    proceeds = holdings * df['Close'].iloc[i]
                    commission_cost = proceeds * commission
                    
                    cash += (proceeds - commission_cost)
                    holdings = 0
            
            df.loc[df.index[i], 'Holdings'] = holdings
            df.loc[df.index[i], 'Cash'] = cash
            df.loc[df.index[i], 'Total_Value'] = cash + (holdings * df['Close'].iloc[i])
        
        # Calculate returns
        df['Returns'] = df['Total_Value'].pct_change()
        
        # Performance metrics
        total_return = (df['Total_Value'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # Buy and hold comparison
        buy_hold_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]
        
        # Sharpe ratio
        sharpe_ratio = self.calculate_sharpe_ratio(df['Returns'])
        
        # Maximum drawdown
        max_drawdown = self.calculate_max_drawdown(df['Total_Value'])
        
        # Win rate
        trades = self.extract_trades(df)
        win_rate = self.calculate_win_rate(trades)
        
        return {
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'excess_return': total_return - buy_hold_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'final_value': df['Total_Value'].iloc[-1],
            'data': df
        }
    
    def calculate_sharpe_ratio(self, returns: pd.Series, 
                              risk_free_rate: float = 0.05) -> float:
        """Calculate Sharpe ratio."""
        if returns.std() == 0:
            return 0
        
        excess_returns = returns.mean() - (risk_free_rate / 252)
        return excess_returns / returns.std() * np.sqrt(252)
    
    def calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """Calculate maximum drawdown."""
        peak = portfolio_values.expanding(min_periods=1).max()
        drawdown = (portfolio_values - peak) / peak
        return drawdown.min()
    
    def extract_trades(self, df: pd.DataFrame) -> List[Dict]:
        """Extract individual trades from backtest results."""
        trades = []
        position = 0
        entry_price = 0
        entry_date = None
        
        for i, row in df.iterrows():
            if row['Position'] == 2 and position == 0:  # Buy
                position = 1
                entry_price = row['Close']
                entry_date = i
            elif row['Position'] == -2 and position == 1:  # Sell
                exit_price = row['Close']
                exit_date = i
                profit_loss = exit_price - entry_price
                profit_loss_pct = (profit_loss / entry_price) * 100
                
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'profit_loss': profit_loss,
                    'profit_loss_pct': profit_loss_pct,
                    'duration': (exit_date - entry_date).days
                })
                
                position = 0
        
        return trades
    
    def calculate_win_rate(self, trades: List[Dict]) -> Dict:
        """Calculate win rate statistics."""
        if not trades:
            return {'win_rate': 0, 'avg_win': 0, 'avg_loss': 0, 'profit_factor': 0}
        
        winning_trades = [t for t in trades if t['profit_loss'] > 0]
        losing_trades = [t for t in trades if t['profit_loss'] < 0]
        
        win_rate = len(winning_trades) / len(trades)
        avg_win = np.mean([t['profit_loss'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t['profit_loss']) for t in losing_trades]) if losing_trades else 0
        
        total_wins = sum([t['profit_loss'] for t in winning_trades])
        total_losses = sum([abs(t['profit_loss']) for t in losing_trades])
        
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return {
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    def run_backtest(self, symbol: str, strategy_name: str, 
                    start_date: str, end_date: str, **kwargs) -> Dict:
        """Run a complete backtest for a given strategy."""
        # Load data
        df = self.load_data(symbol, start_date, end_date)
        
        if df is None:
            return None
        
        # Extract commission for portfolio calculation
        commission = kwargs.pop('commission', 0.001)
        
        # Apply strategy (pass remaining kwargs)
        if strategy_name == 'SMA':
            df = self.simple_moving_average_strategy(df, **kwargs)
        elif strategy_name == 'RSI':
            df = self.rsi_strategy(df, **kwargs)
        elif strategy_name == 'MACD':
            df = self.macd_strategy(df)
        elif strategy_name == 'Bollinger':
            df = self.bollinger_bands_strategy(df)
        elif strategy_name == 'Combined':
            df = self.combined_strategy(df)
        else:
            st.error(f"Unknown strategy: {strategy_name}")
            return None
        
        # Calculate returns (include commission back in kwargs)
        results = self.calculate_returns(df, commission=commission, **kwargs)
        results['strategy'] = strategy_name
        results['symbol'] = symbol
        
        return results
    
    def create_backtest_chart(self, results: Dict) -> go.Figure:
        """Create visualization for backtest results."""
        df = results['data']
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                f"{results['symbol']} - {results['strategy']} Strategy",
                'Portfolio Value vs Buy & Hold',
                'Trading Signals'
            ),
            vertical_spacing=0.1,
            row_heights=[0.5, 0.3, 0.2]
        )
        
        # Price chart with signals
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Close'],
                name='Price', line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # Buy signals
        buy_signals = df[df['Position'] == 2]
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index, y=buy_signals['Close'],
                    mode='markers', name='Buy', 
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        # Sell signals
        sell_signals = df[df['Position'] == -2]
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index, y=sell_signals['Close'],
                    mode='markers', name='Sell',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ),
                row=1, col=1
            )
        
        # Portfolio value vs buy and hold
        buy_hold_value = self.initial_capital * (df['Close'] / df['Close'].iloc[0])
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Total_Value'],
                name='Strategy Portfolio', line=dict(color='green')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=buy_hold_value,
                name='Buy & Hold', line=dict(color='orange', dash='dash')
            ),
            row=2, col=1
        )
        
        # Signal indicator
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['Signal'],
                name='Signal', line=dict(color='purple')
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            title=f"Backtest Results: {results['strategy']} Strategy",
            height=800,
            showlegend=True
        )
        
        return fig


def create_backtesting_ui():
    """Create Streamlit UI for backtesting."""
    st.header("📊 Strategy Backtesting")
    
    # Backtesting parameters
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("Stock Symbol", value="RELIANCE.NS")
        start_date = st.date_input(
            "Start Date", 
            value=datetime.now() - timedelta(days=365)
        )
        initial_capital = st.number_input(
            "Initial Capital (₹)", 
            min_value=10000, 
            value=100000, 
            step=10000
        )
    
    with col2:
        strategy = st.selectbox(
            "Strategy",
            ["SMA", "RSI", "MACD", "Bollinger", "Combined"]
        )
        end_date = st.date_input("End Date", value=datetime.now())
        commission = st.number_input(
            "Commission (%)", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.1, 
            step=0.05
        ) / 100
    
    # Strategy-specific parameters
    strategy_params = {}
    
    if strategy == "SMA":
        col1, col2 = st.columns(2)
        with col1:
            strategy_params['short_window'] = st.number_input(
                "Short MA Period", min_value=5, max_value=50, value=20
            )
        with col2:
            strategy_params['long_window'] = st.number_input(
                "Long MA Period", min_value=20, max_value=200, value=50
            )
    
    elif strategy == "RSI":
        col1, col2 = st.columns(2)
        with col1:
            strategy_params['oversold'] = st.number_input(
                "Oversold Level", min_value=10, max_value=40, value=30
            )
        with col2:
            strategy_params['overbought'] = st.number_input(
                "Overbought Level", min_value=60, max_value=90, value=70
            )
    
    # Run backtest
    if st.button("Run Backtest"):
        if symbol and start_date < end_date:
            with st.spinner("Running backtest..."):
                engine = BacktestEngine(initial_capital)
                
                results = engine.run_backtest(
                    symbol=symbol,
                    strategy_name=strategy,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    commission=commission,
                    **strategy_params
                )
                
                if results:
                    # Performance metrics
                    st.subheader("📈 Performance Metrics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Total Return", 
                            f"{results['total_return']:.2%}"
                        )
                    with col2:
                        st.metric(
                            "Buy & Hold Return", 
                            f"{results['buy_hold_return']:.2%}"
                        )
                    with col3:
                        st.metric(
                            "Excess Return", 
                            f"{results['excess_return']:.2%}",
                            delta=f"{results['excess_return']:.2%}"
                        )
                    with col4:
                        st.metric(
                            "Sharpe Ratio", 
                            f"{results['sharpe_ratio']:.2f}"
                        )
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Max Drawdown", 
                            f"{results['max_drawdown']:.2%}"
                        )
                    with col2:
                        st.metric(
                            "Win Rate", 
                            f"{results['win_rate']['win_rate']:.2%}"
                        )
                    with col3:
                        st.metric(
                            "Total Trades", 
                            results['total_trades']
                        )
                    with col4:
                        st.metric(
                            "Final Value", 
                            f"₹{results['final_value']:,.0f}"
                        )
                    
                    # Charts
                    fig = engine.create_backtest_chart(results)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed trade analysis
                    with st.expander("📊 Detailed Trade Analysis"):
                        trades = engine.extract_trades(results['data'])
                        
                        if trades:
                            trades_df = pd.DataFrame(trades)
                            st.dataframe(trades_df, use_container_width=True)
                            
                            # Trade statistics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("Winning Trades")
                                winning_trades = trades_df[trades_df['profit_loss'] > 0]
                                if not winning_trades.empty:
                                    st.write(f"Count: {len(winning_trades)}")
                                    st.write(f"Avg Profit: ₹{winning_trades['profit_loss'].mean():.2f}")
                                    st.write(f"Best Trade: ₹{winning_trades['profit_loss'].max():.2f}")
                            
                            with col2:
                                st.subheader("Losing Trades")
                                losing_trades = trades_df[trades_df['profit_loss'] < 0]
                                if not losing_trades.empty:
                                    st.write(f"Count: {len(losing_trades)}")
                                    st.write(f"Avg Loss: ₹{losing_trades['profit_loss'].mean():.2f}")
                                    st.write(f"Worst Trade: ₹{losing_trades['profit_loss'].min():.2f}")
                        else:
                            st.info("No trades executed during the backtest period.")
                
                else:
                    st.error("Failed to run backtest. Please check your inputs.")
        else:
            st.error("Please provide valid inputs for the backtest.")
    
    # Strategy comparison
    st.subheader("🔄 Strategy Comparison")
    
    if st.button("Compare All Strategies"):
        if symbol and start_date < end_date:
            with st.spinner("Comparing strategies..."):
                strategies = ["SMA", "RSI", "MACD", "Bollinger", "Combined"]
                comparison_results = []
                
                engine = BacktestEngine(initial_capital)
                
                for strat in strategies:
                    results = engine.run_backtest(
                        symbol=symbol,
                        strategy_name=strat,
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        commission=commission
                    )
                    
                    if results:
                        comparison_results.append({
                            'Strategy': strat,
                            'Total Return': f"{results['total_return']:.2%}",
                            'Excess Return': f"{results['excess_return']:.2%}",
                            'Sharpe Ratio': f"{results['sharpe_ratio']:.2f}",
                            'Max Drawdown': f"{results['max_drawdown']:.2%}",
                            'Win Rate': f"{results['win_rate']['win_rate']:.2%}",
                            'Total Trades': results['total_trades']
                        })
                
                if comparison_results:
                    comparison_df = pd.DataFrame(comparison_results)
                    st.dataframe(comparison_df, use_container_width=True)
                    
                    # Best strategy
                    st.info(
                        f"🏆 Based on total return, the best strategy for {symbol} "
                        f"during this period was: **{comparison_results[0]['Strategy']}**"
                    )
