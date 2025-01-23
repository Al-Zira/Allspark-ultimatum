import google.generativeai as genai
from typing import Dict, List
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

class AIInvestmentAdvisor:
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Load indices from environment
        indices_str = os.getenv('MARKET_INDICES', '')
        self.indices = {}
        if indices_str:
            for pair in indices_str.split(','):
                if ':' in pair:
                    symbol, name = pair.split(':')
                    self.indices[symbol.strip()] = name.strip()
        
        # Load sectors from environment
        sectors_str = os.getenv('MARKET_SECTORS', '')
        self.sectors = {}
        if sectors_str:
            for pair in sectors_str.split(','):
                if ':' in pair:
                    symbol, name = pair.split(':')
                    self.sectors[symbol.strip()] = name.strip()

    def get_market_insights(self) -> Dict:
        """Get AI-generated market analysis"""
        try:
            # Get market data using configured indices
            market_data = {}
            for symbol, name in self.indices.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                if not hist.empty:
                    market_data[name] = {
                        "current": hist['Close'][-1],
                        "change": (hist['Close'][-1] / hist['Close'][0] - 1) * 100,
                        "volatility": hist['Close'].pct_change().std() * np.sqrt(252) * 100
                    }

            # Generate prompt for AI
            market_stats = "\n".join([
                f"{name}: {data.get('change', 0):.2f}% MTD, Volatility: {data.get('volatility', 0):.2f}%"
                for name, data in market_data.items()
            ])
            
            prompt = f"""
            Analyze the current market conditions based on the following data:
            
            {market_stats}
            
            Provide a detailed market analysis including:
            1. Overall market sentiment
            2. Key trends and observations
            3. Risk factors to consider
            4. Sector-specific insights
            """

            if self.api_key:
                response = self.model.generate_content(prompt)
                analysis = response.text
            else:
                analysis = "API key not configured. Unable to generate market analysis."

            return {
                "market_analysis": analysis,
                "market_data": market_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"Error generating market insights: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def get_recommendations(self) -> Dict:
        """Get AI-powered investment recommendations"""
        try:
            # Get sector performance using configured sectors
            sector_performance = {}
            for symbol, sector in self.sectors.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1mo")
                    if not hist.empty:
                        perf = (hist['Close'][-1] / hist['Close'][0] - 1) * 100
                        sector_performance[sector] = perf
                except:
                    continue

            # Generate prompt for AI
            prompt = f"""
            Based on the following sector performance data:
            {', '.join([f'{k}: {v:.2f}%' for k, v in sector_performance.items()])}
            
            Provide investment recommendations including:
            1. Top performing sectors to consider
            2. Sectors to avoid or reduce exposure
            3. Specific investment opportunities
            4. Risk considerations
            """

            if self.api_key:
                response = self.model.generate_content(prompt)
                analysis = response.text
                
                # Parse recommendations into structured format
                recommendations = {
                    "portfolio_recommendations": [
                        {"sector": k, "action": "Increase exposure" if v > 2 else "Reduce exposure" if v < -2 else "Maintain position"}
                        for k, v in sector_performance.items()
                    ],
                    "market_opportunities": [
                        {"sector": k, "performance": f"{v:.2f}%", "reason": "Strong sector performance"}
                        for k, v in sector_performance.items() if v > 3
                    ],
                    "risk_alerts": [
                        {"sector": k, "performance": f"{v:.2f}%", "warning": "Sector underperformance"}
                        for k, v in sector_performance.items() if v < -3
                    ],
                    "ai_analysis": analysis
                }
            else:
                recommendations = {
                    "portfolio_recommendations": [],
                    "market_opportunities": [],
                    "risk_alerts": [],
                    "error": "API key not configured"
                }

            return recommendations
        except Exception as e:
            return {
                "error": f"Error generating recommendations: {str(e)}",
                "portfolio_recommendations": [],
                "market_opportunities": [],
                "risk_alerts": []
            }

    def analyze_market_sentiment(self) -> Dict:
        """Analyze market sentiment"""
        try:
            # Get market indicators
            vix = yf.Ticker("^VIX")
            spy = yf.Ticker("SPY")
            
            vix_hist = vix.history(period="1mo")
            spy_hist = spy.history(period="1mo")
            
            if not vix_hist.empty and not spy_hist.empty:
                vix_current = vix_hist['Close'][-1]
                spy_change = (spy_hist['Close'][-1] / spy_hist['Close'][0] - 1) * 100
                
                # Generate prompt for AI
                prompt = f"""
                Analyze market sentiment based on:
                VIX Index: {vix_current:.2f}
                S&P 500 Monthly Change: {spy_change:.2f}%
                
                Provide:
                1. Overall sentiment (bullish/bearish/neutral)
                2. Confidence level
                3. Key factors influencing sentiment
                """

                if self.api_key:
                    response = self.model.generate_content(prompt)
                    analysis = response.text
                    
                    # Determine sentiment based on indicators
                    sentiment = "bullish" if spy_change > 2 and vix_current < 20 else \
                               "bearish" if spy_change < -2 or vix_current > 30 else \
                               "neutral"
                    
                    confidence = 0.8 if abs(spy_change) > 5 or abs(vix_current - 20) > 10 else 0.5
                    
                    return {
                        "sentiment": sentiment,
                        "confidence": confidence,
                        "analysis": analysis,
                        "indicators": {
                            "vix": float(vix_current),
                            "spy_monthly_change": float(spy_change)
                        }
                    }
            
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": "Insufficient market data"
            }
        except Exception as e:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }

    def analyze_market_news(self) -> Dict:
        """Analyze market news and its potential impact"""
        try:
            # Get news for major indices
            spy = yf.Ticker("SPY")
            news = spy.news[:5]  # Get latest 5 news items
            
            if news:
                # Generate prompt for AI
                news_texts = "\n".join([f"- {item['title']}" for item in news])
                prompt = f"""
                Analyze the following market news and their potential impact:
                {news_texts}
                
                Provide:
                1. Key themes and trends
                2. Potential market impact
                3. Sectors likely to be affected
                4. Risk implications
                """

                if self.api_key:
                    response = self.model.generate_content(prompt)
                    analysis = response.text
                    
                    return {
                        "news_analysis": [
                            {
                                "title": item['title'],
                                "source": item.get('source', 'Unknown'),
                                "timestamp": datetime.fromtimestamp(item['providerPublishTime']).isoformat()
                            }
                            for item in news
                        ],
                        "impact_assessment": {
                            "analysis": analysis,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
            
            return {
                "news_analysis": [],
                "impact_assessment": {
                    "error": "No recent news available"
                }
            }
        except Exception as e:
            return {
                "news_analysis": [],
                "impact_assessment": {
                    "error": str(e)
                }
            } 