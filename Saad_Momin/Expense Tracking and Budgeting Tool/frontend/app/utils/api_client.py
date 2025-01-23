import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Force the base URL to use 127.0.0.1
API_BASE_URL = "http://127.0.0.1:8000"

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        # Test the connection
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
        except Exception as e:
            print(f"Warning: Could not connect to API at {self.base_url}")
            print(f"Error: {str(e)}")

    def _format_datetime(self, dt):
        """Format datetime object to ISO format with timezone info"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        return dt

    def _get(self, endpoint: str, params=None):
        # Format datetime parameters if they exist
        if params:
            params = {
                k: self._format_datetime(v) if isinstance(v, datetime) else v
                for k, v in params.items()
            }
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict):
        # Format datetime fields in the data
        formatted_data = {
            k: self._format_datetime(v) if isinstance(v, datetime) else v
            for k, v in data.items()
        }
        response = requests.post(f"{self.base_url}{endpoint}", json=formatted_data)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str):
        response = requests.delete(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()

    # Expense endpoints
    def create_expense(self, expense_data: dict):
        return self._post("/expenses/", expense_data)

    def get_expenses(self, start_date=None, end_date=None, category=None):
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if category:
            params["category"] = category
        return self._get("/expenses/", params)

    def get_expense_stats(self, start_date=None, end_date=None):
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._get("/expenses/stats", params)

    def get_category_distribution(self):
        return self._get("/expenses/distribution")

    def get_monthly_trend(self):
        return self._get("/expenses/monthly-trend")

    # Budget endpoints
    def create_or_update_budget(self, budget_data: dict):
        return self._post("/budgets/", budget_data)

    def get_budgets(self):
        return self._get("/budgets/")

    def get_budget_alerts(self):
        return self._get("/budgets/alerts")

    def delete_budget(self, category: str):
        return self._delete(f"/budgets/{category}")

    # AI Insights endpoints
    def get_spending_insights(self):
        return self._get("/insights/spending-analysis")

    def get_category_suggestion(self, description: str, amount: float):
        params = {
            "description": description,
            "amount": amount
        }
        return self._get("/insights/suggest-category", params)

    def get_budget_recommendations(self):
        return self._get("/insights/budget-recommendations") 