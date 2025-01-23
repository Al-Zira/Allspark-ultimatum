import requests
from typing import Dict, List, Optional
import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# Export API_URL for use in other modules
__all__ = ['API_URL', 'fetch_inventory', 'fetch_analytics', 'fetch_recommendations', 
           'fetch_expiring_items', 'add_inventory_item', 'remove_inventory_item', 
           'update_item_quantity', 'clear_recommendation_context', 'get_category_suggestion',
           'get_market_price']

class APIError(Exception):
    """Custom exception for API errors"""
    pass

def handle_api_error(response: requests.Response) -> None:
    """Handle API error responses"""
    try:
        error_data = response.json()
        error_message = error_data.get('detail', str(error_data))
    except:
        error_message = f"Error: {response.status_code} - {response.text}"
    raise APIError(error_message)

def fetch_inventory() -> List[Dict]:
    """Fetch inventory data from API"""
    try:
        response = requests.get(f"{API_URL}/inventory")
        if response.ok:
            return response.json()
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to connect to the server: {str(e)}")
        return []

def fetch_analytics() -> Dict:
    """Fetch inventory analytics from API"""
    try:
        response = requests.get(f"{API_URL}/inventory/analytics")
        if response.ok:
            return response.json()
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to fetch analytics: {str(e)}")
        return {}

def fetch_recommendations(preferences: Optional[Dict] = None) -> Dict:
    """Fetch recommendations from API"""
    try:
        params = {}
        if preferences:
            params.update(preferences)
        response = requests.get(f"{API_URL}/recommendations", params=params)
        if response.ok:
            return response.json()
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to fetch recommendations: {str(e)}")
        return {}

def fetch_expiring_items() -> List[Dict]:
    """Fetch expiring items from API"""
    try:
        response = requests.get(f"{API_URL}/expiring-items")
        if response.ok:
            return response.json()
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to fetch expiring items: {str(e)}")
        return []

def add_inventory_item(item_data: Dict) -> Optional[Dict]:
    """Add new inventory item through API"""
    try:
        # Convert the data to query parameters for FastAPI
        params = {
            "name": item_data["name"],
            "quantity": item_data["quantity"],
            "unit": item_data["unit"],
            "category": item_data["category"],
            "expiration_date": item_data["expiration_date"]
        }
        response = requests.post(f"{API_URL}/inventory", params=params)
        if response.ok:
            return response.json()
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to add item: {str(e)}")
        return None

def remove_inventory_item(item_id: int) -> bool:
    """Remove an item from inventory"""
    try:
        response = requests.delete(f"{API_URL}/inventory/{item_id}")
        if response.ok:
            return True
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to remove item: {str(e)}")
        return False

def update_item_quantity(item_id: int, quantity: float, operation: str = "set") -> Optional[Dict]:
    """Update item quantity"""
    try:
        params = {
            "quantity": quantity,
            "operation": operation
        }
        response = requests.put(f"{API_URL}/inventory/{item_id}/quantity", params=params)
        if response.ok:
            return response.json()
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to update quantity: {str(e)}")
        return None

def clear_recommendation_context() -> bool:
    """Clear the recommendation context"""
    try:
        response = requests.post(f"{API_URL}/recommendations/clear-context")
        return response.ok
    except requests.RequestException as e:
        st.error(f"Failed to clear context: {str(e)}")
        return False

def get_category_suggestion(item_name: str) -> Optional[str]:
    """Get category suggestion for an item using AI"""
    try:
        response = requests.get(f"{API_URL}/category/suggest", params={"item_name": item_name})
        if response.ok:
            return response.json().get("category")
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to get category suggestion: {str(e)}")
        return None

def get_market_price(item_name: str, category: str = None) -> Optional[float]:
    """Get current market price for an item using Gemini AI"""
    try:
        params = {
            "item_name": item_name,
            "category": category
        }
        response = requests.get(f"{API_URL}/market-price", params=params)
        if response.ok:
            return response.json().get("price")
        handle_api_error(response)
    except requests.RequestException as e:
        st.error(f"Failed to get market price: {str(e)}")
        return None 