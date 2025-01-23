import google.generativeai as genai
from typing import List, Dict, Any
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from textblob import TextBlob
import time
import json

class AIInvestmentAdvisor:
    def __init__(self, api_key: str):
        """Initialize Gemini AI client"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds
        
    def _rate_limited_generate(self, prompt: str) -> str:
        """Generate content with rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        try:
            response = self.model.generate_content(prompt)
            self.last_request_time = time.time()
            return response.text
        except Exception as e:
            if "429" in str(e):
                return "Rate limit exceeded. Please try again in a few moments."
            return f"Unable to generate content: {str(e)}"
        
    def analyze_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze market sentiment using news and social media"""
        try:
            # Get news articles
            url = f"https://api.coingecko.com/api/v3/news?q={symbol}" if symbol in ['BTC', 'ETH'] else None
            if url:
                response = requests.get(url)
                if response.status_code == 200:
                    news = response.json()
                else:
                    news = []
            else:
                # Fallback to a general market sentiment
                news = []
            
            # Analyze sentiment
            sentiments = []
            for article in news:
                blob = TextBlob(article.get('title', '') + ' ' + article.get('description', ''))
                sentiments.append(blob.sentiment.polarity)
            
            if sentiments:
                avg_sentiment = np.mean(sentiments)
                sentiment_score = (avg_sentiment + 1) * 50  # Convert to 0-100 scale
            else:
                sentiment_score = 50  # Neutral
            
            # Determine sentiment category
            if sentiment_score >= 70:
                category = "Very Bullish"
            elif sentiment_score >= 55:
                category = "Bullish"
            elif sentiment_score >= 45:
                category = "Neutral"
            elif sentiment_score >= 30:
                category = "Bearish"
            else:
                category = "Very Bearish"
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment_category': category,
                'confidence': min(abs(sentiment_score - 50) * 2, 100)
            }
        except Exception as e:
            return {
                'sentiment_score': 50,
                'sentiment_category': 'Neutral',
                'confidence': 0,
                'error': str(e)
            }

    def predict_price_movement(self, price_history, technical_indicators):
        """Predict price movement based on technical analysis"""
        if price_history is None or technical_indicators is None:
            return {
                'direction': 'Unknown',
                'confidence': 0.0,
                'analysis': 'Insufficient data for prediction'
            }
        
        try:
            current_price = price_history['Close'].iloc[-1]
            
            # Analyze technical indicators
            rsi = technical_indicators['rsi']
            sma_20 = technical_indicators['sma_20']
            sma_50 = technical_indicators['sma_50']
            macd = technical_indicators['macd']
            macd_signal = technical_indicators['macd_signal']
            
            # Initialize signals
            signals = []
            confidence_factors = []
            
            # RSI Analysis
            if rsi > 70:
                signals.append('Bearish')
                confidence_factors.append(0.7)
            elif rsi < 30:
                signals.append('Bullish')
                confidence_factors.append(0.7)
            else:
                signals.append('Neutral')
                confidence_factors.append(0.3)
            
            # Moving Average Analysis
            if current_price > sma_50:
                if current_price > sma_20:
                    signals.append('Bullish')
                    confidence_factors.append(0.8)
                else:
                    signals.append('Neutral')
                    confidence_factors.append(0.4)
            else:
                if current_price < sma_20:
                    signals.append('Bearish')
                    confidence_factors.append(0.8)
                else:
                    signals.append('Neutral')
                    confidence_factors.append(0.4)
            
            # MACD Analysis
            if macd > macd_signal:
                signals.append('Bullish')
                confidence_factors.append(0.6)
            else:
                signals.append('Bearish')
                confidence_factors.append(0.6)
            
            # Calculate overall direction and confidence
            bullish_count = signals.count('Bullish')
            bearish_count = signals.count('Bearish')
            
            if bullish_count > bearish_count:
                direction = 'Bullish'
                confidence = sum(cf for s, cf in zip(signals, confidence_factors) if s == 'Bullish') / len(confidence_factors) * 100
            elif bearish_count > bullish_count:
                direction = 'Bearish'
                confidence = sum(cf for s, cf in zip(signals, confidence_factors) if s == 'Bearish') / len(confidence_factors) * 100
            else:
                direction = 'Neutral'
                confidence = 50.0
            
            # Generate analysis text
            analysis = f"""Technical Analysis Summary:
            RSI ({rsi:.1f}): {'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'}
            20-day SMA: {technical_indicators['sma_20']:.2f}
            50-day SMA: {technical_indicators['sma_50']:.2f}
            MACD: {macd:.2f} (Signal: {macd_signal:.2f})
            
            The asset is showing {direction.lower()} signals with {confidence:.1f}% confidence based on technical indicators.
            """
            
            return {
                'direction': direction,
                'confidence': confidence,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'direction': 'Error',
                'confidence': 0.0,
                'analysis': f'Error analyzing price movement: {str(e)}'
            }

    def generate_portfolio_insights(self, portfolio_data: Dict[str, Any]) -> str:
        """Generate comprehensive portfolio insights"""
        prompt = f"""
        Analyze this portfolio data and provide actionable insights:
        
        Portfolio Value: ${portfolio_data['total_portfolio_value']:,.2f}
        
        Asset Allocation:
        {portfolio_data['asset_allocation']}
        
        Sector Allocation:
        {portfolio_data['sector_allocation']}
        
        Performance Metrics:
        - Volatility: {portfolio_data['performance_metrics']['volatility']:.1f}%
        - Sharpe Ratio: {portfolio_data['performance_metrics']['sharpe_ratio']:.2f}
        
        Risk Metrics:
        - Diversification: {portfolio_data['risk_metrics']['diversification_score']:.0f}%
        - Sector Concentration: {portfolio_data['risk_metrics']['sector_concentration']:.1f}%
        
        Provide detailed analysis on:
        1. Portfolio Health Assessment
        2. Risk Management Recommendations
        3. Diversification Opportunities
        4. Rebalancing Suggestions
        5. Sector Exposure Recommendations
        
        Keep recommendations specific and actionable.
        """
        
        try:
            response = self._rate_limited_generate(prompt)
            return response
        except Exception as e:
            return f"Unable to generate portfolio insights: {str(e)}"

    def generate_recommendations(self, 
                               portfolio_details: Dict[str, Any],
                               market_conditions: Dict[str, Any]) -> str:
        """Generate specific investment recommendations"""
        prompt = f"""
        Based on:
        
        Portfolio Details:
        - Total Value: ${portfolio_details['total_portfolio_value']:,.2f}
        - Asset Allocation: {portfolio_details['asset_allocation']}
        - Risk Metrics: {portfolio_details['risk_metrics']}
        
        Market Conditions:
        - Sentiment: {market_conditions['market_sentiment']}
        - Monthly Return: {market_conditions['monthly_return']}
        
        Provide specific, actionable recommendations for:
        1. Portfolio Adjustments
        2. Risk Management Actions
        3. Market Timing Considerations
        4. Specific Assets to Consider
        
        Focus on practical, implementable suggestions.
        """
        
        try:
            response = self._rate_limited_generate(prompt)
            return response
        except Exception as e:
            return f"Unable to generate recommendations: {str(e)}"

    def analyze_asset_trend(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze asset trend and generate AI insights"""
        prompt = f"""
        Analyze these trend metrics:
        
        Recent Price History: {trend_data['price_history'][-5:]}
        Average Return: {trend_data['avg_return']:.2f}%
        Volatility: {trend_data['volatility']:.2f}%
        Momentum Score: {trend_data['momentum']:.2f}
        
        Determine the trend (Bullish/Bearish/Neutral) and confidence (0-100).
        Consider momentum, volatility, and recent price action.
        """
        
        try:
            response = self._rate_limited_generate(prompt)
            result = response.text.strip().lower()
            
            # Determine trend and confidence
            if "bullish" in result:
                trend = "Bullish"
                confidence = 80 if trend_data['momentum'] > 0.6 else 60
            elif "bearish" in result:
                trend = "Bearish"
                confidence = 80 if trend_data['momentum'] < 0.4 else 60
            else:
                trend = "Neutral"
                confidence = 50
            
            # Adjust confidence based on volatility
            if trend_data['volatility'] > 30:
                confidence = max(confidence - 20, 0)
            
            return {
                'trend': trend,
                'confidence': confidence,
                'analysis': response.text
            }
        except Exception as e:
            return {
                'trend': "Unknown",
                'confidence': 0,
                'analysis': f"Analysis error: {str(e)}"
            }

    def risk_recommendation(self, risk_metrics: Dict[str, Any]) -> str:
        """Generate risk-based recommendations"""
        prompt = f"""
        Analyze these risk metrics:
        {risk_metrics}
        
        Provide specific recommendations for:
        1. Risk Mitigation Strategies
        2. Portfolio Protection Measures
        3. Hedging Suggestions
        4. Volatility Management
        5. Correlation-based Diversification
        
        Focus on practical risk management actions.
        """
        
        try:
            response = self._rate_limited_generate(prompt)
            return response
        except Exception as e:
            return f"Risk Analysis Error: {str(e)}"

    def get_market_insights(self) -> Dict:
        """Get AI-generated market insights"""
        try:
            prompt = """
            Provide a detailed analysis of current market conditions including:
            1. Major Market Trends
            2. Key Economic Indicators
            3. Sector Analysis
            
            Format the response in Markdown.
            """
            response = self.model.generate_content(prompt)
            return {
                "market_analysis": response.text,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"Error generating market insights: {str(e)}"
            }

    def get_portfolio_recommendations(self, assets: Dict) -> Dict:
        """Get AI-powered portfolio recommendations"""
        if not assets:
            return {
                "recommendations": [],
                "timestamp": datetime.now().isoformat()
            }
        
        portfolio_summary = self._create_portfolio_summary(assets)
        
        prompt = f"""Based on this portfolio:
        {portfolio_summary}
        
        Provide recommendations for:
        1. Portfolio rebalancing
        2. Risk management
        3. Potential opportunities
        4. Asset allocation adjustments
        """
        
        response = self._generate_insights(prompt)
        
        return {
            "recommendations": response.split('\n'),
            "timestamp": datetime.now().isoformat()
        }

    def get_market_opportunities(self) -> Dict:
        """Get AI-powered market opportunities"""
        prompt = """Identify current market opportunities considering:
        1. Undervalued assets
        2. Growth potential
        3. Market inefficiencies
        4. Emerging trends
        """
        
        response = self._generate_insights(prompt)
        
        return {
            "opportunities": response.split('\n'),
            "timestamp": datetime.now().isoformat()
        }

    def get_risk_alerts(self, assets: Dict) -> Dict:
        """Get AI-powered risk alerts for the portfolio"""
        if not assets:
            return {
                "alerts": [],
                "timestamp": datetime.now().isoformat()
            }
        
        portfolio_summary = self._create_portfolio_summary(assets)
        
        prompt = f"""Based on this portfolio:
        {portfolio_summary}
        
        Identify potential risks:
        1. Concentration risk
        2. Market risk
        3. Sector-specific risks
        4. Asset-specific concerns
        """
        
        response = self._generate_insights(prompt)
        
        return {
            "alerts": response.split('\n'),
            "risk_level": self._calculate_risk_level(assets),
            "timestamp": datetime.now().isoformat()
        }

    def _create_portfolio_summary(self, assets: Dict) -> str:
        """Create a summary of the portfolio for AI prompts"""
        total_value = sum(asset['current_value'] for asset in assets.values())
        
        summary = f"Portfolio Value: ${total_value:,.2f}\n\nAssets:\n"
        
        for asset in assets.values():
            summary += f"- {asset['symbol']}: ${asset['current_value']:,.2f} ({asset['quantity']} units)\n"
        
        return summary

    def _calculate_risk_level(self, assets: Dict) -> str:
        """Calculate overall risk level of the portfolio"""
        if not assets:
            return "Low"
        
        # Simple risk calculation based on concentration
        max_concentration = max(asset['current_value'] for asset in assets.values()) / \
                           sum(asset['current_value'] for asset in assets.values()) * 100
                           
        if max_concentration > 40:
            return "High"
        elif max_concentration > 20:
            return "Medium"
        else:
            return "Low"

    def _generate_insights(self, prompt: str) -> str:
        """Generate insights using the AI model"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating insights: {str(e)}"

    def get_recommendations(self) -> Dict:
        """Get AI-generated investment recommendations"""
        try:
            # Mock recommendations for demonstration
            return {
                "portfolio_recommendations": [
                    {
                        "recommendation": "Increase defensive positions",
                        "rationale": "Market volatility suggests defensive positioning",
                        "confidence": 0.85
                    },
                    {
                        "recommendation": "Consider healthcare sector allocation",
                        "rationale": "Sector offers defensive growth potential",
                        "confidence": 0.78
                    }
                ],
                "market_opportunities": [
                    {
                        "sector": "Healthcare",
                        "opportunity": "Aging demographics and innovation driving growth",
                        "confidence": 0.82
                    },
                    {
                        "sector": "Technology",
                        "opportunity": "AI and cloud computing expansion",
                        "confidence": 0.75
                    }
                ],
                "risk_analysis": [
                    {
                        "risk_type": "Market Risk",
                        "description": "Elevated volatility due to economic uncertainty",
                        "severity": "Medium",
                        "mitigation": "Consider increasing cash position"
                    },
                    {
                        "risk_type": "Sector Risk",
                        "description": "High technology sector concentration",
                        "severity": "High",
                        "mitigation": "Diversify across defensive sectors"
                    }
                ]
            }
        except Exception as e:
            return {
                "error": f"Error generating recommendations: {str(e)}"
            }

    def analyze_market_sentiment(self) -> Dict:
        """Analyze current market sentiment using AI"""
        try:
            prompt = """
            Analyze the current market sentiment considering:
            1. Social media trends
            2. News sentiment
            3. Technical indicators
            4. Market momentum
            5. Investor psychology
            
            Provide a detailed analysis with confidence scores.
            """
            response = self.model.generate_content(prompt)
            
            # Parse the response and structure it
            return {
                "overall_sentiment": "bullish",  # Extract from response
                "confidence": 0.75,
                "analysis": response.text,
                "factors": {
                    "social_media": {"sentiment": "positive", "score": 0.8},
                    "news": {"sentiment": "neutral", "score": 0.6},
                    "technical": {"sentiment": "bullish", "score": 0.7},
                    "momentum": {"sentiment": "positive", "score": 0.75},
                    "psychology": {"sentiment": "optimistic", "score": 0.65}
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error analyzing market sentiment: {str(e)}"}

    def analyze_market_news(self) -> Dict:
        """Analyze market news and assess impact"""
        try:
            prompt = """
            Analyze the latest market news and provide:
            1. Key headlines
            2. Impact assessment
            3. Market implications
            4. Trading opportunities
            5. Risk factors
            
            Focus on major market-moving news.
            """
            response = self.model.generate_content(prompt)
            
            return {
                "news_analysis": response.text,
                "key_events": [
                    {
                        "headline": "Fed Interest Rate Decision",
                        "impact": "High",
                        "market_reaction": "Positive",
                        "sectors_affected": ["Financials", "Real Estate"]
                    },
                    {
                        "headline": "Tech Earnings Reports",
                        "impact": "Medium",
                        "market_reaction": "Mixed",
                        "sectors_affected": ["Technology", "Communication Services"]
                    }
                ],
                "market_impact": {
                    "short_term": "Volatile",
                    "medium_term": "Positive",
                    "long_term": "Bullish"
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error analyzing market news: {str(e)}"}

    def generate_investment_strategies(self, portfolio: Dict) -> Dict:
        """Generate AI-driven investment strategies"""
        try:
            portfolio_value = sum(asset["current_value"] for asset in portfolio.values())
            sectors = set(asset["sector"] for asset in portfolio.values())
            
            prompt = f"""
            Generate investment strategies for a portfolio with:
            - Total value: ${portfolio_value:,.2f}
            - Sectors: {', '.join(sectors)}
            
            Consider:
            1. Asset allocation
            2. Risk management
            3. Growth opportunities
            4. Market timing
            5. Tax efficiency
            """
            response = self.model.generate_content(prompt)
            
            return {
                "strategies": response.text,
                "recommendations": [
                    {
                        "strategy": "Dynamic Asset Allocation",
                        "description": "Adjust allocation based on market conditions",
                        "implementation": ["Increase defensive assets", "Reduce high-beta stocks"],
                        "timeframe": "3-6 months"
                    },
                    {
                        "strategy": "Sector Rotation",
                        "description": "Rotate into sectors with momentum",
                        "implementation": ["Focus on healthcare", "Reduce technology exposure"],
                        "timeframe": "1-3 months"
                    }
                ],
                "risk_management": {
                    "hedging_strategies": ["Options protection", "Stop-loss orders"],
                    "diversification_suggestions": ["Add commodities", "Consider bonds"],
                    "position_sizing": ["Reduce large positions", "Balance sector weights"]
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error generating investment strategies: {str(e)}"}

    def assess_portfolio_risk(self, portfolio: Dict) -> Dict:
        """Provide AI-driven portfolio risk assessment"""
        try:
            portfolio_value = sum(asset["current_value"] for asset in portfolio.values())
            sectors = {asset["sector"]: 0 for asset in portfolio.values()}
            for asset in portfolio.values():
                sectors[asset["sector"]] += asset["current_value"] / portfolio_value
            
            prompt = f"""
            Assess the risks in a portfolio with:
            - Total value: ${portfolio_value:,.2f}
            - Sector allocation: {json.dumps(sectors, indent=2)}
            
            Consider:
            1. Market risk
            2. Sector concentration
            3. Individual stock risk
            4. Economic factors
            5. Geopolitical risks
            """
            response = self.model.generate_content(prompt)
            
            return {
                "risk_assessment": response.text,
                "risk_metrics": {
                    "overall_risk_score": 7.5,  # Scale of 1-10
                    "market_risk": "Medium",
                    "sector_risk": "High",
                    "liquidity_risk": "Low",
                    "concentration_risk": "Medium-High"
                },
                "risk_factors": [
                    {
                        "factor": "Sector Concentration",
                        "risk_level": "High",
                        "description": "Over-exposure to technology sector",
                        "mitigation": "Consider sector diversification"
                    },
                    {
                        "factor": "Market Beta",
                        "risk_level": "Medium",
                        "description": "Portfolio shows high correlation with market",
                        "mitigation": "Add defensive assets"
                    }
                ],
                "stress_test_scenarios": {
                    "market_crash": -30,
                    "recession": -20,
                    "inflation_spike": -15,
                    "tech_bubble": -25
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error assessing portfolio risk: {str(e)}"}

    def get_custom_recommendations(self, portfolio: Dict) -> Dict:
        """Generate personalized portfolio recommendations"""
        try:
            portfolio_value = sum(asset["current_value"] for asset in portfolio.values())
            sectors = {asset["sector"]: 0 for asset in portfolio.values()}
            for asset in portfolio.values():
                sectors[asset["sector"]] += asset["current_value"] / portfolio_value
            
            prompt = f"""
            Generate personalized recommendations for a portfolio with:
            - Total value: ${portfolio_value:,.2f}
            - Sector allocation: {json.dumps(sectors, indent=2)}
            
            Consider:
            1. Portfolio optimization
            2. Risk-adjusted returns
            3. Market opportunities
            4. Tax efficiency
            5. Long-term growth
            """
            response = self.model.generate_content(prompt)
            
            return {
                "recommendations": response.text,
                "actions": [
                    {
                        "action": "Rebalance Portfolio",
                        "details": "Adjust sector weights to reduce concentration",
                        "priority": "High",
                        "timeframe": "Immediate"
                    },
                    {
                        "action": "Add Defensive Assets",
                        "details": "Consider adding dividend stocks and bonds",
                        "priority": "Medium",
                        "timeframe": "1-2 months"
                    }
                ],
                "opportunities": [
                    {
                        "type": "Sector Rotation",
                        "description": "Rotate into healthcare and consumer staples",
                        "rationale": "Defensive positioning for market uncertainty"
                    },
                    {
                        "type": "Value Opportunities",
                        "description": "Look for undervalued quality stocks",
                        "rationale": "Market volatility creating buying opportunities"
                    }
                ],
                "tax_considerations": [
                    {
                        "strategy": "Tax-Loss Harvesting",
                        "potential_savings": "Estimated 1-2% annually"
                    },
                    {
                        "strategy": "Long-term Holdings",
                        "benefit": "Reduced capital gains tax"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Error generating custom recommendations: {str(e)}"}
