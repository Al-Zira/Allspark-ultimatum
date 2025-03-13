import numpy as np
import pandas as pd
from typing import List, Dict, Any
import yfinance as yf
from scipy.optimize import minimize
from src.utils import calculate_technical_indicators, calculate_correlation
import ta
from datetime import datetime, timedelta
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from sklearn.preprocessing import StandardScaler
from src.database import Database
from src.ai_advisor import AIInvestmentAdvisor

class FinancialAnalyzer:
    def __init__(self):
        """Initialize the financial analyzer"""
        self.db = Database()
        self.ai_advisor = AIInvestmentAdvisor()
        self.market_cache = {}
        self.sentiment_cache = {}
        self.data_cache = {}  # New general-purpose cache
        self.cache_duration = 900  # 15 minutes
        self.risk_free_rate = 0.02  # Default annual risk-free rate

    def _ensure_timezone_naive(self, series: pd.Series) -> pd.Series:
        """Ensure the series is timezone naive"""
        if isinstance(series.index, pd.DatetimeIndex) and series.index.tz is not None:
            series.index = series.index.tz_localize(None)
        return series

    def _get_cached_data(self, key: str, fetch_func, period: str = "1y") -> Any:
        """Get data from cache or fetch and cache it"""
        cache_key = f"{key}_{period}"
        if cache_key in self.data_cache:
            timestamp, data = self.data_cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_duration:
                return data

        data = fetch_func()
        self.data_cache[cache_key] = (datetime.now(), data)
        return data

    def _fetch_ticker_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch ticker data with caching"""
        def fetch():
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period)
        
        return self._get_cached_data(f"ticker_{symbol}", fetch, period)

    def _get_market_data(self, period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Get market and index data with caching"""
        def fetch():
            indices = {
                "SPY": "market",
                "^VIX": "volatility",
                "^GSPC": "sp500",
                "^DJI": "dow",
                "^IXIC": "nasdaq"
            }
            data = {}
            for symbol, name in indices.items():
                try:
                    hist = self._fetch_ticker_data(symbol, period)
                    if not hist.empty:
                        data[name] = hist
                except:
                    continue
            return data
        
        return self._get_cached_data("market_data", fetch, period)

    def _calculate_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        if returns.empty:
            return {
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "var_95": 0.0,
                "var_99": 0.0,
                "max_drawdown": 0.0
            }

        # Annualized volatility
        volatility = returns.std() * np.sqrt(252)

        # Sharpe and Sortino ratios
        excess_returns = returns - (self.risk_free_rate / 252)
        sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std()) if excess_returns.std() != 0 else 0
        
        downside_returns = excess_returns[excess_returns < 0]
        sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std() if len(downside_returns) > 0 and downside_returns.std() != 0 else 0

        # Value at Risk
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)

        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = cumulative / rolling_max - 1
        max_drawdown = drawdowns.min()

        return {
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe),
            "sortino_ratio": float(sortino),
            "var_95": float(var_95),
            "var_99": float(var_99),
            "max_drawdown": float(max_drawdown)
        }

    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate daily returns"""
        if prices.empty:
            return pd.Series()
        prices = self._ensure_timezone_naive(prices)
        return prices.pct_change().dropna()

    def calculate_beta(self, returns: pd.Series, market_returns: pd.Series = None) -> float:
        """Calculate beta coefficient"""
        if returns.empty:
            return 0.0

        if market_returns is None:
            market_returns = self._get_market_returns()

        returns = self._ensure_timezone_naive(returns)
        market_returns = self._ensure_timezone_naive(market_returns)
        
        # Align dates
        aligned_data = pd.concat([returns, market_returns], axis=1).dropna()
        if aligned_data.empty or aligned_data.shape[1] != 2:
            return 0.0

        covariance = aligned_data.cov().iloc[0, 1]
        market_variance = aligned_data.iloc[:, 1].var()
        
        return covariance / market_variance if market_variance != 0 else 0.0

    def calculate_alpha(self, returns: pd.Series, market_returns: pd.Series = None, beta: float = None) -> float:
        """Calculate Jensen's Alpha"""
        if returns.empty:
            return 0.0

        if market_returns is None:
            market_returns = self._get_market_returns()
        
        if beta is None:
            beta = self.calculate_beta(returns, market_returns)

        returns = self._ensure_timezone_naive(returns)
        market_returns = self._ensure_timezone_naive(market_returns)
        
        # Align dates
        aligned_data = pd.concat([returns, market_returns], axis=1).dropna()
        if aligned_data.empty or aligned_data.shape[1] != 2:
            return 0.0

        portfolio_return = aligned_data.iloc[:, 0].mean()
        market_return = aligned_data.iloc[:, 1].mean()
        daily_rf_rate = self.risk_free_rate / 252

        return (portfolio_return - daily_rf_rate) - beta * (market_return - daily_rf_rate)

    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe Ratio"""
        if returns.empty:
            return 0.0

        returns = self._ensure_timezone_naive(returns)
        excess_returns = returns - (self.risk_free_rate / 252)
        
        if excess_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())

    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino Ratio"""
        if returns.empty:
            return 0.0

        returns = self._ensure_timezone_naive(returns)
        excess_returns = returns - self.risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        
        return np.sqrt(252) * np.mean(excess_returns) / downside_std if downside_std != 0 else 0.0

    @staticmethod
    def calculate_technical_indicators(prices: pd.Series) -> Dict[str, float]:
        """Calculate various technical indicators"""
        return calculate_technical_indicators(prices)
    
    @staticmethod
    def calculate_correlation_matrix(assets: Dict[str, pd.Series]) -> pd.DataFrame:
        """Calculate correlation matrix between assets"""
        return calculate_correlation(assets)
    
    @staticmethod
    def optimize_portfolio(returns: pd.DataFrame, 
                         target_return: float = None,
                         risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Optimize portfolio weights using Modern Portfolio Theory"""
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        def portfolio_return(weights):
            return np.sum(returns.mean() * weights) * 252
        
        num_assets = len(returns.columns)
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
        ]
        
        if target_return is not None:
            constraints.append(
                {'type': 'eq', 'fun': lambda x: portfolio_return(x) - target_return}
            )
        
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Minimize volatility
        result = minimize(portfolio_volatility,
                        num_assets * [1./num_assets],
                        method='SLSQP',
                        bounds=bounds,
                        constraints=constraints)
        
        optimal_weights = result.x
        opt_volatility = portfolio_volatility(optimal_weights)
        opt_return = portfolio_return(optimal_weights)
        sharpe = (opt_return - risk_free_rate) / opt_volatility
        
        return {
            'weights': dict(zip(returns.columns, optimal_weights)),
            'expected_return': opt_return,
            'volatility': opt_volatility,
            'sharpe_ratio': sharpe
        }
    
    @staticmethod
    def calculate_drawdown(returns: pd.Series) -> Dict[str, float]:
        """Calculate maximum drawdown and current drawdown"""
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = cumulative / rolling_max - 1
        
        return {
            'max_drawdown': drawdowns.min(),
            'current_drawdown': drawdowns.iloc[-1]
        }
    
    @staticmethod
    def risk_assessment(portfolio_returns: List[float], 
                       market_returns: List[float] = None) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        if not portfolio_returns:
            return {
                'volatility': 0,
                'max_drawdown': 0,
                'value_at_risk': 0,
                'beta': 0,
                'alpha': 0,
                'sharpe_ratio': 0
            }
        
        returns_series = pd.Series(portfolio_returns)
        
        risk_metrics = {
            'volatility': np.std(portfolio_returns) * np.sqrt(252) * 100,
            'max_drawdown': FinancialAnalyzer.calculate_drawdown(returns_series)['max_drawdown'] * 100,
            'value_at_risk': np.percentile(portfolio_returns, 5) * 100,
            'sharpe_ratio': FinancialAnalyzer.calculate_sharpe_ratio(portfolio_returns)
        }
        
        if market_returns:
            risk_metrics.update({
                'beta': FinancialAnalyzer.calculate_beta(portfolio_returns, market_returns),
                'alpha': FinancialAnalyzer.calculate_alpha(portfolio_returns, market_returns)
            })
        
        return risk_metrics
    
    def calculate_risk_metrics(self, assets: Dict) -> Dict:
        """Calculate risk metrics for the portfolio"""
        if not assets:
            return {
                "volatility": 0,
                "beta": 0,
                "alpha": 0,
                "sharpe_ratio": 0,
                "var_95": 0
            }
        
        # Calculate portfolio returns
        portfolio_values = self._get_portfolio_history(assets)
        returns = portfolio_values.pct_change().dropna()
        
        # Calculate metrics
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        beta = self._calculate_beta(returns)
        alpha = self._calculate_alpha(returns, beta)
        sharpe = self._calculate_sharpe_ratio(returns)
        var_95 = self._calculate_var(returns, 0.95)
        
        return {
            "volatility": float(volatility),
            "beta": float(beta),
            "alpha": float(alpha),
            "sharpe_ratio": float(sharpe),
            "var_95": float(var_95)
        }
    
    def get_technical_indicators(self, symbol: str) -> Dict:
        """Get technical indicators for a symbol"""
        # Get historical data
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="6mo")
        
        if history.empty:
            return {}
        
        # Calculate indicators
        close = history['Close']
        high = history['High']
        low = history['Low']
        volume = history['Volume']
        
        indicators = {}
        
        # Moving averages
        indicators['sma_20'] = ta.trend.sma_indicator(close, window=20).iloc[-1]
        indicators['sma_50'] = ta.trend.sma_indicator(close, window=50).iloc[-1]
        indicators['sma_200'] = ta.trend.sma_indicator(close, window=200).iloc[-1]
        
        # RSI
        indicators['rsi'] = ta.momentum.rsi(close, window=14).iloc[-1]
        
        # MACD
        macd = ta.trend.macd(close)
        indicators['macd'] = macd.iloc[-1]
        indicators['macd_signal'] = ta.trend.macd_signal(close).iloc[-1]
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close)
        indicators['bb_upper'] = bb.bollinger_hband().iloc[-1]
        indicators['bb_lower'] = bb.bollinger_lband().iloc[-1]
        
        # Volume indicators
        indicators['obv'] = ta.volume.on_balance_volume(close, volume).iloc[-1]
        
        return {k: float(v) for k, v in indicators.items() if not pd.isna(v)}
    
    def analyze_diversification(self, assets: Dict) -> Dict:
        """Analyze portfolio diversification"""
        if not assets:
            return {
                "diversification_score": 0,
                "sector_concentration": {},
                "asset_type_concentration": {},
                "recommendations": []
            }
        
        # Calculate concentrations
        total_value = sum(asset['current_value'] for asset in assets.values())
        
        sector_concentration = {}
        asset_type_concentration = {}
        
        for asset in assets.values():
            # Sector concentration
            sector = asset.get('sector', 'Unknown')
            sector_concentration[sector] = sector_concentration.get(sector, 0) + asset['current_value']
            
            # Asset type concentration
            asset_type = asset.get('type', 'Unknown')
            asset_type_concentration[asset_type] = asset_type_concentration.get(asset_type, 0) + asset['current_value']
        
        # Convert to percentages
        sector_concentration = {k: v/total_value*100 for k, v in sector_concentration.items()}
        asset_type_concentration = {k: v/total_value*100 for k, v in asset_type_concentration.items()}
        
        # Calculate diversification score (0-100)
        num_sectors = len(sector_concentration)
        num_asset_types = len(asset_type_concentration)
        max_concentration = max(sector_concentration.values())
        
        diversification_score = (
            (num_sectors * 20) +  # More sectors = better
            (num_asset_types * 20) +  # More asset types = better
            (100 - max_concentration)  # Lower maximum concentration = better
        ) / 3
        
        # Generate recommendations
        recommendations = []
        if max_concentration > 40:
            recommendations.append("Consider reducing exposure to dominant sector")
        if num_sectors < 5:
            recommendations.append("Consider investing in more sectors")
        if num_asset_types < 3:
            recommendations.append("Consider diversifying across more asset types")
        
        return {
            "diversification_score": min(100, diversification_score),
            "sector_concentration": sector_concentration,
            "asset_type_concentration": asset_type_concentration,
            "recommendations": recommendations
        }
    
    def get_historical_performance(self, assets: Dict, start_date: datetime, end_date: datetime) -> Dict:
        """Get historical performance data"""
        # Get portfolio values over time
        portfolio_values = self._get_portfolio_history(assets, start_date, end_date)
        
        # Calculate metrics
        returns = portfolio_values.pct_change().dropna()
        cumulative_returns = (1 + returns).cumprod() - 1
        
        return {
            "portfolio_values": portfolio_values.to_dict(),
            "returns": returns.to_dict(),
            "cumulative_returns": cumulative_returns.to_dict(),
            "total_return": float(cumulative_returns.iloc[-1] if not cumulative_returns.empty else 0),
            "volatility": float(returns.std() * np.sqrt(252)) if not returns.empty else 0
        }
    
    def compare_assets(self, symbols: List[str]) -> Dict:
        """Compare multiple assets"""
        try:
            results = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                info = ticker.info
                
                if not hist.empty:
                    returns = hist["Close"].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252)
                    sharpe = returns.mean() / returns.std() * np.sqrt(252)
                    
                    results[symbol] = {
                        "name": info.get("longName", symbol),
                        "sector": info.get("sector", "Unknown"),
                        "market_cap": info.get("marketCap", 0),
                        "pe_ratio": info.get("trailingPE", 0),
                        "dividend_yield": info.get("dividendYield", 0),
                        "performance": {
                            "ytd_return": (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1),
                            "volatility": volatility,
                            "sharpe_ratio": sharpe
                        }
                    }
            
            return results
        except Exception as e:
            return {"error": f"Error comparing assets: {str(e)}"}
    
    def _get_portfolio_history(self, assets: Dict, start_date: datetime = None, end_date: datetime = None) -> pd.Series:
        """Get historical portfolio values"""
        if not assets:
            return pd.Series()
        
        # Default to last 6 months if no dates provided
        if not start_date:
            start_date = datetime.now() - timedelta(days=180)
        if not end_date:
            end_date = datetime.now()
        
        # Get historical data for each asset
        asset_histories = {}
        for asset_id, asset in assets.items():
            ticker = yf.Ticker(asset['symbol'])
            history = ticker.history(start=start_date, end=end_date)
            if not history.empty:
                asset_histories[asset_id] = history['Close'] * asset['quantity']
        
        # Combine all histories
        if asset_histories:
            portfolio_values = pd.concat(asset_histories.values(), axis=1).sum(axis=1)
            return portfolio_values
        return pd.Series()
    
    def get_portfolio_metrics(self, assets: Dict) -> Dict:
        """Get portfolio performance metrics"""
        if not assets:
            return {
                "total_return": 0,
                "daily_returns": [],
                "volatility": 0,
                "sharpe_ratio": 0,
                "beta": 0,
                "alpha": 0
            }
        
        # Get historical data
        portfolio_values = self._get_portfolio_history(assets)
        if portfolio_values.empty:
            return {
                "total_return": 0,
                "daily_returns": [],
                "volatility": 0,
                "sharpe_ratio": 0,
                "beta": 0,
                "alpha": 0
            }
        
        # Calculate metrics
        returns = portfolio_values.pct_change().dropna()
        total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        
        # Get market data for comparison
        spy = yf.Ticker("SPY")
        market_hist = spy.history(period="1y")
        market_returns = market_hist['Close'].pct_change().dropna()
        
        # Calculate beta and alpha
        beta = self._calculate_beta(returns, market_returns)
        alpha = self._calculate_alpha(returns, beta, market_returns)
        
        # Calculate Sharpe ratio
        risk_free_rate = 0.02  # Assuming 2% risk-free rate
        excess_returns = returns.mean() * 252 - risk_free_rate
        sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
        
        return {
            "total_return": float(total_return),
            "daily_returns": returns.tolist(),
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "beta": float(beta),
            "alpha": float(alpha)
        }
    
    def _calculate_beta(self, returns: pd.Series, market_returns: pd.Series = None) -> float:
        """Calculate portfolio beta"""
        if market_returns is None:
            spy = yf.Ticker("SPY")
            market_hist = spy.history(period="1y")
            market_returns = market_hist['Close'].pct_change().dropna()
        
        # Align dates
        aligned_data = pd.concat([returns, market_returns], axis=1).dropna()
        if aligned_data.empty or aligned_data.shape[1] != 2:
            return 0
        
        covariance = aligned_data.cov().iloc[0, 1]
        market_variance = aligned_data.iloc[:, 1].var()
        
        return covariance / market_variance if market_variance > 0 else 0
    
    def _calculate_alpha(self, returns: pd.Series, beta: float, market_returns: pd.Series = None) -> float:
        """Calculate portfolio alpha"""
        if market_returns is None:
            spy = yf.Ticker("SPY")
            market_hist = spy.history(period="1y")
            market_returns = market_hist['Close'].pct_change().dropna()
        
        # Align dates
        aligned_data = pd.concat([returns, market_returns], axis=1).dropna()
        if aligned_data.empty or aligned_data.shape[1] != 2:
            return 0
        
        risk_free_rate = 0.02 / 252  # Daily risk-free rate (assuming 2% annual)
        portfolio_return = aligned_data.iloc[:, 0].mean()
        market_return = aligned_data.iloc[:, 1].mean()
        
        return (portfolio_return - risk_free_rate) - beta * (market_return - risk_free_rate)
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio for the portfolio"""
        if returns.empty:
            return 0
        
        # Get risk-free rate from config
        risk_free_rate = self.config.DEFAULT_RISK_FREE_RATE
        
        # Calculate excess returns
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        # Calculate Sharpe ratio
        if excess_returns.std() == 0:
            return 0
        
        sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
        return float(sharpe)
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk (VaR) for the portfolio"""
        if returns.empty:
            return 0
        
        sorted_returns = returns.sort_values()
        index = int(len(sorted_returns) * (1 - confidence_level))
        var = -sorted_returns.iloc[index]
        return float(var)

    def analyze_sentiment(self, symbol: str, asset_type: str = "stock") -> Dict:
        """Analyze sentiment for an asset"""
        try:
            # Fetch latest news and social media data
            news_data = self._fetch_news_data(symbol)
            social_data = self._fetch_social_data(symbol)
            
            # Analyze sentiment
            sentiment_data = {
                "overall_sentiment": self._calculate_overall_sentiment(news_data, social_data),
                "news_sentiment": self._analyze_news_sentiment(news_data),
                "social_sentiment": self._analyze_social_sentiment(social_data),
                "sentiment_trends": self._analyze_sentiment_trends(symbol),
                "market_impact": self._analyze_market_impact(symbol),
                "timestamp": datetime.now().isoformat()
            }
            
            return sentiment_data
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                "error": "Failed to analyze sentiment",
                "details": str(e)
            }

    def get_market_conditions(self) -> Dict:
        """Get current market conditions and indicators"""
        try:
            # Get market data
            spy = yf.Ticker("SPY")
            vix = yf.Ticker("^VIX")
            
            spy_hist = spy.history(period="1mo")
            vix_hist = vix.history(period="1mo")
            
            if spy_hist.empty or vix_hist.empty:
                return {
                    "market_sentiment": "neutral",
                    "volatility_index": 0,
                    "sector_performance": {},
                    "market_indicators": {},
                    "trading_signals": {}
                }
            
            # Calculate market indicators
            spy_close = spy_hist['Close']
            sma_20 = ta.trend.sma_indicator(spy_close, window=20).iloc[-1]
            rsi = ta.momentum.rsi(spy_close).iloc[-1]
            macd = ta.trend.macd_diff(spy_close).iloc[-1]
            
            market_indicators = {
                "spy_sma_20": float(sma_20) if not pd.isna(sma_20) and not np.isinf(sma_20) else 0,
                "spy_rsi": float(rsi) if not pd.isna(rsi) and not np.isinf(rsi) else 50,
                "spy_macd": float(macd) if not pd.isna(macd) and not np.isinf(macd) else 0
            }
            
            # Get sector performance
            sectors = ["XLF", "XLK", "XLV", "XLE", "XLI", "XLP", "XLY", "XLB", "XLU", "XLRE"]
            sector_performance = {}
            
            for sector in sectors:
                try:
                    ticker = yf.Ticker(sector)
                    hist = ticker.history(period="1mo")
                    if not hist.empty:
                        perf = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                        if not pd.isna(perf) and not np.isinf(perf):
                            sector_performance[sector] = float(perf)
                except:
                    continue
            
            # Determine market sentiment
            rsi = market_indicators["spy_rsi"]
            if rsi > 70:
                sentiment = "overbought"
            elif rsi < 30:
                sentiment = "oversold"
            else:
                sentiment = "neutral"
            
            vix_value = float(vix_hist['Close'].iloc[-1]) if not vix_hist.empty else 0
            if pd.isna(vix_value) or np.isinf(vix_value):
                vix_value = 0

            return {
                "market_sentiment": sentiment,
                "volatility_index": vix_value,
                "sector_performance": sector_performance,
                "market_indicators": market_indicators,
                "trading_signals": self._generate_trading_signals(spy_hist)
            }
            
        except Exception as e:
            return {
                "market_sentiment": "neutral",
                "volatility_index": 0,
                "sector_performance": {},
                "market_indicators": {},
                "trading_signals": {},
                "error": str(e)
            }

    def analyze_portfolio_risk(self, assets: Dict) -> Dict:
        """Analyze portfolio risk metrics"""
        if not assets:
            return {
                "risk_metrics": {
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "var_95": 0.0,
                    "var_99": 0.0
                },
                "risk_decomposition": {},
                "stress_test_results": {
                    "market_crash": 0.0,
                    "recession": 0.0,
                    "tech_bubble": 0.0,
                    "financial_crisis": 0.0
                },
                "var_analysis": {
                    "var_95": 0.0,
                    "var_99": 0.0,
                    "expected_shortfall": 0.0
                },
                "correlation_matrix": {}
            }

        # Get portfolio returns
        portfolio_values = self._get_portfolio_history(assets)
        returns = portfolio_values.pct_change().dropna()

        # Calculate risk metrics
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        var_95 = self._calculate_var(returns, 0.95)
        var_99 = self._calculate_var(returns, 0.99)

        # Calculate correlation matrix
        symbols = [asset["symbol"] for asset in assets.values()]
        correlation_matrix = {}
        histories = {}
        
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if not hist.empty:
                histories[symbol] = hist["Close"].pct_change().dropna()

        if histories:
            returns_df = pd.DataFrame(histories)
            correlation_matrix = returns_df.corr().to_dict()

        # Calculate risk decomposition
        total_value = sum(asset["current_value"] for asset in assets.values())
        risk_decomposition = {
            symbol: (asset["current_value"] / total_value) * volatility 
            for symbol, asset in zip(symbols, assets.values())
        }

        return {
            "risk_metrics": {
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "var_95": float(var_95),
                "var_99": float(var_99)
            },
            "risk_decomposition": risk_decomposition,
            "stress_test_results": {
                "market_crash": total_value * 0.7,  # 30% drop
                "recession": total_value * 0.8,     # 20% drop
                "tech_bubble": total_value * 0.85,  # 15% drop
                "financial_crisis": total_value * 0.75  # 25% drop
            },
            "var_analysis": {
                "var_95": float(var_95),
                "var_99": float(var_99),
                "expected_shortfall": float(-returns[returns < -var_95].mean()) if len(returns[returns < -var_95]) > 0 else 0.0
            },
            "correlation_matrix": correlation_matrix
        }

    def optimize_portfolio(self, assets: Dict, target_return: float = None) -> Dict:
        """Optimize portfolio allocation using Modern Portfolio Theory"""
        if not assets:
            return {
                "optimal_weights": {},
                "expected_return": 0,
                "expected_risk": 0,
                "optimization_metrics": {
                    "sharpe_ratio": 0,
                    "diversification_score": 0
                },
                "rebalancing_suggestions": []
            }

        # Get historical data and calculate returns
        histories = {}
        returns = {}
        for asset_id, asset in assets.items():
            symbol = asset['symbol']
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if not hist.empty:
                histories[symbol] = hist
                returns[symbol] = hist['Close'].pct_change().dropna()

        if not returns:
            return {
                "optimal_weights": {asset['symbol']: 1.0/len(assets) for asset in assets.values()},
                "expected_return": 0,
                "expected_risk": 0,
                "optimization_metrics": {"sharpe_ratio": 0, "diversification_score": 0},
                "rebalancing_suggestions": []
            }

        # Create returns DataFrame and calculate parameters
        returns_df = pd.DataFrame(returns)
        mu = returns_df.mean() * 252
        S = returns_df.cov() * 252

        # Define optimization functions
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(S, weights)))

        def portfolio_return(weights):
            return np.sum(mu * weights)

        def objective(weights):
            port_ret = portfolio_return(weights)
            port_vol = portfolio_volatility(weights)
            return -port_ret/port_vol if port_vol > 0 else 0

        # Setup optimization constraints
        n_assets = len(returns_df.columns)
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        if target_return is not None:
            constraints.append(
                {'type': 'eq', 'fun': lambda x: portfolio_return(x) - target_return}
            )
        bounds = tuple((0, 1) for _ in range(n_assets))

        # Current portfolio weights
        current_total = sum(asset['current_value'] for asset in assets.values())
        current_weights = {symbol: asset['current_value']/current_total 
                         for symbol, asset in zip(returns_df.columns, assets.values())}

        # Optimize portfolio
        result = minimize(objective,
                        x0=np.array([1./n_assets for _ in range(n_assets)]),
                        method='SLSQP',
                        bounds=bounds,
                        constraints=constraints)

        if not result.success:
            return {
                "optimal_weights": current_weights,
                "expected_return": float(portfolio_return(np.array(list(current_weights.values())))),
                "expected_risk": float(portfolio_volatility(np.array(list(current_weights.values())))),
                "optimization_metrics": {"sharpe_ratio": 0, "diversification_score": 0},
                "rebalancing_suggestions": []
            }

        # Calculate metrics for optimized portfolio
        opt_weights = result.x
        opt_ret = portfolio_return(opt_weights)
        opt_vol = portfolio_volatility(opt_weights)

        # Generate rebalancing suggestions
        rebalancing = []
        for i, symbol in enumerate(returns_df.columns):
            current = current_weights.get(symbol, 0)
            optimal = opt_weights[i]
            if abs(current - optimal) > 0.05:  # 5% threshold
                action = "increase" if optimal > current else "decrease"
                rebalancing.append({
                    "symbol": symbol,
                    "current_weight": float(current),
                    "optimal_weight": float(optimal),
                    "action": action,
                    "change_needed": float(abs(optimal - current))
                })

        return {
            "optimal_weights": {symbol: float(weight) 
                              for symbol, weight in zip(returns_df.columns, opt_weights)},
            "expected_return": float(opt_ret),
            "expected_risk": float(opt_vol),
            "optimization_metrics": {
                "sharpe_ratio": float(opt_ret/opt_vol) if opt_vol > 0 else 0,
                "diversification_score": float(1 - np.sqrt(np.dot(opt_weights, opt_weights)))
            },
            "rebalancing_suggestions": sorted(rebalancing, 
                                            key=lambda x: abs(x['change_needed']), 
                                            reverse=True)
        }

    def analyze_sectors(self, assets: Dict) -> Dict:
        """Perform detailed sector analysis"""
        try:
            # Get sector data for assets
            sector_allocation = {}
            sector_values = {}
            
            for asset_id, asset in assets.items():
                if asset['asset_type'].lower() == 'stock':
                    ticker = yf.Ticker(asset['symbol'])
                    info = ticker.info
                    sector = info.get('sector', 'Other')
                    
                    if sector not in sector_allocation:
                        sector_allocation[sector] = 0
                        sector_values[sector] = 0
                    
                    sector_allocation[sector] += 1
                    sector_values[sector] += asset['current_value']
            
            total_value = sum(sector_values.values())
            sector_allocation = {k: v/len(assets) for k, v in sector_allocation.items()}
            sector_values = {k: v/total_value for k, v in sector_values.items()}
            
            # Get sector performance
            sector_etfs = {
                "Technology": "XLK",
                "Financial": "XLF",
                "Healthcare": "XLV",
                "Energy": "XLE",
                "Industrial": "XLI",
                "Consumer Staples": "XLP",
                "Consumer Discretionary": "XLY",
                "Materials": "XLB",
                "Utilities": "XLU",
                "Real Estate": "XLRE"
            }
            
            sector_performance = {}
            sector_risk = {}
            
            for sector, etf in sector_etfs.items():
                try:
                    ticker = yf.Ticker(etf)
                    hist = ticker.history(period="1y")
                    if not hist.empty:
                        returns = hist['Close'].pct_change().dropna()
                        perf = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                        vol = returns.std() * np.sqrt(252) * 100
                        
                        sector_performance[sector] = float(perf)
                        sector_risk[sector] = float(vol)
                except:
                    continue
            
            # Generate sector recommendations
            recommendations = []
            for sector in sector_allocation:
                if sector in sector_performance:
                    perf = sector_performance[sector]
                    risk = sector_risk[sector]
                    alloc = sector_values.get(sector, 0) * 100
                    
                    if perf > 10 and alloc < 15:
                        recommendations.append(f"Consider increasing allocation to {sector} sector")
                    elif perf < -10 and alloc > 15:
                        recommendations.append(f"Consider reducing exposure to {sector} sector")
            
            return {
                "sector_allocation": sector_values,
                "sector_performance": sector_performance,
                "sector_risk": sector_risk,
                "sector_correlation": self._calculate_sector_correlation(sector_etfs),
                "sector_recommendations": recommendations
            }
            
        except Exception as e:
            return {
                "sector_allocation": {},
                "sector_performance": {},
                "sector_risk": {},
                "sector_correlation": {},
                "sector_recommendations": [],
                "error": str(e)
            }

    def _generate_trading_signals(self, history: pd.DataFrame) -> Dict:
        """Generate trading signals based on technical indicators"""
        close = history['Close']
        
        # Calculate indicators
        sma_20 = ta.trend.sma_indicator(close, window=20)
        sma_50 = ta.trend.sma_indicator(close, window=50)
        rsi = ta.momentum.rsi(close)
        macd = ta.trend.macd_diff(close)
        
        # Generate signals
        signals = {
            "trend": "bullish" if sma_20.iloc[-1] > sma_50.iloc[-1] else "bearish",
            "rsi_signal": "oversold" if rsi.iloc[-1] < 30 else "overbought" if rsi.iloc[-1] > 70 else "neutral",
            "macd_signal": "buy" if macd.iloc[-1] > 0 else "sell"
        }
        
        return signals

    def _calculate_risk_contribution(self, returns: pd.DataFrame, assets: Dict) -> Dict:
        """Calculate risk contribution of each asset"""
        try:
            weights = []
            symbols = []
            total_value = sum(asset.get('current_value', 0) for asset in assets.values())
            
            if total_value == 0:
                return {}
            
            for symbol in returns.columns:
                asset_value = next((asset.get('current_value', 0) for asset in assets.values() 
                                if asset.get('symbol') == symbol), 0)
                weights.append(asset_value / total_value)
                symbols.append(symbol)
            
            weights = np.array(weights)
            cov = returns.cov().values
            port_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            
            if port_vol == 0:
                return {symbol: 0.0 for symbol in symbols}
            
            # Component risk contributions
            contrib = np.multiply(weights, np.dot(cov, weights)) / port_vol
            
            # Ensure all values are finite
            contrib = np.nan_to_num(contrib, 0)
            
            return {symbol: float(risk) for symbol, risk in zip(symbols, contrib)}
        except Exception:
            return {}

    def _calculate_sector_correlation(self, sector_etfs: Dict) -> Dict:
        """Calculate correlation between sectors"""
        histories = {}
        
        for sector, etf in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                hist = ticker.history(period="1y")
                if not hist.empty:
                    histories[sector] = hist['Close'].pct_change().dropna()
            except:
                continue
        
        if histories:
            correlation = pd.DataFrame(histories).corr()
            return correlation.to_dict()
        return {}

    def get_recommendations(self) -> Dict:
        """Get investment recommendations based on portfolio and market analysis"""
        try:
            # Get market conditions
            market_conditions = self.get_market_conditions()
            
            # Generate portfolio recommendations
            portfolio_recommendations = []
            market_opportunities = []
            risk_alerts = []
            
            # Market sentiment based recommendations
            sentiment = market_conditions.get('market_sentiment', 'neutral')
            vix = market_conditions.get('volatility_index', 0)
            
            if sentiment == 'bullish':
                portfolio_recommendations.append("Consider increasing equity exposure")
                market_opportunities.append({
                    "sector": "Growth Stocks",
                    "reason": "Strong market momentum"
                })
            elif sentiment == 'bearish':
                portfolio_recommendations.append("Consider defensive positions")
                risk_alerts.append({
                    "type": "Market Risk",
                    "message": "Bearish market conditions detected"
                })
            
            # VIX based recommendations
            if vix > 20:
                risk_alerts.append({
                    "type": "Volatility Risk",
                    "message": f"High market volatility (VIX: {vix})"
                })
                portfolio_recommendations.append("Consider hedging strategies")
            
            # Sector performance based recommendations
            sector_performance = market_conditions.get('sector_performance', {})
            for sector, performance in sector_performance.items():
                if performance > 2.0:
                    market_opportunities.append({
                        "sector": sector,
                        "reason": f"Strong sector performance ({performance:.1f}%)"
                    })
                elif performance < -2.0:
                    risk_alerts.append({
                        "type": "Sector Risk",
                        "message": f"Weak performance in {sector} sector ({performance:.1f}%)"
                    })
            
            return {
                "portfolio_recommendations": portfolio_recommendations,
                "market_opportunities": market_opportunities,
                "risk_alerts": risk_alerts
            }
            
        except Exception as e:
            return {
                "portfolio_recommendations": [],
                "market_opportunities": [],
                "risk_alerts": [{"type": "Error", "message": str(e)}]
            }

    def get_performance_metrics(self, assets: Dict) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            if not assets:
                return {
                    "total_return": 0.0,
                    "daily_returns": [],
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "beta": 0.0,
                    "alpha": 0.0
                }
            
            total_value = sum(asset["current_value"] for asset in assets.values())
            total_cost = sum(asset["purchase_price"] * asset["quantity"] for asset in assets.values())
            total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0
            
            # Mock daily returns for demonstration
            daily_returns = np.random.normal(0.001, 0.02, 30).tolist()
            volatility = np.std(daily_returns) * np.sqrt(252)
            sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
            
            return {
                "total_return": total_return,
                "daily_returns": daily_returns,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "beta": 1.1,  # Mock value
                "alpha": 0.02  # Mock value
            }
        except Exception as e:
            return {
                "error": f"Error calculating performance metrics: {str(e)}"
            }

    def get_portfolio_history(self, assets: Dict) -> Dict:
        """Get portfolio historical performance"""
        try:
            if not assets:
                return {
                    "dates": [],
                    "values": [],
                    "returns": []
                }
            
            # Generate 30 days of mock historical data
            dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
            dates.reverse()
            
            # Generate mock values with some randomness
            base_value = sum(asset["current_value"] for asset in assets.values())
            daily_returns = np.random.normal(0.001, 0.02, 30)
            values = [base_value]
            
            for ret in daily_returns[1:]:
                values.append(values[-1] * (1 + ret))
            
            return {
                "dates": dates,
                "values": values,
                "returns": daily_returns.tolist()
            }
        except Exception as e:
            return {
                "error": f"Error getting portfolio history: {str(e)}"
            }

    def backtest_portfolio(self, assets: Dict, start_date: str, end_date: str) -> Dict:
        """Backtest portfolio performance"""
        try:
            if not assets:
                return {
                    "performance": [],
                    "metrics": {
                        "total_return": 0.0,
                        "sharpe_ratio": 0.0,
                        "max_drawdown": 0.0
                    }
                }
            
            # Get historical data for each asset
            histories = {}
            for asset_id, asset in assets.items():
                ticker = yf.Ticker(asset["symbol"])
                hist = ticker.history(start=start_date, end=end_date)
                if not hist.empty:
                    histories[asset["symbol"]] = hist
            
            # Calculate portfolio performance
            portfolio_values = []
            dates = []
            
            # Use the first asset's dates as reference
            reference_dates = list(histories.values())[0].index
            
            for date in reference_dates:
                total_value = 0
                for symbol, hist in histories.items():
                    if date in hist.index:
                        asset_value = hist.loc[date, "Close"] * assets[symbol]["quantity"]
                        total_value += asset_value
                portfolio_values.append(total_value)
                dates.append(date.strftime("%Y-%m-%d"))
            
            # Calculate metrics
            returns = pd.Series(portfolio_values).pct_change().dropna()
            total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
            
            # Calculate maximum drawdown
            peak = portfolio_values[0]
            max_drawdown = 0
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            return {
                "performance": [
                    {"date": date, "value": value} 
                    for date, value in zip(dates, portfolio_values)
                ],
                "metrics": {
                    "total_return": total_return,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown
                }
            }
        except Exception as e:
            return {"error": f"Error backtesting portfolio: {str(e)}"}

    def get_rebalancing_suggestions(self, assets: Dict) -> Dict:
        """Get portfolio rebalancing suggestions"""
        try:
            if not assets:
                return {
                    "suggestions": [],
                    "current_allocation": {},
                    "target_allocation": {}
                }
            
            # Calculate current allocation
            total_value = sum(asset["current_value"] for asset in assets.values())
            current_allocation = {
                asset["symbol"]: asset["current_value"] / total_value 
                for asset in assets.values()
            }
            
            # Define target allocation (simplified example)
            target_allocation = {symbol: 1.0/len(assets) for symbol in current_allocation}
            
            # Generate rebalancing suggestions
            suggestions = []
            for symbol in current_allocation:
                diff = target_allocation[symbol] - current_allocation[symbol]
                if abs(diff) > 0.05:  # 5% threshold
                    action = "increase" if diff > 0 else "decrease"
                    suggestions.append({
                        "symbol": symbol,
                        "action": action,
                        "amount": abs(diff) * total_value,
                        "percentage": abs(diff) * 100
                    })
            
            return {
                "suggestions": suggestions,
                "current_allocation": current_allocation,
                "target_allocation": target_allocation
            }
        except Exception as e:
            return {"error": f"Error generating rebalancing suggestions: {str(e)}"}

    def analyze_performance_attribution(self, assets: Dict) -> Dict:
        """Analyze portfolio performance attribution"""
        if not assets:
            return {
                "attribution": {},
                "sector_contribution": {},
                "asset_contribution": {}
            }

        # Calculate total portfolio metrics
        total_value = sum(asset["current_value"] for asset in assets.values())
        total_cost = sum(asset["purchase_price"] * asset["quantity"] for asset in assets.values())
        total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0

        # Calculate attribution by asset
        asset_contribution = {}
        sector_contribution = {}

        for asset in assets.values():
            # Asset level attribution
            asset_cost = asset["purchase_price"] * asset["quantity"]
            asset_return = (asset["current_value"] - asset_cost) / asset_cost if asset_cost > 0 else 0
            weight = asset_cost / total_cost if total_cost > 0 else 0
            contribution = asset_return * weight

            asset_contribution[asset["symbol"]] = {
                "return": float(asset_return),
                "weight": float(weight),
                "contribution": float(contribution)
            }

            # Sector level attribution
            sector = asset.get("sector", "Unknown")
            if sector not in sector_contribution:
                sector_contribution[sector] = {
                    "return": 0.0,
                    "weight": 0.0,
                    "contribution": 0.0
                }
            
            sector_contribution[sector]["return"] += asset_return * weight
            sector_contribution[sector]["weight"] += weight
            sector_contribution[sector]["contribution"] += contribution

        # Convert sector metrics to float
        for sector in sector_contribution:
            sector_contribution[sector] = {
                k: float(v) for k, v in sector_contribution[sector].items()
            }

        return {
            "total_return": float(total_return),
            "attribution": {
                "asset_selection": float(0.6 * total_return),  # Simplified attribution
                "sector_allocation": float(0.4 * total_return)
            },
            "sector_contribution": sector_contribution,
            "asset_contribution": asset_contribution
        }

    def analyze_correlations(self, assets: Dict) -> Dict:
        """Analyze portfolio correlations"""
        if not assets:
            return {
                "correlation_matrix": {},
                "average_correlation": 0.0,
                "diversification_score": 0.0,
                "interpretation": {
                    "score": "Low",
                    "suggestion": "Add assets to improve diversification"
                }
            }

        # Get historical data
        histories = {}
        for asset in assets.values():
            ticker = yf.Ticker(asset["symbol"])
            hist = ticker.history(period="1y")
            if not hist.empty:
                histories[asset["symbol"]] = hist["Close"].pct_change().dropna()

        if not histories:
            return {
                "correlation_matrix": {},
                "average_correlation": 0.0,
                "diversification_score": 0.0,
                "interpretation": {
                    "score": "Low",
                    "suggestion": "Unable to calculate correlations due to insufficient data"
                }
            }

        # Calculate correlation matrix
        returns_df = pd.DataFrame(histories)
        correlation_matrix = returns_df.corr().to_dict()

        # Calculate average correlation
        correlations = []
        for symbol1 in correlation_matrix:
            for symbol2 in correlation_matrix[symbol1]:
                if symbol1 != symbol2:
                    correlations.append(correlation_matrix[symbol1][symbol2])

        avg_correlation = float(np.mean(correlations)) if correlations else 0.0
        diversification_score = float(1 - avg_correlation)

        # Determine interpretation
        if diversification_score > 0.7:
            score = "High"
            suggestion = "Good diversification"
        elif diversification_score > 0.4:
            score = "Medium"
            suggestion = "Consider adding some uncorrelated assets"
        else:
            score = "Low"
            suggestion = "Portfolio needs more diversification"

        return {
            "correlation_matrix": correlation_matrix,
            "average_correlation": avg_correlation,
            "diversification_score": diversification_score,
            "interpretation": {
                "score": score,
                "suggestion": suggestion
            }
        }

    def _calculate_all_technical_indicators(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators in one pass"""
        if hist.empty:
            return {}

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        volume = hist["Volume"]

        # Moving averages and Bollinger Bands
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        sma_200 = close.rolling(window=200).mean()
        std_20 = close.rolling(window=20).std()
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        # Volume analysis
        volume_sma = volume.rolling(window=20).mean()
        volume_std = volume.rolling(window=20).std()
        relative_volume = volume / volume_sma
        
        # Support and resistance
        window = 20
        resistance_levels = []
        support_levels = []
        
        for i in range(window, len(high) - window):
            if all(high.iloc[i] >= high.iloc[i-window:i]) and all(high.iloc[i] >= high.iloc[i+1:i+window+1]):
                resistance_levels.append(float(high.iloc[i]))
            if all(low.iloc[i] <= low.iloc[i-window:i]) and all(low.iloc[i] <= low.iloc[i+1:i+window+1]):
                support_levels.append(float(low.iloc[i]))

        current_price = float(close.iloc[-1])
        
        # Compile all indicators
        indicators = {
            "price": {
                "current": current_price,
                "open": float(hist["Open"].iloc[-1]),
                "high": float(high.iloc[-1]),
                "low": float(low.iloc[-1]),
                "close": float(close.iloc[-1])
            },
            "moving_averages": {
                "sma_20": float(sma_20.iloc[-1]),
                "sma_50": float(sma_50.iloc[-1]),
                "sma_200": float(sma_200.iloc[-1])
            },
            "bollinger_bands": {
                "upper": float(upper_band.iloc[-1]),
                "middle": float(sma_20.iloc[-1]),
                "lower": float(lower_band.iloc[-1])
            },
            "rsi": {
                "value": float(rsi.iloc[-1]),
                "signal": "Oversold" if rsi.iloc[-1] < 30 else "Overbought" if rsi.iloc[-1] > 70 else "Neutral"
            },
            "macd": {
                "macd": float(macd.iloc[-1]),
                "signal": float(signal.iloc[-1]),
                "histogram": float(histogram.iloc[-1])
            },
            "volume": {
                "current": float(volume.iloc[-1]),
                "sma": float(volume_sma.iloc[-1]),
                "relative": float(relative_volume.iloc[-1])
            },
            "support_resistance": {
                "resistance_levels": sorted(set([round(x, 2) for x in resistance_levels])),
                "support_levels": sorted(set([round(x, 2) for x in support_levels])),
                "nearest_resistance": min((r for r in resistance_levels if r > current_price), default=None),
                "nearest_support": max((s for s in support_levels if s < current_price), default=None)
            }
        }

        # Add trend signals
        indicators["signals"] = {
            "trend": "Bullish" if current_price > indicators["moving_averages"]["sma_200"] else "Bearish",
            "momentum": "Bullish" if indicators["rsi"]["value"] > 50 else "Bearish",
            "macd": "Bullish" if indicators["macd"]["macd"] > indicators["macd"]["signal"] else "Bearish",
            "volume": "High" if indicators["volume"]["relative"] > 1.5 else "Low" if indicators["volume"]["relative"] < 0.5 else "Normal"
        }

        return indicators

    def analyze_technical_indicators(self, symbol: str) -> Dict:
        """Get comprehensive technical analysis"""
        try:
            hist = self._fetch_ticker_data(symbol)
            if hist.empty:
                return {"error": "No historical data available"}

            return self._calculate_all_technical_indicators(hist)
        except Exception as e:
            return {"error": f"Error calculating technical indicators: {str(e)}"}

    def get_price_chart_data(self, symbol: str, timeframe: str) -> Dict:
        """Get price chart data with technical analysis"""
        try:
            hist = self._fetch_ticker_data(symbol, timeframe)
            if hist.empty:
                return {"error": "No historical data available"}

            # Get technical indicators
            indicators = self._calculate_all_technical_indicators(hist)

            # Format OHLCV data
            ohlcv = [{
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"])
            } for date, row in hist.iterrows()]

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "ohlcv": ohlcv,
                "indicators": indicators
            }
        except Exception as e:
            return {"error": f"Error getting price chart data: {str(e)}"}

    def calculate_support_resistance(self, symbol: str) -> Dict:
        """Calculate support and resistance levels"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {"error": "No historical data available"}

            high = hist["High"]
            low = hist["Low"]
            close = hist["Close"]
            current_price = float(close.iloc[-1])

            # Find local maxima and minima
            window = 20
            resistance_levels = []
            support_levels = []

            for i in range(window, len(high) - window):
                if all(high.iloc[i] >= high.iloc[i-window:i]) and all(high.iloc[i] >= high.iloc[i+1:i+window+1]):
                    resistance_levels.append(float(high.iloc[i]))
                if all(low.iloc[i] <= low.iloc[i-window:i]) and all(low.iloc[i] <= low.iloc[i+1:i+window+1]):
                    support_levels.append(float(low.iloc[i]))

            # Get unique levels within tolerance
            resistance_levels = sorted(set([round(x, 2) for x in resistance_levels]))
            support_levels = sorted(set([round(x, 2) for x in support_levels]))

            return {
                "current_price": current_price,
                "resistance_levels": resistance_levels,
                "support_levels": support_levels,
                "nearest_resistance": min((r for r in resistance_levels if r > current_price), default=None),
                "nearest_support": max((s for s in support_levels if s < current_price), default=None)
            }
        except Exception as e:
            return {"error": f"Error calculating support/resistance levels: {str(e)}"}

    def generate_trading_signals(self, symbol: str) -> Dict:
        """Generate trading signals based on technical analysis"""
        try:
            indicators = self.analyze_technical_indicators(symbol)
            
            if "error" in indicators:
                return indicators

            signals = []
            
            # Moving Average signals
            ma = indicators["moving_averages"]
            if ma["sma_20"] > ma["sma_50"]:
                signals.append({
                    "type": "MA Crossover",
                    "signal": "Bullish",
                    "strength": "Medium",
                    "description": "20-day SMA above 50-day SMA"
                })
            elif ma["sma_20"] < ma["sma_50"]:
                signals.append({
                    "type": "MA Crossover",
                    "signal": "Bearish",
                    "strength": "Medium",
                    "description": "20-day SMA below 50-day SMA"
                })

            # RSI signals
            rsi = indicators["rsi"]
            if rsi["value"] < 30:
                signals.append({
                    "type": "RSI",
                    "signal": "Buy",
                    "strength": "Strong",
                    "description": "RSI indicates oversold conditions"
                })
            elif rsi["value"] > 70:
                signals.append({
                    "type": "RSI",
                    "signal": "Sell",
                    "strength": "Strong",
                    "description": "RSI indicates overbought conditions"
                })

            # MACD signals
            macd = indicators["macd"]
            if macd["macd"] > macd["signal"]:
                signals.append({
                    "type": "MACD",
                    "signal": "Bullish",
                    "strength": "Medium",
                    "description": "MACD line above signal line"
                })
            elif macd["macd"] < macd["signal"]:
                signals.append({
                    "type": "MACD",
                    "signal": "Bearish",
                    "strength": "Medium",
                    "description": "MACD line below signal line"
                })

            # Calculate overall signal
            bullish_signals = sum(1 for s in signals if s["signal"] in ["Bullish", "Buy"])
            bearish_signals = sum(1 for s in signals if s["signal"] in ["Bearish", "Sell"])
            
            overall_signal = "Bullish" if bullish_signals > bearish_signals else "Bearish" if bearish_signals > bullish_signals else "Neutral"
            confidence = min(max(abs(bullish_signals - bearish_signals) / len(signals), 0), 1) if signals else 0

            return {
                "signals": signals,
                "overall_signal": overall_signal,
                "confidence": float(confidence),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error generating trading signals: {str(e)}"}

    def analyze_volume(self, symbol: str) -> Dict:
        """Analyze trading volume patterns"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {"error": "No historical data available"}

            volume = hist["Volume"]
            close = hist["Close"]

            # Calculate volume metrics
            avg_volume = float(volume.mean())
            volume_std = float(volume.std())
            current_volume = float(volume.iloc[-1])

            # Volume trend
            volume_ma = volume.rolling(window=20).mean()
            volume_trend = "Increasing" if volume_ma.iloc[-1] > volume_ma.iloc[-20] else "Decreasing"

            # Volume price correlation
            returns = close.pct_change()
            volume_return_corr = float(returns.corr(volume))

            # Find unusual volume days
            unusual_volume_days = [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "volume": float(vol),
                    "z_score": float((vol - avg_volume) / volume_std)
                }
                for date, vol in volume.items()
                if abs(vol - avg_volume) > 2 * volume_std
            ]

            return {
                "current_volume": current_volume,
                "average_volume": avg_volume,
                "volume_trend": volume_trend,
                "volume_price_correlation": volume_return_corr,
                "unusual_volume_days": unusual_volume_days,
                "analysis": {
                    "relative_volume": float(current_volume / avg_volume),
                    "volume_signal": "High" if current_volume > avg_volume * 1.5 else "Low" if current_volume < avg_volume * 0.5 else "Normal",
                    "trend_strength": "Strong" if abs(volume_return_corr) > 0.7 else "Moderate" if abs(volume_return_corr) > 0.3 else "Weak"
                }
            }
        except Exception as e:
            return {"error": f"Error analyzing volume: {str(e)}"}

    def analyze_market_conditions(self) -> Dict:
        """Analyze overall market conditions"""
        try:
            # Get major market indices
            indices = ["^GSPC", "^DJI", "^IXIC", "^VIX"]
            market_data = {}
            
            for symbol in indices:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                if not hist.empty:
                    close = hist["Close"]
                    returns = close.pct_change()
                    market_data[symbol] = {
                        "current_price": float(close.iloc[-1]),
                        "daily_return": float(returns.iloc[-1] * 100),
                        "monthly_return": float((close.iloc[-1] / close.iloc[0] - 1) * 100),
                        "volatility": float(returns.std() * 100)
                    }

            # Calculate market sentiment
            sp500_return = market_data.get("^GSPC", {}).get("monthly_return", 0)
            vix_level = market_data.get("^VIX", {}).get("current_price", 0)
            
            sentiment = "Bullish" if sp500_return > 2 and vix_level < 20 else \
                       "Bearish" if sp500_return < -2 or vix_level > 30 else \
                       "Neutral"

            # Determine market phase
            if sp500_return > 5:
                market_phase = "Expansion"
            elif sp500_return < -5:
                market_phase = "Contraction"
            else:
                market_phase = "Consolidation"

            return {
                "timestamp": datetime.now().isoformat(),
                "market_data": market_data,
                "analysis": {
                    "sentiment": sentiment,
                    "market_phase": market_phase,
                    "volatility_regime": "High" if vix_level > 25 else "Low" if vix_level < 15 else "Normal",
                    "risk_level": "High" if vix_level > 30 else "Low" if vix_level < 15 else "Moderate"
                }
            }
        except Exception as e:
            return {"error": f"Error analyzing market conditions: {str(e)}"}

    def _analyze_portfolio_data(self, assets: Dict, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Comprehensive portfolio analysis in a single pass"""
        if not assets:
            return {
                "portfolio_value": 0,
                "returns": pd.Series(),
                "holdings": {},
                "metrics": {},
                "risk_metrics": {},
                "sector_allocation": {},
                "asset_type_allocation": {}
            }

        # Get historical data for all assets
        histories = {}
        holdings = {}
        total_value = 0
        sector_allocation = {}
        asset_type_allocation = {}

        for asset_id, asset in assets.items():
            # Current holdings analysis
            current_value = asset.get('current_value', 0)
            total_value += current_value
            
            holdings[asset_id] = {
                "symbol": asset['symbol'],
                "type": asset.get('type', 'Unknown'),
                "sector": asset.get('sector', 'Unknown'),
                "quantity": asset.get('quantity', 0),
                "current_value": current_value,
                "weight": 0  # Will be updated after total calculation
            }

            # Sector and asset type allocation
            sector = asset.get('sector', 'Unknown')
            asset_type = asset.get('type', 'Unknown')
            
            sector_allocation[sector] = sector_allocation.get(sector, 0) + current_value
            asset_type_allocation[asset_type] = asset_type_allocation.get(asset_type, 0) + current_value

            # Get historical data
            try:
                hist = self._fetch_ticker_data(asset['symbol'], "1y")
                if not hist.empty:
                    histories[asset_id] = hist['Close'] * asset.get('quantity', 0)
            except Exception:
                continue

        # Update weights
        if total_value > 0:
            for asset_id in holdings:
                holdings[asset_id]['weight'] = holdings[asset_id]['current_value'] / total_value
            
            sector_allocation = {k: v/total_value for k, v in sector_allocation.items()}
            asset_type_allocation = {k: v/total_value for k, v in asset_type_allocation.items()}

        # Calculate portfolio values and returns
        if histories:
            portfolio_values = pd.concat(histories.values(), axis=1).sum(axis=1)
            returns = portfolio_values.pct_change().dropna()
        else:
            portfolio_values = pd.Series()
            returns = pd.Series()

        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(returns)

        # Get market data for comparison
        market_data = self._get_market_data()
        market_returns = None
        if 'market' in market_data:
            market_returns = market_data['market']['Close'].pct_change().dropna()

        # Calculate portfolio metrics
        metrics = {
            "total_value": float(total_value),
            "number_of_assets": len(assets),
            "diversification_score": 1 - max(sector_allocation.values(), default=0),
        }

        if not returns.empty and market_returns is not None:
            # Align dates
            aligned_data = pd.concat([returns, market_returns], axis=1).dropna()
            if not aligned_data.empty:
                portfolio_returns = aligned_data.iloc[:, 0]
                market_returns = aligned_data.iloc[:, 1]
                
                # Calculate beta
                covariance = portfolio_returns.cov(market_returns)
                market_variance = market_returns.var()
                beta = covariance / market_variance if market_variance != 0 else 0
                
                # Calculate alpha
                risk_free_daily = self.risk_free_rate / 252
                alpha = (portfolio_returns.mean() - risk_free_daily) - beta * (market_returns.mean() - risk_free_daily)
                
                metrics.update({
                    "beta": float(beta),
                    "alpha": float(alpha),
                    "correlation_with_market": float(portfolio_returns.corr(market_returns))
                })

        return {
            "portfolio_value": total_value,
            "returns": returns,
            "holdings": holdings,
            "metrics": metrics,
            "risk_metrics": risk_metrics,
            "sector_allocation": sector_allocation,
            "asset_type_allocation": asset_type_allocation
        }

    def get_portfolio_analysis(self, assets: Dict) -> Dict:
        """Get comprehensive portfolio analysis"""
        try:
            analysis = self._analyze_portfolio_data(assets)
            
            return {
                "portfolio_value": float(analysis["portfolio_value"]),
                "holdings": analysis["holdings"],
                "metrics": analysis["metrics"],
                "risk_metrics": analysis["risk_metrics"],
                "allocations": {
                    "sector": analysis["sector_allocation"],
                    "asset_type": analysis["asset_type_allocation"]
                },
                "recommendations": self._generate_portfolio_recommendations(analysis)
            }
        except Exception as e:
            return {"error": f"Error analyzing portfolio: {str(e)}"}

    def _generate_portfolio_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate portfolio recommendations based on analysis"""
        recommendations = []
        
        # Check diversification
        if analysis["metrics"].get("diversification_score", 0) < 0.5:
            recommendations.append({
                "type": "Diversification",
                "priority": "High",
                "suggestion": "Consider diversifying across more sectors"
            })

        # Check risk metrics
        risk_metrics = analysis["risk_metrics"]
        if risk_metrics.get("sharpe_ratio", 0) < 1:
            recommendations.append({
                "type": "Risk-Adjusted Returns",
                "priority": "Medium",
                "suggestion": "Consider optimizing portfolio for better risk-adjusted returns"
            })

        if risk_metrics.get("volatility", 0) > 0.2:
            recommendations.append({
                "type": "Volatility",
                "priority": "High",
                "suggestion": "Consider reducing portfolio volatility"
            })

        # Check market exposure
        metrics = analysis["metrics"]
        if metrics.get("beta", 1) > 1.2:
            recommendations.append({
                "type": "Market Exposure",
                "priority": "Medium",
                "suggestion": "Consider reducing market exposure"
            })

        # Check sector concentration
        sector_allocation = analysis["sector_allocation"]
        max_sector_allocation = max(sector_allocation.values(), default=0)
        if max_sector_allocation > 0.3:
            max_sector = max(sector_allocation.items(), key=lambda x: x[1])[0]
            recommendations.append({
                "type": "Sector Concentration",
                "priority": "High",
                "suggestion": f"Consider reducing exposure to {max_sector} sector"
            })

        return recommendations
