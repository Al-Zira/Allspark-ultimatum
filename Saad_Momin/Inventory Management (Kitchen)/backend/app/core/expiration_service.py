from datetime import datetime, timedelta
from app.models.expiration import ExpirationTracker, ExpirationStatus
from app.models.inventory import InventoryItem
from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List, Dict

class ExpirationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_expiring_items(self, days_threshold: int = 7) -> List[Dict]:
        """Get items that are expiring soon or already expired"""
        try:
            # Calculate the threshold date
            threshold_date = datetime.utcnow() + timedelta(days=days_threshold)
            
            # Query items that are expiring soon or expired
            expiring_items = (
                self.db.query(ExpirationTracker)
                .join(InventoryItem)
                .filter(ExpirationTracker.expiration_date <= threshold_date)
                .all()
            )

            # Format the response
            return [
                {
                    "id": tracker.item.id,
                    "name": tracker.item.name,
                    "expiration_date": tracker.expiration_date.isoformat(),
                    "status": tracker.status,
                    "days_until_expiration": (tracker.expiration_date - datetime.utcnow()).days
                }
                for tracker in expiring_items
            ]
        except Exception as e:
            logger.error(f"Error getting expiring items: {str(e)}")
            return []
    
    async def update_expiration_statuses(self):
        """Update the status of all expiration trackers"""
        try:
            now = datetime.utcnow()
            warning_threshold = now + timedelta(days=7)

            # Get all active expiration trackers
            trackers = self.db.query(ExpirationTracker).all()

            for tracker in trackers:
                if tracker.expiration_date <= now:
                    tracker.status = ExpirationStatus.EXPIRED
                elif tracker.expiration_date <= warning_threshold:
                    tracker.status = ExpirationStatus.WARNING
                else:
                    tracker.status = ExpirationStatus.GOOD

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating expiration statuses: {str(e)}")
            raise
    
    def get_expired_items(self) -> List[ExpirationTracker]:
        """Get all expired items"""
        return self.db.query(ExpirationTracker).filter(
            ExpirationTracker.status == ExpirationStatus.EXPIRED
        ).all()
    
    def suggest_consumption_priority(self) -> List[dict]:
        """Generate prioritized list of items to consume"""
        expiring_items = self.get_expiring_items()
        
        prioritized_items = []
        for item in expiring_items:
            prioritized_items.append({
                'item_name': item.item.name,
                'days_remaining': item.days_until_expiration,
                'quantity': item.current_quantity,
                'freshness': item.freshness_percentage,
                'priority_score': self._calculate_priority_score(item)
            })
        
        return sorted(prioritized_items, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_priority_score(self, item: ExpirationTracker) -> float:
        """Calculate priority score based on expiration and quantity"""
        days_remaining = max(item.days_until_expiration, 0)
        freshness = item.freshness_percentage or 0
        
        # Higher score = higher priority to consume
        return (1 / (days_remaining + 1)) * 100 + (100 - freshness) * 0.5 