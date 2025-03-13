import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from datetime import datetime, timedelta
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json, logging
from typing import List

# Load environment variables
load_dotenv()

# Initialize Gemini AI client
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def calculate_risk_metrics(financial_data: pd.DataFrame) -> dict:
    returns = financial_data['Close'].pct_change().dropna()
    
    if returns.empty:
        return {
            'value_at_risk': None,
            'conditional_var': None,
            'sharpe_ratio': None,
            'max_drawdown': None
        }

    risk_metrics = {
        'value_at_risk': float(np.percentile(returns, 5)),
        'conditional_var': float(returns[returns <= np.percentile(returns, 5)].mean()),
        'sharpe_ratio': float(calculate_sharpe_ratio(returns)),
        'max_drawdown': float(calculate_max_drawdown(financial_data['Close']))
    }
    
    return risk_metrics

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    excess_returns = returns - (risk_free_rate / 252)
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(prices: pd.Series) -> float:
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return float(drawdown.min())

def calculate_rsi(prices: pd.Series, periods: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ml_enhanced_prediction(financial_data: pd.DataFrame) -> dict:
    if financial_data is None or financial_data.empty:
        raise ValueError("Input financial data is empty")

    # Create features with lowercase column names
    features = pd.DataFrame({
        'close': financial_data['Close'],
        'ma_10': financial_data['Close'].rolling(window=10, min_periods=1).mean(),
        'ma_50': financial_data['Close'].rolling(window=50, min_periods=1).mean(),
        'rsi': calculate_rsi(financial_data['Close']),
        'volume': financial_data['Volume'].ffill()
    })
    
    features = features.dropna()
    feature_columns = ['ma_10', 'ma_50', 'rsi', 'volume']
    X = features[feature_columns]
    y = features['close']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    xgb_model.fit(X_train_scaled, y_train)
    
    # Convert numpy types to Python native types
    feature_importance = {k: float(v) for k, v in zip(feature_columns, xgb_model.feature_importances_)}
    
    # Generate forecast values
    last_data = X.iloc[-1:].copy()
    last_close = float(financial_data['Close'].iloc[-1])
    forecast_values = generate_forecast(xgb_model, scaler, last_data, last_close, feature_columns)
    
    return {
        'forecast_values': [float(x) for x in forecast_values],  # Convert numpy floats to Python floats
        'feature_importance': feature_importance,
        'data_points': int(len(features)),
        'last_price': float(last_close)
    }

def generate_forecast(model, scaler, last_data, last_close, feature_columns, forecast_period: int = 30) -> List[float]:
    forecasted_values = [float(last_close)]  # Convert to Python float
    current_data = last_data.copy()
    
    for _ in range(forecast_period):
        # Scale the current data
        scaled_data = scaler.transform(current_data)
        # Make prediction and convert to Python float
        prediction = float(model.predict(scaled_data)[0])
        forecasted_values.append(prediction)
        
        # Update the current data for the next prediction
        prev_ma10 = float(current_data['ma_10'].iloc[0])
        prev_ma50 = float(current_data['ma_50'].iloc[0])
        
        # Update moving averages based on the new prediction
        current_data['ma_10'] = float((prev_ma10 * 9 + prediction) / 10)
        current_data['ma_50'] = float((prev_ma50 * 49 + prediction) / 50)
        
        # Calculate RSI using a simplified method
        rsi_lookback = 14
        if len(forecasted_values) >= rsi_lookback:
            changes = pd.Series(forecasted_values[-rsi_lookback:]).diff().dropna()
            gains = float(changes[changes > 0].mean() or 0)
            losses = float(-changes[changes < 0].mean() or 0)
            rs = gains / losses if losses != 0 else 0
            current_data['rsi'] = float(100 - (100 / (1 + rs)) if rs != 0 else 50)
        else:
            current_data['rsi'] = 50.0
        
        # Keep volume constant
        current_data['volume'] = float(current_data['volume'].iloc[0])
    
    return forecasted_values

def load_financial_data(symbol: str, period: str = '2y') -> pd.DataFrame:
    try:
        data = yf.download(symbol, period=period)
        return data
    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")

def get_ai_prediction(financial_data: pd.DataFrame, context: str, asset_type: str) -> dict:
    # Format the data for AI analysis
    recent_data = financial_data.tail(30)
    price_change = ((recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0]) - 1) * 100
    volatility = recent_data['Close'].pct_change().std() * np.sqrt(252) * 100
    current_price = recent_data['Close'].iloc[-1]
    
    prompt = f"""Analyze this {asset_type} with:
    - Current price: ${current_price:.2f}
    - Price change: {price_change:.2f}%
    - Volatility: {volatility:.2f}%
    - Context: {context}
    
    Provide a JSON response in the following format:
    {{
        "trend": "brief description of overall trend",
        "factors": ["factor1", "factor2", "factor3"],
        "risks": ["risk1", "risk2", "risk3"],
        "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
        "forecast": {{
            "month1": expected_percentage_change_1,
            "month2": expected_percentage_change_2,
            "month3": expected_percentage_change_3
        }}
    }}
    
    Ensure all values are realistic and based on the provided data. Return only valid JSON."""
    
    try:
        response = model.generate_content(prompt)
        prediction = response.text.strip()
        
        # Remove any markdown formatting if present
        prediction = prediction.replace("```json", "").replace("```", "").strip()
        
        try:
            result = json.loads(prediction)
            # Validate forecast values are numbers
            for key in ['month1', 'month2', 'month3']:
                if not isinstance(result['forecast'][key], (int, float)):
                    result['forecast'][key] = 0.0
            return result
        except json.JSONDecodeError:
            return {
                "trend": f"Price changed by {price_change:.2f}% over the period",
                "factors": ["Market conditions", "Company performance", "Economic indicators"],
                "risks": ["Market volatility", "Economic uncertainty", "Competition"],
                "opportunities": ["Growth potential", "Market expansion", "Innovation"],
                "forecast": {
                    "month1": price_change / 3,
                    "month2": price_change / 2,
                    "month3": price_change
                }
            }
    except Exception as e:
        raise ValueError(f"Error getting AI prediction: {str(e)}") 