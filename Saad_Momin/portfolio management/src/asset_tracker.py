import yfinance as yf
import pandas as pd
from typing import Dict, List, Any
import uuid
from datetime import datetime, timedelta
import json
import os
from config.config import Config
import numpy as np
from src.ai_insights import AIInvestmentAdvisor
import requests
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from src.database import Database
from src.utils import calculate_technical_indicators, get_asset_info

class AssetTracker:
    def __init__(self, db=None):
        """Initialize AssetTracker with optional database"""
        self.db = db
        self.assets = {}
    
    def add_asset(self, asset: Dict) -> Dict:
        """Add a new asset to the portfolio"""
        try:
            asset_id = str(uuid.uuid4())
            
            # Get asset info from Yahoo Finance
            ticker = yf.Ticker(asset["symbol"])
            info = ticker.info
            
            new_asset = {
                "symbol": asset["symbol"],
                "name": info.get("longName", asset["symbol"]),
                "type": asset["type"],  # Use the provided asset type
                "quantity": asset["shares"],
                "purchase_price": asset["price"],
                "current_value": asset["shares"] * asset["price"],  # Use purchase price as current value for now
                "sector": info.get("sector", "Unknown")
            }
            
            # Store in memory
            self.assets[asset_id] = new_asset
            
            # Store in database if available
            if self.db:
                self.db.add_asset({
                    "id": asset_id,
                    **new_asset,
                    "purchase_date": datetime.now().isoformat()
                })
            
            return {
                "asset_id": asset_id,
                "asset": new_asset
            }
            
        except Exception as e:
            return {
                "error": f"Error adding asset: {str(e)}"
            }
    
    def get_all_assets(self) -> Dict:
        """Get all assets in the portfolio"""
        if self.db:
            return self.db.get_all_assets()
        
        # Return assets with current values updated from Yahoo Finance
        updated_assets = {}
        for asset_id, asset in self.assets.items():
            try:
                # Get current price from Yahoo Finance
                ticker = yf.Ticker(asset["symbol"])
                current_price = ticker.history(period="1d")["Close"].iloc[-1]
                
                # Update current value
                updated_asset = asset.copy()
                updated_asset["current_value"] = current_price * asset["quantity"]
                updated_assets[asset_id] = updated_asset
            except Exception:
                # If we can't get current price, use the last known value
                updated_assets[asset_id] = asset
        
        return updated_assets
    
    def update_asset(self, asset_id: str, updates: Dict) -> Dict:
        """Update an existing asset"""
        if asset_id not in self.assets:
            return {"error": "Asset not found"}
        
        try:
            for key, value in updates.items():
                if key in self.assets[asset_id]:
                    self.assets[asset_id][key] = value
            
            # Update database if available
            if self.db:
                self.db.update_asset(asset_id, self.assets[asset_id])
            
            return {"asset": self.assets[asset_id]}
            
        except Exception as e:
            return {"error": f"Error updating asset: {str(e)}"}
    
    def delete_asset(self, asset_id: str) -> Dict:
        """Delete an asset from the portfolio"""
        if asset_id not in self.assets:
            return {"error": "Asset not found"}
        
        try:
            deleted_asset = self.assets.pop(asset_id)
            
            # Delete from database if available
            if self.db:
                self.db.remove_asset(asset_id)
            
            return {"deleted": deleted_asset}
            
        except Exception as e:
            return {"error": f"Error deleting asset: {str(e)}"}
    
    def get_asset(self, asset_id: str) -> Dict:
        """Get a specific asset by ID"""
        if asset_id not in self.assets:
            return {"error": "Asset not found"}
        
        return {"asset": self.assets[asset_id]}
