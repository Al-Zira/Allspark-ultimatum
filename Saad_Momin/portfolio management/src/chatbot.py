import google.generativeai as genai
from typing import Dict
from datetime import datetime

class FinanceChatbot:
    def __init__(self, api_key: str):
        """Initialize the chatbot with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
    
    def generate_response(self, message: str) -> str:
        """Generate a response to a general finance question"""
        try:
            prompt = f"""
            You are a financial advisor assistant. Answer the following question:
            {message}
            
            Provide a clear, concise, and informative response.
            """
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def analyze_portfolio(self, portfolio: Dict, message: str) -> str:
        """Analyze portfolio based on user's question"""
        try:
            portfolio_value = sum(asset["current_value"] for asset in portfolio.values())
            sectors = {asset["sector"]: 0 for asset in portfolio.values()}
            for asset in portfolio.values():
                sectors[asset["sector"]] += asset["current_value"] / portfolio_value
            
            prompt = f"""
            You are a portfolio analysis assistant. Answer the following question about this portfolio:
            
            Portfolio Details:
            - Total Value: ${portfolio_value:,.2f}
            - Number of Assets: {len(portfolio)}
            - Sector Allocation: {sectors}
            
            Question: {message}
            
            Provide a detailed analysis and specific recommendations.
            """
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing portfolio: {str(e)}"
    
    def analyze_market(self, message: str) -> str:
        """Analyze market conditions based on user's question"""
        try:
            prompt = f"""
            You are a market analysis assistant. Answer the following question about current market conditions:
            {message}
            
            Consider:
            1. Market trends
            2. Economic indicators
            3. Sector performance
            4. Risk factors
            5. Investment opportunities
            
            Provide a comprehensive analysis with specific insights.
            """
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing market: {str(e)}"