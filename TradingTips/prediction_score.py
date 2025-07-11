"""
Simple Prediction Scoring Enhancement for Trading App
Add this to improve prediction accuracy
"""

def calculate_prediction_score(df, symbol_info=None):
    """Calculate a simple prediction score from 0-100 based on technical indicators."""
    try:
        if df is None or df.empty:
            return 50, "No Data"
        
        latest = df.iloc[-1]
        score = 50  # Start neutral
        
        # RSI scoring (30 points max)
        rsi = latest.get('RSI', 50)
        if rsi < 30:  # Oversold - potential buy
            score += 15
        elif rsi > 70:  # Overbought - potential sell
            score -= 15
        elif 40 <= rsi <= 60:  # Neutral zone
            score += 5
        
        # MACD scoring (20 points max)
        macd = latest.get('MACD', 0)
        macd_signal = latest.get('MACD_Signal', 0)
        if macd > macd_signal:  # Bullish
            score += 10
        else:  # Bearish
            score -= 10
        
        # Moving Average scoring (20 points max)
        current_price = latest['Close']
        sma_20 = latest.get('SMA_20', current_price)
        sma_50 = latest.get('SMA_50', current_price)
        
        if current_price > sma_20 > sma_50:  # Strong uptrend
            score += 15
        elif current_price < sma_20 < sma_50:  # Strong downtrend
            score -= 15
        elif current_price > sma_20:  # Above short-term MA
            score += 8
        else:
            score -= 8
        
        # Volume scoring (15 points max)
        volume_ratio = latest.get('Volume_Ratio', 1)
        if volume_ratio > 1.5:  # High volume confirms move
            score += 10
        elif volume_ratio < 0.8:  # Low volume weakens signal
            score -= 5
        
        # Bollinger Bands scoring (15 points max)
        bb_upper = latest.get('BB_Upper', current_price)
        bb_lower = latest.get('BB_Lower', current_price)
        
        if current_price < bb_lower:  # Oversold
            score += 10
        elif current_price > bb_upper:  # Overbought
            score -= 10
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Determine recommendation
        if score >= 75:
            recommendation = "Strong Buy"
        elif score >= 65:
            recommendation = "Buy"
        elif score >= 55:
            recommendation = "Weak Buy"
        elif score >= 45:
            recommendation = "Hold"
        elif score >= 35:
            recommendation = "Weak Sell"
        elif score >= 25:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"
        
        return score, recommendation
        
    except Exception as e:
        return 50, f"Error: {str(e)}"
