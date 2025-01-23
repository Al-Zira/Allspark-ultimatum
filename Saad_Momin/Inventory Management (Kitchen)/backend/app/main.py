from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn

from app.core.database import get_db, init_db, migrate_db
from app.models.inventory import InventoryItem
from app.core.inventory_service import InventoryService
from app.core.expiration_service import ExpirationService
from app.core.recommendation_service import RecommendationService
from app.ai.gemini_service import GeminiService

app = FastAPI(title="AI Kitchen Manager API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and run migrations
@app.on_event("startup")
async def startup_event():
    init_db()
    migrate_db()

# Routes
@app.get("/")
async def root():
    return {"message": "AI Kitchen Manager API"}

@app.get("/api/inventory")
async def get_inventory(db: Session = Depends(get_db)):
    inventory_service = InventoryService(db)
    return await inventory_service.get_all_items()

@app.post("/api/inventory")
async def add_item(
    item_data: Dict = Body(..., description="Item data including name, quantity, unit, category, and optional expiration_date"),
    db: Session = Depends(get_db)
):
    try:
        inventory_service = InventoryService(db)
        return await inventory_service.add_item(item_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/inventory/{item_id}")
async def remove_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    try:
        inventory_service = InventoryService(db)
        return await inventory_service.remove_item(item_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/inventory/{item_id}/quantity")
async def update_quantity(
    item_id: int,
    quantity: float = Query(..., description="New quantity value"),
    operation: str = Query("set", description="Operation: set, add, or subtract"),
    db: Session = Depends(get_db)
):
    try:
        inventory_service = InventoryService(db)
        return await inventory_service.update_item_quantity(item_id, quantity, operation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/analytics")
async def get_inventory_analytics(db: Session = Depends(get_db)):
    """Get inventory analytics"""
    try:
        inventory_service = InventoryService(db)
        total_value = await inventory_service.get_total_value()
        
        return {
            "total_items": db.query(InventoryItem).count(),
            "total_value": total_value,
            "health_score": 100  # Placeholder for health score calculation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/charts/category-distribution")
async def get_category_distribution(db: Session = Depends(get_db)):
    """Get distribution of items by category for charts"""
    inventory_service = InventoryService(db)
    return await inventory_service.get_category_distribution()

@app.get("/api/inventory/charts/value-history")
async def get_value_history(
    days: int = Query(30, description="Number of days of history to return"),
    db: Session = Depends(get_db)
):
    """Get inventory value history for charts"""
    inventory_service = InventoryService(db)
    return await inventory_service.get_value_history(days)

@app.get("/api/inventory/charts/expiration-summary")
async def get_expiration_summary(db: Session = Depends(get_db)):
    """Get summary of item expiration status for charts"""
    inventory_service = InventoryService(db)
    return await inventory_service.get_expiration_summary()

@app.get("/api/recommendations")
async def get_recommendations(
    dietary: Optional[str] = Query(None, description="Dietary restrictions"),
    cuisine: Optional[str] = Query(None, description="Preferred cuisine type"),
    difficulty: Optional[str] = Query(None, description="Cooking difficulty level"),
    time: Optional[int] = Query(None, description="Available cooking time in minutes"),
    db: Session = Depends(get_db)
):
    recommendation_service = RecommendationService(db)
    
    # Build preferences dict if any preferences are provided
    preferences = {}
    if dietary:
        preferences["dietary"] = dietary
    if cuisine:
        preferences["cuisine"] = cuisine
    if difficulty:
        preferences["difficulty"] = difficulty
    if time:
        preferences["time"] = time
    
    return await recommendation_service.get_recommendations(
        user_preferences=preferences if preferences else None
    )

@app.post("/api/recommendations/clear-context")
async def clear_recommendation_context(db: Session = Depends(get_db)):
    recommendation_service = RecommendationService(db)
    recommendation_service.clear_context()
    return {"message": "Recommendation context cleared"}

@app.get("/api/expiring-items")
async def get_expiring_items(
    days_threshold: int = Query(7, description="Days threshold for expiration warning"),
    db: Session = Depends(get_db)
):
    expiration_service = ExpirationService(db)
    return await expiration_service.get_expiring_items(days_threshold)

@app.get("/api/category/suggest")
async def suggest_category(
    item_name: str = Query(..., description="Name of the item to categorize"),
    db: Session = Depends(get_db)
):
    """Get AI suggestion for item category"""
    try:
        inventory_service = InventoryService(db)
        category = await inventory_service.suggest_category(item_name)
        return {"category": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-price")
async def get_market_price(
    item_name: str = Query(..., description="Name of the item to get price for"),
    category: Optional[str] = Query(None, description="Category of the item"),
    db: Session = Depends(get_db)
):
    """Get current market price for an item using Gemini AI"""
    try:
        gemini_service = GeminiService()
        price = await gemini_service.get_market_price(item_name, category)
        if price is not None:
            return {"price": price}
        raise HTTPException(status_code=404, detail="Could not determine price for item")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 