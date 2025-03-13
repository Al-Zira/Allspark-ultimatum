import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()

class AIFinancialInsights:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _format_expenses_for_analysis(self, expenses):
        """Format expenses data for AI analysis"""
        if not expenses:
            return "No expense data available."
        
        df = pd.DataFrame(expenses)
        summary = []
        
        # Total spending
        total_spending = df['amount'].sum()
        summary.append(f"Total Spending: ${total_spending:.2f}")
        
        # Category breakdown
        category_spending = df.groupby('category')['amount'].sum()
        summary.append("\nCategory Breakdown:")
        for category, amount in category_spending.items():
            percentage = (amount / total_spending) * 100
            summary.append(f"- {category}: ${amount:.2f} ({percentage:.1f}%)")
        
        # Monthly trend
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
        monthly_spending = df.groupby('month')['amount'].sum()
        summary.append("\nMonthly Spending:")
        for month, amount in monthly_spending.items():
            summary.append(f"- {month}: ${amount:.2f}")
        
        return "\n".join(summary)

    def get_spending_insights(self, expenses, budgets):
        """Generate AI insights about spending patterns"""
        if not expenses:
            return "No expenses data available for analysis."
        
        # Prepare data summary for AI
        data_summary = self._format_expenses_for_analysis(expenses)
        budget_info = "\nBudget Information:"
        if budgets:
            for budget in budgets:
                budget_info += f"\n- {budget['category']}: ${budget['monthly_limit']:.2f}/month"
        else:
            budget_info += "\nNo budgets set."
        
        prompt = f"""
        As a financial advisor, analyze this spending data and provide insights:

        {data_summary}
        {budget_info}

        Please provide:
        1. Key observations about spending patterns
        2. Specific recommendations for budget management
        3. Areas of concern or potential savings opportunities
        4. Positive financial habits observed

        Keep the analysis concise and actionable.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating AI insights: {str(e)}"

    def suggest_category(self, description: str, amount: float, existing_categories: list):
        """Suggest a category for a new expense based on description"""
        categories_info = "\n".join([f"- {cat}" for cat in existing_categories]) if existing_categories else "No existing categories"
        
        prompt = f"""
        As a financial categorization expert, suggest the most appropriate category for this expense:

        Description: {description}
        Amount: ${amount:.2f}

        Existing categories:
        {categories_info}

        Please provide:
        1. The most appropriate category name (if it matches an existing category, use that)
        2. A brief explanation of why this category is appropriate

        Return ONLY the category name in UPPERCASE, nothing else.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().upper()
        except Exception as e:
            return None

    def get_budget_recommendations(self, expenses, current_budgets):
        """Generate budget recommendations based on spending patterns"""
        if not expenses:
            return "No expense data available for budget recommendations."
        
        data_summary = self._format_expenses_for_analysis(expenses)
        current_budget_info = "\nCurrent Budgets:"
        if current_budgets:
            for budget in current_budgets:
                current_budget_info += f"\n- {budget['category']}: ${budget['monthly_limit']:.2f}/month"
        else:
            current_budget_info += "\nNo budgets currently set."
        
        prompt = f"""
        As a budget planning expert, analyze this spending data and provide budget recommendations:

        {data_summary}
        {current_budget_info}

        Please provide:
        1. Recommended monthly budget for each spending category
        2. Explanation for each recommendation
        3. Suggestions for new budget categories if needed
        4. Tips for staying within these budgets

        Focus on realistic and achievable budgets based on the spending patterns.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating budget recommendations: {str(e)}" 