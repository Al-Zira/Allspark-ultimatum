import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List
import os
import uuid

class Database:
    def __init__(self, db_path="data/portfolio.db"):
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables"""
        self.cursor.executescript('''
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            type TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            asset_id TEXT NOT NULL,
            type TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        );

        CREATE TABLE IF NOT EXISTS portfolio_history (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            total_value REAL NOT NULL,
            cash_balance REAL NOT NULL
        );
        ''')
        self.conn.commit()
    
    def add_asset(self, asset_data: Dict[str, Any]) -> bool:
        """Add a new asset to the portfolio"""
        try:
            self.cursor.execute('''
            INSERT INTO assets (id, symbol, quantity, purchase_price, purchase_date, type)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                asset_data['symbol'],
                asset_data['quantity'],
                asset_data['purchase_price'],
                datetime.now().isoformat(),
                asset_data['type']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding asset: {e}")
            return False
    
    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Get asset details by ID"""
        try:
            self.cursor.execute('SELECT * FROM assets WHERE id = ?', (asset_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'symbol': result[1],
                    'quantity': result[2],
                    'purchase_price': result[3],
                    'purchase_date': result[4],
                    'type': result[5]
                }
            return None
        except Exception as e:
            print(f"Error getting asset: {e}")
            return None
    
    def get_all_assets(self) -> List[Dict[str, Any]]:
        """Get all assets in the portfolio"""
        try:
            self.cursor.execute('SELECT * FROM assets')
            results = self.cursor.fetchall()
            return [{
                'id': row[0],
                'symbol': row[1],
                'quantity': row[2],
                'purchase_price': row[3],
                'purchase_date': row[4],
                'type': row[5]
            } for row in results]
        except Exception as e:
            print(f"Error getting assets: {e}")
            return []
    
    def update_asset(self, asset_id: str, asset_data: Dict[str, Any]) -> bool:
        """Update asset details"""
        try:
            self.cursor.execute('''
            UPDATE assets
            SET quantity = ?, purchase_price = ?
            WHERE id = ?
            ''', (
                asset_data['quantity'],
                asset_data['purchase_price'],
                asset_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating asset: {e}")
            return False
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset from the portfolio"""
        try:
            self.cursor.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting asset: {e}")
            return False
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Record a new transaction"""
        try:
            self.cursor.execute('''
            INSERT INTO transactions (id, asset_id, type, quantity, price, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                transaction_data['asset_id'],
                transaction_data['type'],
                transaction_data['quantity'],
                transaction_data['price'],
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def get_transactions(self, asset_id: str = None) -> List[Dict[str, Any]]:
        """Get transaction history"""
        try:
            if asset_id:
                self.cursor.execute('SELECT * FROM transactions WHERE asset_id = ?', (asset_id,))
            else:
                self.cursor.execute('SELECT * FROM transactions')
            results = self.cursor.fetchall()
            return [{
                'id': row[0],
                'asset_id': row[1],
                'type': row[2],
                'quantity': row[3],
                'price': row[4],
                'timestamp': row[5]
            } for row in results]
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def add_portfolio_snapshot(self, total_value: float, cash_balance: float) -> bool:
        """Record portfolio value at a point in time"""
        try:
            self.cursor.execute('''
            INSERT INTO portfolio_history (id, timestamp, total_value, cash_balance)
            VALUES (?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                datetime.now().isoformat(),
                total_value,
                cash_balance
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding portfolio snapshot: {e}")
            return False
    
    def get_portfolio_history(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get portfolio value history"""
        try:
            if start_date and end_date:
                self.cursor.execute('''
                SELECT * FROM portfolio_history
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
                ''', (start_date, end_date))
            else:
                self.cursor.execute('SELECT * FROM portfolio_history ORDER BY timestamp')
            results = self.cursor.fetchall()
            return [{
                'id': row[0],
                'timestamp': row[1],
                'total_value': row[2],
                'cash_balance': row[3]
            } for row in results]
        except Exception as e:
            print(f"Error getting portfolio history: {e}")
            return []
    
    def __del__(self):
        """Close database connection"""
        self.conn.close() 