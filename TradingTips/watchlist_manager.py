"""
Watchlist Management Module for Trading App
"""

import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st


class WatchlistManager:
    """Manage watchlist operations and price alerts."""
    
    def __init__(self, db_path: str = 'trading_app.db'):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """Initialize watchlist and alerts tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                target_price REAL,
                stop_loss REAL,
                notes TEXT,
                added_date TEXT NOT NULL,
                alert_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Price alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,  -- 'above', 'below', 'target', 'stop_loss'
                trigger_price REAL NOT NULL,
                current_price REAL,
                message TEXT,
                created_date TEXT NOT NULL,
                triggered_date TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_to_watchlist(self, symbol: str, target_price: Optional[float] = None, 
                        stop_loss: Optional[float] = None, notes: str = "") -> bool:
        """Add a stock to watchlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO watchlist 
                (symbol, target_price, stop_loss, notes, added_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol.upper(), target_price, stop_loss, notes, 
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error adding to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove a stock from watchlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM watchlist WHERE symbol = ?', (symbol.upper(),))
            cursor.execute('DELETE FROM price_alerts WHERE symbol = ?', (symbol.upper(),))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error removing from watchlist: {e}")
            return False
    
    def get_watchlist(self) -> pd.DataFrame:
        """Get current watchlist."""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query('SELECT * FROM watchlist ORDER BY added_date DESC', conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error getting watchlist: {e}")
            return pd.DataFrame()
    
    def update_watchlist_prices(self, watchlist_df: pd.DataFrame) -> pd.DataFrame:
        """Update watchlist with current market prices and calculate metrics."""
        if watchlist_df.empty:
            return watchlist_df
        
        for idx, row in watchlist_df.iterrows():
            try:
                stock = yf.Ticker(row['symbol'])
                current_data = stock.history(period='1d')
                
                if not current_data.empty:
                    current_price = current_data['Close'].iloc[-1]
                    prev_close = current_data['Close'].iloc[0] if len(current_data) > 1 else current_price
                    
                    watchlist_df.loc[idx, 'current_price'] = current_price
                    watchlist_df.loc[idx, 'day_change'] = current_price - prev_close
                    watchlist_df.loc[idx, 'day_change_pct'] = ((current_price - prev_close) / prev_close) * 100
                    
                    # Calculate distance to target and stop loss
                    if pd.notna(row['target_price']):
                        target_distance = ((row['target_price'] - current_price) / current_price) * 100
                        watchlist_df.loc[idx, 'target_distance_pct'] = target_distance
                    
                    if pd.notna(row['stop_loss']):
                        stop_distance = ((current_price - row['stop_loss']) / current_price) * 100
                        watchlist_df.loc[idx, 'stop_distance_pct'] = stop_distance
                    
                    # Get additional info
                    info = stock.info
                    watchlist_df.loc[idx, 'volume'] = info.get('volume', 0)
                    watchlist_df.loc[idx, 'market_cap'] = info.get('marketCap', 0)
                    watchlist_df.loc[idx, 'pe_ratio'] = info.get('trailingPE', 0)
                
            except Exception as e:
                st.warning(f"Could not fetch data for {row['symbol']}: {e}")
                watchlist_df.loc[idx, 'current_price'] = 0
        
        return watchlist_df
    
    def add_price_alert(self, symbol: str, alert_type: str, trigger_price: float, 
                       message: str = "") -> bool:
        """Add a price alert for a stock."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_alerts 
                (symbol, alert_type, trigger_price, message, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol.upper(), alert_type, trigger_price, message,
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error adding price alert: {e}")
            return False
    
    def check_price_alerts(self) -> List[Dict]:
        """Check for triggered price alerts."""
        triggered_alerts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get active alerts
            cursor.execute('SELECT * FROM price_alerts WHERE is_active = 1')
            alerts = cursor.fetchall()
            
            for alert in alerts:
                symbol = alert[1]
                alert_type = alert[2]
                trigger_price = alert[3]
                alert_id = alert[0]
                
                try:
                    # Get current price
                    stock = yf.Ticker(symbol)
                    current_price = stock.history(period='1d')['Close'].iloc[-1]
                    
                    triggered = False
                    
                    if alert_type == 'above' and current_price >= trigger_price:
                        triggered = True
                    elif alert_type == 'below' and current_price <= trigger_price:
                        triggered = True
                    
                    if triggered:
                        # Mark alert as triggered
                        cursor.execute('''
                            UPDATE price_alerts 
                            SET is_active = 0, triggered_date = ?, current_price = ?
                            WHERE id = ?
                        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                             current_price, alert_id))
                        
                        triggered_alerts.append({
                            'symbol': symbol,
                            'alert_type': alert_type,
                            'trigger_price': trigger_price,
                            'current_price': current_price,
                            'message': alert[4] or f"{symbol} reached {trigger_price}"
                        })
                
                except Exception as e:
                    st.warning(f"Error checking alert for {symbol}: {e}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error checking price alerts: {e}")
        
        return triggered_alerts
    
    def get_watchlist_summary(self) -> Dict:
        """Get summary statistics for watchlist."""
        try:
            watchlist_df = self.get_watchlist()
            
            if watchlist_df.empty:
                return {
                    'total_stocks': 0,
                    'avg_target_distance': 0,
                    'stocks_near_target': 0,
                    'stocks_near_stop': 0,
                    'active_alerts': 0
                }
            
            watchlist_df = self.update_watchlist_prices(watchlist_df)
            
            # Calculate summary stats
            total_stocks = len(watchlist_df)
            
            # Stocks with targets
            stocks_with_targets = watchlist_df[watchlist_df['target_price'].notna()]
            avg_target_distance = stocks_with_targets['target_distance_pct'].mean() if not stocks_with_targets.empty else 0
            
            # Stocks near target (within 5%)
            stocks_near_target = len(stocks_with_targets[
                (stocks_with_targets['target_distance_pct'] <= 5) & 
                (stocks_with_targets['target_distance_pct'] >= -5)
            ])
            
            # Stocks near stop loss (within 5%)
            stocks_with_stops = watchlist_df[watchlist_df['stop_loss'].notna()]
            stocks_near_stop = len(stocks_with_stops[
                (stocks_with_stops['stop_distance_pct'] <= 5) & 
                (stocks_with_stops['stop_distance_pct'] >= 0)
            ])
            
            # Get active alerts count with error handling
            try:
                active_alerts_count = self.get_active_alerts_count()
            except Exception:
                active_alerts_count = 0
            
            return {
                'total_stocks': total_stocks,
                'avg_target_distance': avg_target_distance,
                'stocks_near_target': stocks_near_target,
                'stocks_near_stop': stocks_near_stop,
                'active_alerts': active_alerts_count
            }
        except Exception as e:
            st.error(f"Error getting watchlist summary: {e}")
            return {
                'total_stocks': 0,
                'avg_target_distance': 0,
                'stocks_near_target': 0,
                'stocks_near_stop': 0,
                'active_alerts': 0
            }
    
    def get_active_alerts_count(self) -> int:
        """Get count of active price alerts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM price_alerts WHERE is_active = 1')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            # If table doesn't exist or other error, return 0
            return 0
    
    def get_top_movers(self, limit: int = 5) -> pd.DataFrame:
        """Get top movers from watchlist."""
        watchlist_df = self.get_watchlist()
        
        if watchlist_df.empty:
            return pd.DataFrame()
        
        watchlist_df = self.update_watchlist_prices(watchlist_df)
        
        # Sort by day change percentage
        top_gainers = watchlist_df.nlargest(limit, 'day_change_pct')
        top_losers = watchlist_df.nsmallest(limit, 'day_change_pct')
        
        return {
            'gainers': top_gainers[['symbol', 'current_price', 'day_change', 'day_change_pct']],
            'losers': top_losers[['symbol', 'current_price', 'day_change', 'day_change_pct']]
        }


def create_watchlist_ui():
    """Create Streamlit UI for watchlist management."""
    st.header("👁️ Watchlist Management")
    
    try:
        watchlist_manager = WatchlistManager()
        
        # Watchlist summary with error handling
        try:
            summary = watchlist_manager.get_watchlist_summary()
        except Exception as e:
            st.error(f"Error loading watchlist summary: {e}")
            summary = {
                'total_stocks': 0,
                'stocks_near_target': 0,
                'stocks_near_stop': 0,
                'active_alerts': 0
            }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Stocks", summary.get('total_stocks', 0))
        with col2:
            st.metric("Near Target", summary.get('stocks_near_target', 0))
        with col3:
            st.metric("Near Stop Loss", summary.get('stocks_near_stop', 0))
        with col4:
            st.metric("Active Alerts", summary.get('active_alerts', 0))
        
        # Add to watchlist section
        with st.expander("➕ Add Stock to Watchlist"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_symbol = st.text_input("Stock Symbol", placeholder="e.g., RELIANCE.NS")
            with col2:
                target_price = st.number_input("Target Price (₹)", min_value=0.0, value=0.0)
            with col3:
                stop_loss = st.number_input("Stop Loss (₹)", min_value=0.0, value=0.0)
            
            notes = st.text_area("Notes", placeholder="Investment thesis, alerts, etc.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add to Watchlist"):
                    if new_symbol:
                        success = watchlist_manager.add_to_watchlist(
                            new_symbol, 
                            target_price if target_price > 0 else None,
                            stop_loss if stop_loss > 0 else None,
                            notes
                        )
                        if success:
                            st.success(f"Added {new_symbol} to watchlist!")
                            st.rerun()
            
            with col2:
                if st.button("Add Price Alert"):
                    if new_symbol and target_price > 0:
                        alert_type = "above" if target_price > 0 else "below"
                        success = watchlist_manager.add_price_alert(
                            new_symbol, alert_type, target_price,
                            f"Price alert for {new_symbol} at ₹{target_price}"
                        )
                        if success:
                            st.success(f"Added price alert for {new_symbol}!")
        
        # Display watchlist
        watchlist_df = watchlist_manager.get_watchlist()
        
        if not watchlist_df.empty:
            st.subheader("📊 Current Watchlist")
            
            # Update with current prices
            updated_df = watchlist_manager.update_watchlist_prices(watchlist_df)
            
            # Format for display
            display_columns = ['symbol', 'current_price', 'day_change', 'day_change_pct',
                              'target_price', 'target_distance_pct', 'stop_loss', 'stop_distance_pct']
            
            if all(col in updated_df.columns for col in display_columns):
                display_df = updated_df[display_columns].copy()
                display_df.columns = ['Symbol', 'Current Price', 'Day Change', 'Day Change %',
                                    'Target Price', 'Target Distance %', 'Stop Loss', 'Stop Distance %']
                
                # Simple display without styling for now
                st.dataframe(display_df, use_container_width=True)
                
                # Remove from watchlist
                col1, col2 = st.columns([3, 1])
                with col1:
                    symbol_to_remove = st.selectbox(
                        "Remove from watchlist:", 
                        [""] + updated_df['symbol'].tolist()
                    )
                with col2:
                    if st.button("Remove") and symbol_to_remove:
                        success = watchlist_manager.remove_from_watchlist(symbol_to_remove)
                        if success:
                            st.success(f"Removed {symbol_to_remove} from watchlist!")
                            st.rerun()
            
            # Top movers
            try:
                movers = watchlist_manager.get_top_movers(3)
                if isinstance(movers, dict) and not movers['gainers'].empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 Top Gainers")
                        st.dataframe(movers['gainers'], use_container_width=True)
                    
                    with col2:
                        st.subheader("📉 Top Losers")
                        st.dataframe(movers['losers'], use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load top movers: {e}")
        
        else:
            st.info("Your watchlist is empty. Add some stocks to get started!")
        
        # Check for triggered alerts
        try:
            triggered_alerts = watchlist_manager.check_price_alerts()
            if triggered_alerts:
                st.subheader("🚨 Triggered Alerts")
                for alert in triggered_alerts:
                    st.warning(
                        f"**{alert['symbol']}** - {alert['message']} "
                        f"(Current: ₹{alert['current_price']:.2f})"
                    )
        except Exception as e:
            st.warning(f"Could not check alerts: {e}")
    
    except Exception as e:
        st.error(f"Error loading watchlist: {e}")
        st.info("There might be an issue with the database. Please try refreshing the page.")
