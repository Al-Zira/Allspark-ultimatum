from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem
from app.models.expiration import ExpirationTracker, ExpirationStatus
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.core.logger import logger
from sqlalchemy import text, func
from app.ai.gemini_service import GeminiService

class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.gemini_service = GeminiService()
    
    async def get_all_items(self) -> List[Dict]:
        """Get all inventory items"""
        items = self.db.query(InventoryItem).all()
        return [
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "value_per_unit": item.value_per_unit,
                "total_value": item.value_per_unit * item.quantity if item.value_per_unit else None,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            }
            for item in items
        ]

    async def add_item(self, item_data: Dict) -> Optional[InventoryItem]:
        """Add a new item to inventory"""
        try:
            # Get market price from Gemini AI
            price = await self.gemini_service.get_market_price(item_data['name'], item_data.get('category'))
            
            # Calculate estimated value
            quantity = float(item_data['quantity'])
            estimated_value = price * quantity if price else None

            # Create new item with value
            new_item = InventoryItem(
                name=item_data['name'],
                quantity=quantity,
                unit=item_data.get('unit', 'kg'),
                category=item_data.get('category', 'other'),
                value_per_unit=price,
                estimated_value=estimated_value
            )
            
            self.db.add(new_item)
            self.db.commit()
            self.db.refresh(new_item)
            return new_item
            
        except Exception as e:
            logger.error(f"Error adding inventory item: {str(e)}")
            self.db.rollback()
            return None

    async def remove_item(self, item_id: int) -> Dict:
        """Remove an item from inventory"""
        try:
            item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")

            self.db.delete(item)
            self.db.commit()

            return {"message": f"Item {item.name} removed successfully"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing inventory item: {str(e)}")
            raise

    async def update_item_quantity(self, item_id: int, quantity: float, operation: str = "set") -> Dict:
        """Update item quantity"""
        try:
            item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")

            if operation == "add":
                item.quantity += quantity
            elif operation == "subtract":
                if item.quantity - quantity < 0:
                    raise ValueError("Cannot reduce quantity below 0")
                item.quantity -= quantity
            else:  # set
                item.quantity = quantity

            # Update estimated value based on new quantity
            item.estimated_value = await self._estimate_value(item.name, item.quantity, item.unit)
            item.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(item)

            return {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "estimated_value": item.estimated_value,
                "updated_at": item.updated_at.isoformat()
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating item quantity: {str(e)}")
            raise

    async def get_analytics(self) -> Dict:
        """Get inventory analytics"""
        try:
            total_items = self.db.query(InventoryItem).count()
            total_value = self.db.query(func.sum(InventoryItem.estimated_value)).scalar() or 0.0
            
            # Calculate health score based on expiration dates and variety
            categories = self.db.query(InventoryItem.category).distinct().count()
            expired_items = self.db.query(ExpirationTracker).filter(
                ExpirationTracker.status == ExpirationStatus.EXPIRED
            ).count()
            
            # Simple health score calculation
            base_score = 100
            category_bonus = min(categories * 5, 25)  # Up to 25 points for variety
            expiry_penalty = min(expired_items * 10, 50)  # Up to 50 points penalty for expired items
            
            health_score = max(0, min(100, base_score + category_bonus - expiry_penalty))
            
            return {
                "total_items": total_items,
                "total_value": round(total_value, 2),
                "health_score": health_score,
                "categories": categories,
                "expired_items": expired_items
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise

    async def _guess_category(self, item_name: str) -> str:
        """Use AI to guess item category based on name"""
        try:
            prompt = f"""
            You are a food category classification AI. Classify this food item into exactly one category:
            Item: {item_name}
            
            Consider these categories:
            - dairy: Milk, cheese, yogurt, butter, etc.
            - produce: Fresh fruits and vegetables
            - meat: All types of meat, poultry, and fish
            - grains: Rice, bread, pasta, cereals
            - beverages: Drinks, juices, sodas
            - spices: Seasonings, herbs, spices
            - snacks: Chips, crackers, nuts
            - condiments: Sauces, dressings, oils
            - canned: Any canned foods
            - frozen: Frozen foods
            - baking: Flour, sugar, baking powder
            - other: Anything that doesn't fit above
            
            Return ONLY a JSON response in this exact format:
            {{
                "category": "one of the categories listed above",
                "confidence": confidence level as a number between 0 and 1,
                "reasoning": "Brief explanation of the classification"
            }}
            """
            
            response = await self.gemini_service.generate_json_content(prompt)
            if response and "category" in response:
                return response["category"].lower()
            
            # Fallback to 'other' if AI fails
            logger.warning(f"AI category prediction failed for {item_name}, falling back to 'other'")
            return "other"
            
        except Exception as e:
            logger.error(f"Error in AI category prediction for {item_name}: {str(e)}")
            return "other"

    async def _estimate_value(self, name: str, quantity: float, unit: str) -> float:
        """Use AI to estimate item value"""
        try:
            prompt = f"""
            You are a grocery price estimation AI. Estimate the current market price for this item:
            Item: {name}
            Quantity: {quantity}
            Unit: {unit}

            Consider:
            - Current market trends
            - Quality level (assume standard quality)
            - Seasonal variations
            - Standard retail prices
            
            Return ONLY a JSON response in this exact format:
            {{
                "estimated_price": price in USD as a number (total price for the given quantity),
                "unit_price": price per unit in USD as a number,
                "confidence": confidence level as a number between 0 and 1,
                "reasoning": "Brief explanation of the estimate"
            }}
            """
            
            response = await self.gemini_service.generate_json_content(prompt)
            if response and "estimated_price" in response:
                return float(response["estimated_price"])
            return 0.0
        except Exception as e:
            logger.error(f"Error estimating value for {name}: {str(e)}")
            return 0.0

    async def suggest_category(self, item_name: str) -> str:
        """Use AI to suggest a category for an item"""
        try:
            # Define existing categories
            existing_categories = [
                "dairy", "produce", "meat", "grains", "beverages", 
                "spices", "snacks", "condiments", "canned", 
                "frozen", "baking", "other"
            ]
            
            # Create prompt for AI
            prompt = f"""
            You are a kitchen inventory expert. Given this food item: "{item_name}", 
            suggest the most appropriate category from this list:
            {', '.join(existing_categories)}

            If none of the existing categories fit well, you may suggest a new category 
            that would be useful for kitchen organization.

            Consider:
            1. Common usage of the item
            2. Storage requirements
            3. Typical shelf location
            4. Food group classification

            Return ONLY the category name, nothing else.
            """
            
            # Get AI suggestion
            response = await self.gemini_service.generate_content(prompt)
            if not response:
                logger.warning(f"No AI response for category suggestion of {item_name}")
                return "other"
            
            # Clean and validate the response
            suggested_category = response.strip().lower()
            
            # If it's a multi-word response, format it appropriately
            suggested_category = suggested_category.replace(" ", "_")
            
            logger.info(f"AI suggested category '{suggested_category}' for item '{item_name}'")
            return suggested_category
            
        except Exception as e:
            logger.error(f"Error suggesting category for {item_name}: {str(e)}")
            return "other"  # Default to 'other' if there's an error

    async def get_category_distribution(self) -> List[Dict]:
        """Get distribution of items by category"""
        try:
            # Query items grouped by category
            items = self.db.query(
                InventoryItem.category,
                func.count(InventoryItem.id).label('count'),
                func.sum(InventoryItem.estimated_value).label('total_value')
            ).group_by(InventoryItem.category).all()
            
            return [
                {
                    "category": item.category or "uncategorized",
                    "count": item.count,
                    "total_value": float(item.total_value or 0)
                }
                for item in items
            ]
        except Exception as e:
            logger.error(f"Error getting category distribution: {str(e)}")
            return []

    async def get_value_history(self, days: int = 30) -> List[Dict]:
        """Get inventory value history"""
        try:
            # Get current date in UTC
            now = datetime.utcnow()
            start_date = now - timedelta(days=days)
            
            # Query items updated within the time range
            items = self.db.query(InventoryItem).filter(
                InventoryItem.updated_at >= start_date
            ).order_by(InventoryItem.updated_at).all()
            
            # Group items by date and calculate total value
            history = {}
            for item in items:
                date_key = item.updated_at.date().isoformat()
                if date_key not in history:
                    history[date_key] = 0
                history[date_key] += (item.estimated_value or 0)
            
            # Fill in missing dates with previous value
            date_range = []
            current_date = start_date
            last_value = 0
            
            while current_date <= now:
                date_key = current_date.date().isoformat()
                value = history.get(date_key, last_value)
                date_range.append({
                    "date": date_key,
                    "value": value
                })
                last_value = value
                current_date += timedelta(days=1)
            
            return date_range
            
        except Exception as e:
            logger.error(f"Error getting value history: {str(e)}")
            return []

    async def get_expiration_summary(self) -> Dict:
        """Get summary of item expiration status"""
        try:
            current_date = datetime.utcnow().date()
            
            # Get counts for different expiration statuses
            result = self.db.query(
                ExpirationTracker.status,
                func.count(ExpirationTracker.id).label('count')
            ).group_by(ExpirationTracker.status).all()
            
            # Get items expiring soon (next 7 days)
            expiring_soon = self.db.query(
                func.count(ExpirationTracker.id)
            ).filter(
                ExpirationTracker.expiration_date.between(
                    current_date,
                    current_date + timedelta(days=7)
                )
            ).scalar() or 0
            
            return {
                "expired": next((r.count for r in result if r.status == ExpirationStatus.EXPIRED), 0),
                "good": next((r.count for r in result if r.status == ExpirationStatus.GOOD), 0),
                "expiring_soon": expiring_soon
            }
        except Exception as e:
            logger.error(f"Error getting expiration summary: {str(e)}")
            return {"expired": 0, "good": 0, "expiring_soon": 0}

    async def _calculate_expiration_status(self, item_name: str, category: str, days_until_expiry: int) -> Dict:
        """Use Gemini AI to calculate intelligent expiration status"""
        try:
            prompt = f"""
            You are an AI food safety expert. Analyze this food item's expiration status:
            Item: {item_name}
            Category: {category}
            Days until expiration: {days_until_expiry}

            Consider:
            1. Typical shelf life for this category
            2. Food safety guidelines
            3. Storage conditions
            4. Type of food

            Return ONLY a JSON response in this format:
            {{
                "status": "GOOD" or "EXPIRING_SOON" or "EXPIRED",
                "confidence": number between 0 and 1,
                "recommended_action": "brief action recommendation",
                "storage_tip": "brief storage tip"
            }}
            """
            
            response = await self.gemini_service.generate_json_content(prompt)
            if response and "status" in response:
                return response
            return {"status": "GOOD", "confidence": 1.0, "recommended_action": "", "storage_tip": ""}
            
        except Exception as e:
            logger.error(f"Error calculating expiration status: {str(e)}")
            return {"status": "GOOD", "confidence": 1.0, "recommended_action": "", "storage_tip": ""}

    async def get_expiring_items(self, days_threshold: int = 7) -> List[Dict]:
        """Get items that are expiring soon with intelligent status"""
        try:
            current_date = datetime.utcnow().date()
            expiring_items = []
            
            # Get all items with expiration tracking
            items = self.db.query(InventoryItem, ExpirationTracker).join(
                ExpirationTracker
            ).all()
            
            for item, tracker in items:
                # Calculate days until expiration
                days_until_expiry = (tracker.expiration_date - current_date).days
                
                # Get intelligent status from AI
                status_info = await self._calculate_expiration_status(
                    item.name,
                    item.category,
                    days_until_expiry
                )
                
                expiring_items.append({
                    "id": item.id,
                    "name": item.name,
                    "expiration_date": tracker.expiration_date.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "status": status_info["status"],
                    "recommended_action": status_info.get("recommended_action", ""),
                    "storage_tip": status_info.get("storage_tip", "")
                })
            
            return sorted(expiring_items, key=lambda x: x["days_until_expiry"])
            
        except Exception as e:
            logger.error(f"Error getting expiring items: {str(e)}")
            return []

    async def get_total_value(self) -> float:
        """Get total inventory value"""
        try:
            items = self.db.query(InventoryItem).all()
            total = 0.0
            for item in items:
                if item.value_per_unit:
                    total += item.value_per_unit * item.quantity
            return total
        except Exception as e:
            logger.error(f"Error calculating total value: {str(e)}")
            return 0.0