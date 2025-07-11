"""
Advanced Prediction Engine for Trading App
Combines technical analysis, machine learning, and fundamental analysis
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Tuple, Optional
import ta
import joblib
import os

class AdvancedPredictionEngine:
    """Advanced prediction engine using ML and comprehensive analysis."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.feature_importance = {}
        
    def calculate_advanced_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators."""
        try:
            # Basic price features
            df['Returns'] = df['Close'].pct_change()
            df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
            df['Volatility'] = df['Returns'].rolling(window=20).std()
            
            # Price-based indicators
            df['Price_Position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'])
            df['Upper_Shadow'] = df['High'] - np.maximum(df['Open'], df['Close'])
            df['Lower_Shadow'] = np.minimum(df['Open'], df['Close']) - df['Low']
            df['Body_Size'] = abs(df['Close'] - df['Open'])
            
            # Advanced Moving Averages
            for period in [5, 10, 20, 50, 100, 200]:
                df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
                df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()
                if period <= 50:  # Avoid too many features
                    df[f'Price_vs_SMA_{period}'] = df['Close'] / df[f'SMA_{period}'] - 1
                    df[f'Price_vs_EMA_{period}'] = df['Close'] / df[f'EMA_{period}'] - 1
            
            # Momentum Indicators
            df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
            df['RSI_SMA'] = df['RSI'].rolling(window=5).mean()
            df['Stoch_K'] = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close']).stoch()
            df['Stoch_D'] = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close']).stoch_signal()
            df['Williams_R'] = ta.momentum.WilliamsRIndicator(df['High'], df['Low'], df['Close']).williams_r()
            
            # MACD Family
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            df['MACD_Histogram'] = macd.macd_diff()
            df['MACD_Ratio'] = df['MACD'] / df['MACD_Signal']
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['Close'])
            df['BB_Upper'] = bollinger.bollinger_hband()
            df['BB_Lower'] = bollinger.bollinger_lband()
            df['BB_Middle'] = bollinger.bollinger_mavg()
            df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
            
            # Volume Indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
            df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
            df['Volume_Price_Trend'] = ta.volume.VolumePriceTrendIndicator(df['Close'], df['Volume']).volume_price_trend()
            
            # Trend Indicators
            df['ADX'] = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close']).adx()
            df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close']).cci()
            
            # Support and Resistance Levels
            df['Resistance_20'] = df['High'].rolling(window=20).max()
            df['Support_20'] = df['Low'].rolling(window=20).min()
            df['Distance_to_Resistance'] = (df['Resistance_20'] - df['Close']) / df['Close']
            df['Distance_to_Support'] = (df['Close'] - df['Support_20']) / df['Close']
            
            # Fibonacci Retracements
            high_20 = df['High'].rolling(window=20).max()
            low_20 = df['Low'].rolling(window=20).min()
            df['Fib_23.6'] = high_20 - 0.236 * (high_20 - low_20)
            df['Fib_38.2'] = high_20 - 0.382 * (high_20 - low_20)
            df['Fib_61.8'] = high_20 - 0.618 * (high_20 - low_20)
            
            # Market Microstructure
            df['Spread'] = df['High'] - df['Low']
            df['True_Range'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
            
            # Pattern Recognition Features
            df['Higher_High'] = ((df['High'] > df['High'].shift(1)) & (df['High'].shift(1) > df['High'].shift(2))).astype(int)
            df['Lower_Low'] = ((df['Low'] < df['Low'].shift(1)) & (df['Low'].shift(1) < df['Low'].shift(2))).astype(int)
            df['Doji'] = (abs(df['Close'] - df['Open']) <= 0.001 * df['Close']).astype(int)
            
            # Cyclical Features
            df['Day_of_Week'] = pd.to_datetime(df.index).dayofweek
            df['Month'] = pd.to_datetime(df.index).month
            df['Quarter'] = pd.to_datetime(df.index).quarter
            
            return df
            
        except Exception as e:
            st.error(f"Error calculating technical indicators: {e}")
            return df
    
    def prepare_features(self, df: pd.DataFrame, target_days: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for machine learning."""
        try:
            # Calculate technical indicators
            df = self.calculate_advanced_technical_indicators(df)
            
            # Create target variable (future returns)
            df['Target'] = df['Close'].shift(-target_days) / df['Close'] - 1
            
            # Select features (excluding target and non-numeric columns)
            feature_columns = [col for col in df.columns if col not in ['Target', 'Open', 'High', 'Low', 'Close', 'Volume']]
            feature_columns = [col for col in feature_columns if df[col].dtype in ['float64', 'int64']]
            
            # Remove rows with missing values
            df_clean = df.dropna()
            
            if len(df_clean) < 50:  # Need minimum data
                raise ValueError("Insufficient data for training")
            
            X = df_clean[feature_columns].values
            y = df_clean['Target'].values
            
            return X, y, feature_columns
            
        except Exception as e:
            st.error(f"Error preparing features: {e}")
            return np.array([]), np.array([]), []
    
    def train_prediction_models(self, symbol: str, period: str = "2y") -> Dict:
        """Train multiple ML models for price prediction."""
        try:
            # Get stock data
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Prepare features
            X, y, feature_columns = self.prepare_features(df)
            
            if len(X) == 0:
                raise ValueError("No valid features prepared")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train multiple models
            models = {
                'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
                'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=6)
            }
            
            results = {}
            
            for name, model in models.items():
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    importance = dict(zip(feature_columns, model.feature_importances_))
                    top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
                else:
                    top_features = []
                
                results[name] = {
                    'model': model,
                    'mse': mse,
                    'r2': r2,
                    'accuracy': max(0, r2 * 100),  # Convert R² to percentage
                    'top_features': top_features
                }
            
            # Store best model
            best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
            self.models[symbol] = results[best_model_name]['model']
            self.feature_importance[symbol] = results[best_model_name]['top_features']
            
            return results
            
        except Exception as e:
            st.error(f"Error training models: {e}")
            return {}
    
    def predict_price_movement(self, symbol: str, days_ahead: int = 5) -> Dict:
        """Predict future price movement using trained models."""
        try:
            # Get recent data
            stock = yf.Ticker(symbol)
            df = stock.history(period="6mo")
            
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # If no model exists, train one
            if symbol not in self.models:
                self.train_prediction_models(symbol)
            
            # Prepare features for prediction
            df_with_indicators = self.calculate_advanced_technical_indicators(df)
            
            # Get latest features
            feature_columns = [col for col in df_with_indicators.columns 
                             if col not in ['Open', 'High', 'Low', 'Close', 'Volume'] 
                             and df_with_indicators[col].dtype in ['float64', 'int64']]
            
            latest_features = df_with_indicators[feature_columns].iloc[-1:].fillna(0)
            
            # Scale features
            latest_scaled = self.scaler.transform(latest_features)
            
            # Make prediction
            model = self.models[symbol]
            predicted_return = model.predict(latest_scaled)[0]
            
            # Calculate confidence based on model performance and market conditions
            current_volatility = df['Close'].pct_change().rolling(20).std().iloc[-1]
            base_confidence = max(50, min(90, (1 - abs(predicted_return)) * 100))
            volatility_adjustment = max(0.5, 1 - current_volatility * 10)
            confidence = base_confidence * volatility_adjustment
            
            # Determine signal strength
            if abs(predicted_return) > 0.05:  # > 5% predicted move
                signal_strength = "Strong"
            elif abs(predicted_return) > 0.02:  # > 2% predicted move
                signal_strength = "Moderate"
            else:
                signal_strength = "Weak"
            
            # Calculate target price
            current_price = df['Close'].iloc[-1]
            target_price = current_price * (1 + predicted_return)
            
            # Risk assessment
            recent_volatility = df['Close'].pct_change().tail(10).std() * np.sqrt(252)  # Annualized
            if recent_volatility > 0.3:
                risk_level = "High"
            elif recent_volatility > 0.2:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            return {
                'predicted_return': predicted_return,
                'target_price': target_price,
                'current_price': current_price,
                'confidence': confidence,
                'signal_strength': signal_strength,
                'risk_level': risk_level,
                'direction': 'Bullish' if predicted_return > 0 else 'Bearish',
                'days_ahead': days_ahead,
                'top_factors': self.feature_importance.get(symbol, [])
            }
            
        except Exception as e:
            st.error(f"Error making prediction: {e}")
            return {}
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """Get comprehensive analysis combining multiple approaches."""
        try:
            # Get stock data and info
            stock = yf.Ticker(symbol)
            df = stock.history(period="1y")
            info = stock.info
            
            if df.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Technical Analysis
            df = self.calculate_advanced_technical_indicators(df)
            
            current_price = df['Close'].iloc[-1]
            
            # Technical signals
            technical_signals = {
                'RSI': 'Overbought' if df['RSI'].iloc[-1] > 70 else 'Oversold' if df['RSI'].iloc[-1] < 30 else 'Neutral',
                'MACD': 'Bullish' if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1] else 'Bearish',
                'BB_Position': 'Upper Band' if df['BB_Position'].iloc[-1] > 0.8 else 'Lower Band' if df['BB_Position'].iloc[-1] < 0.2 else 'Middle',
                'Trend': 'Uptrend' if current_price > df['SMA_50'].iloc[-1] else 'Downtrend',
                'Volume': 'High' if df['Volume_Ratio'].iloc[-1] > 1.5 else 'Normal'
            }
            
            # Support and Resistance
            support_resistance = {
                'support_20d': df['Support_20'].iloc[-1],
                'resistance_20d': df['Resistance_20'].iloc[-1],
                'fibonacci_levels': {
                    '23.6%': df['Fib_23.6'].iloc[-1],
                    '38.2%': df['Fib_38.2'].iloc[-1],
                    '61.8%': df['Fib_61.8'].iloc[-1]
                }
            }
            
            # Fundamental ratios (if available)
            fundamentals = {
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'pb_ratio': info.get('priceToBook', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'roe': info.get('returnOnEquity', 'N/A'),
                'profit_margin': info.get('profitMargins', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A')
            }
            
            # ML Prediction
            ml_prediction = self.predict_price_movement(symbol)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'technical_signals': technical_signals,
                'support_resistance': support_resistance,
                'fundamentals': fundamentals,
                'ml_prediction': ml_prediction,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"Error in comprehensive analysis: {e}")
            return {}
    
    def generate_enhanced_ai_prompt(self, analysis_data: Dict) -> str:
        """Generate enhanced AI prompt with comprehensive data."""
        try:
            symbol = analysis_data['symbol']
            current_price = analysis_data['current_price']
            tech_signals = analysis_data['technical_signals']
            support_resistance = analysis_data['support_resistance']
            fundamentals = analysis_data['fundamentals']
            ml_prediction = analysis_data.get('ml_prediction', {})
            
            prompt = f"""
Perform a comprehensive analysis of {symbol} stock with the following data:

CURRENT MARKET DATA:
- Current Price: ₹{current_price:.2f}
- Market Cap: {fundamentals.get('market_cap', 'N/A')}

TECHNICAL ANALYSIS:
- RSI Signal: {tech_signals['RSI']} (Value: {tech_signals.get('rsi_value', 'N/A')})
- MACD Signal: {tech_signals['MACD']}
- Bollinger Band Position: {tech_signals['BB_Position']}
- Overall Trend: {tech_signals['Trend']}
- Volume: {tech_signals['Volume']}

SUPPORT & RESISTANCE:
- 20-day Support: ₹{support_resistance['support_20d']:.2f}
- 20-day Resistance: ₹{support_resistance['resistance_20d']:.2f}
- Key Fibonacci Levels: {support_resistance['fibonacci_levels']}

FUNDAMENTAL METRICS:
- P/E Ratio: {fundamentals['pe_ratio']}
- P/B Ratio: {fundamentals['pb_ratio']}
- Debt-to-Equity: {fundamentals['debt_to_equity']}
- ROE: {fundamentals['roe']}
- Profit Margin: {fundamentals['profit_margin']}

MACHINE LEARNING PREDICTION:
- Predicted Direction: {ml_prediction.get('direction', 'N/A')}
- Target Price: ₹{ml_prediction.get('target_price', 0):.2f}
- Confidence Level: {ml_prediction.get('confidence', 0):.1f}%
- Signal Strength: {ml_prediction.get('signal_strength', 'N/A')}
- Risk Level: {ml_prediction.get('risk_level', 'N/A')}
- Key Factors: {ml_prediction.get('top_factors', [])}

Based on this comprehensive analysis, provide:

1. **Overall Recommendation**: BUY/SELL/HOLD with confidence level
2. **Entry Strategy**: Optimal entry price and timing
3. **Risk Management**: Stop-loss and position sizing recommendations
4. **Target Prices**: Multiple target levels (conservative, moderate, aggressive)
5. **Time Horizon**: Short-term (1-4 weeks) and medium-term (1-3 months) outlook
6. **Key Risks**: Major risks to watch out for
7. **Catalyst Events**: Upcoming events that could impact the stock

Provide specific price levels, percentages, and actionable insights. Consider both technical and fundamental factors in your analysis.
"""
            
            return prompt
            
        except Exception as e:
            return f"Error generating enhanced prompt: {e}"


def create_prediction_ui():
    """Create UI for advanced prediction features."""
    st.header("🔮 Advanced Prediction Engine")
    
    # Initialize prediction engine
    if 'prediction_engine' not in st.session_state:
        st.session_state.prediction_engine = AdvancedPredictionEngine()
    
    engine = st.session_state.prediction_engine
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol", value="RELIANCE.NS")
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Quick Prediction", "Comprehensive Analysis", "Model Training"]
        )
    
    with col2:
        confidence_threshold = st.slider("Min Confidence %", 50, 95, 70)
        prediction_days = st.selectbox("Prediction Horizon", [1, 3, 5, 7, 10], index=2)
    
    if st.button("🚀 Generate Advanced Analysis", type="primary"):
        if symbol:
            with st.spinner("Running advanced analysis..."):
                
                if analysis_type == "Model Training":
                    st.subheader("🤖 Model Training Results")
                    
                    training_results = engine.train_prediction_models(symbol)
                    
                    if training_results:
                        for model_name, results in training_results.items():
                            with st.expander(f"📊 {model_name} Performance"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Accuracy", f"{results['accuracy']:.1f}%")
                                with col2:
                                    st.metric("R² Score", f"{results['r2']:.3f}")
                                with col3:
                                    st.metric("MSE", f"{results['mse']:.6f}")
                                
                                st.write("**Top Important Features:**")
                                for feature, importance in results['top_features']:
                                    st.write(f"- {feature}: {importance:.3f}")
                
                elif analysis_type == "Quick Prediction":
                    st.subheader("⚡ Quick ML Prediction")
                    
                    prediction = engine.predict_price_movement(symbol, prediction_days)
                    
                    if prediction:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            direction_color = "green" if prediction['direction'] == 'Bullish' else "red"
                            st.markdown(
                                f"**Direction:** <span style='color: {direction_color}'>{prediction['direction']}</span>",
                                unsafe_allow_html=True
                            )
                        
                        with col2:
                            st.metric("Target Price", f"₹{prediction['target_price']:.2f}")
                        
                        with col3:
                            st.metric("Confidence", f"{prediction['confidence']:.1f}%")
                        
                        with col4:
                            st.metric("Signal Strength", prediction['signal_strength'])
                        
                        # Additional details
                        st.write("**Key Prediction Factors:**")
                        for factor, importance in prediction['top_factors'][:5]:
                            st.write(f"- {factor}: {importance:.3f}")
                        
                        if prediction['confidence'] >= confidence_threshold:
                            st.success(f"✅ High confidence prediction meets your threshold of {confidence_threshold}%")
                        else:
                            st.warning(f"⚠️ Prediction confidence ({prediction['confidence']:.1f}%) below threshold ({confidence_threshold}%)")
                
                else:  # Comprehensive Analysis
                    st.subheader("📊 Comprehensive Analysis")
                    
                    analysis = engine.get_comprehensive_analysis(symbol)
                    
                    if analysis:
                        # Technical Signals
                        st.write("**Technical Signals:**")
                        cols = st.columns(len(analysis['technical_signals']))
                        for i, (signal, value) in enumerate(analysis['technical_signals'].items()):
                            with cols[i]:
                                st.metric(signal, value)
                        
                        # Support/Resistance
                        with st.expander("📈 Support & Resistance Levels"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Support (20D)", f"₹{analysis['support_resistance']['support_20d']:.2f}")
                            with col2:
                                st.metric("Resistance (20D)", f"₹{analysis['support_resistance']['resistance_20d']:.2f}")
                            
                            st.write("**Fibonacci Retracement Levels:**")
                            for level, price in analysis['support_resistance']['fibonacci_levels'].items():
                                st.write(f"- {level}: ₹{price:.2f}")
                        
                        # Fundamentals
                        with st.expander("💼 Fundamental Analysis"):
                            fund_cols = st.columns(3)
                            fundamentals = analysis['fundamentals']
                            
                            with fund_cols[0]:
                                st.metric("P/E Ratio", fundamentals['pe_ratio'])
                                st.metric("ROE", fundamentals['roe'])
                            
                            with fund_cols[1]:
                                st.metric("P/B Ratio", fundamentals['pb_ratio'])
                                st.metric("Profit Margin", fundamentals['profit_margin'])
                            
                            with fund_cols[2]:
                                st.metric("Debt/Equity", fundamentals['debt_to_equity'])
                        
                        # ML Prediction
                        if 'ml_prediction' in analysis and analysis['ml_prediction']:
                            ml_pred = analysis['ml_prediction']
                            st.write("**Machine Learning Prediction:**")
                            
                            pred_cols = st.columns(4)
                            with pred_cols[0]:
                                st.metric("Direction", ml_pred['direction'])
                            with pred_cols[1]:
                                st.metric("Target Price", f"₹{ml_pred['target_price']:.2f}")
                            with pred_cols[2]:
                                st.metric("Confidence", f"{ml_pred['confidence']:.1f}%")
                            with pred_cols[3]:
                                st.metric("Risk Level", ml_pred['risk_level'])
                        
                        # Enhanced AI Analysis
                        st.write("**🤖 Enhanced AI Analysis:**")
                        if st.button("Generate Enhanced AI Insights"):
                            enhanced_prompt = engine.generate_enhanced_ai_prompt(analysis)
                            
                            # Here you would call your Azure OpenAI with the enhanced prompt
                            st.text_area("Enhanced Analysis Prompt", enhanced_prompt, height=200)
                            st.info("Use this enhanced prompt with your Azure OpenAI service for superior analysis")
        else:
            st.error("Please enter a stock symbol")
    
    # Model Performance Dashboard
    with st.expander("📊 Model Performance Dashboard"):
        st.write("**Prediction Engine Statistics:**")
        
        if st.session_state.prediction_engine.models:
            st.write(f"Trained Models: {len(st.session_state.prediction_engine.models)}")
            for symbol in st.session_state.prediction_engine.models.keys():
                st.write(f"- {symbol}")
        else:
            st.info("No models trained yet. Train a model using the 'Model Training' option.")
    
    # Tips and Information
    with st.expander("💡 How Advanced Predictions Work"):
        st.markdown("""
        **This advanced prediction engine uses:**
        
        1. **80+ Technical Indicators**: RSI, MACD, Bollinger Bands, ADX, CCI, Fibonacci levels, and more
        2. **Machine Learning Models**: Random Forest and Gradient Boosting algorithms
        3. **Feature Engineering**: Price patterns, volume analysis, market microstructure
        4. **Fundamental Analysis**: P/E, P/B, ROE, debt ratios integration
        5. **Risk Assessment**: Volatility analysis and confidence scoring
        6. **Multi-timeframe Analysis**: Short-term and medium-term predictions
        
        **Confidence Levels:**
        - 90%+: Very High (strong signals across multiple indicators)
        - 80-90%: High (good agreement between technical and fundamental factors)
        - 70-80%: Medium (moderate signals with some uncertainty)
        - 60-70%: Low (weak signals, higher risk)
        - <60%: Very Low (conflicting signals, avoid trading)
        """)
