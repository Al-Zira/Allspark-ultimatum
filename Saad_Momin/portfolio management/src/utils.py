import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Any
from binance.client import Client

def calculate_technical_indicators(prices: pd.Series) -> Dict[str, float]:
    """Calculate various technical indicators"""
    if len(prices) < 14:
        return {
            'rsi': 50,
            'sma_50': prices.iloc[-1] if len(prices) > 0 else 0,
            'sma_20': prices.iloc[-1] if len(prices) > 0 else 0,
            'ema_20': prices.iloc[-1] if len(prices) > 0 else 0,
            'macd': 0,
            'macd_signal': 0
        }
    
    # RSI
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Moving Averages
    sma_50 = prices.rolling(window=50).mean()
    sma_20 = prices.rolling(window=20).mean()
    ema_20 = prices.ewm(span=20, adjust=False).mean()
    
    # MACD
    ema_12 = prices.ewm(span=12, adjust=False).mean()
    ema_26 = prices.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    
    return {
        'rsi': rsi.iloc[-1],
        'sma_50': sma_50.iloc[-1],
        'sma_20': sma_20.iloc[-1],
        'ema_20': ema_20.iloc[-1],
        'macd': macd.iloc[-1],
        'macd_signal': macd_signal.iloc[-1]
    }

def get_asset_info(symbol: str, asset_type: str, binance_client: Client = None) -> Dict[str, Any]:
    """Get asset information from appropriate source"""
    if asset_type.lower() == 'crypto':
        return get_crypto_info(symbol, binance_client)
    return get_stock_info(symbol)

def get_crypto_info(symbol: str, binance_client: Client = None) -> Dict[str, Any]:
    """Get cryptocurrency information"""
    try:
        if binance_client:
            symbol_info = binance_client.get_symbol_info(f"{symbol}USDT")
            return {
                'name': symbol.upper(),
                'sector': 'Cryptocurrency',
                'exchange': 'Crypto',
                'metadata': symbol_info
            }
    except Exception:
        pass
    
    return {
        'name': symbol.upper(),
        'sector': 'Cryptocurrency',
        'exchange': 'Crypto'
    }

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get stock information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'Other'),
            'industry': info.get('industry'),
            'exchange': info.get('exchange'),
            'metadata': info
        }
    except Exception:
        return {
            'name': symbol,
            'sector': 'Other',
            'exchange': 'Unknown'
        }

def calculate_correlation(assets: Dict[str, Any]) -> float:
    """Calculate average correlation between assets"""
    if len(assets) < 2:
        return 0
    
    # Get historical prices for all assets
    prices = {}
    for asset in assets.values():
        ticker = yf.Ticker(asset['symbol'])
        hist = ticker.history(period="1mo")['Close']
        if not hist.empty:
            prices[asset['symbol']] = hist
    
    if len(prices) < 2:
        return 0
    
    # Calculate correlation matrix
    df = pd.DataFrame(prices)
    corr_matrix = df.corr()
    
    # Calculate average correlation (excluding self-correlation)
    n = len(corr_matrix)
    total_corr = (corr_matrix.sum().sum() - n) / (n * n - n)
    return total_corr
