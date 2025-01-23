from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from .. import models
from ..ai_insights import AIFinancialInsights

router = APIRouter(prefix="/insights", tags=["insights"])
ai_insights = AIFinancialInsights()

@router.get("/spending-analysis")
async def get_spending_insights(db: Session = Depends(get_db)):
    """Get AI-powered insights about spending patterns"""
    try:
        expenses = db.query(models.Expense).all()
        budgets = db.query(models.Budget).all()
        
        # Convert SQLAlchemy objects to dictionaries
        expense_data = [
            {
                "date": expense.date.isoformat(),
                "amount": expense.amount,
                "category": expense.category,
                "description": expense.description
            }
            for expense in expenses
        ]
        
        budget_data = [
            {
                "category": budget.category,
                "monthly_limit": budget.monthly_limit
            }
            for budget in budgets
        ]
        
        insights = ai_insights.get_spending_insights(expense_data, budget_data)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest-category")
async def suggest_category(description: str, amount: float, db: Session = Depends(get_db)):
    """Get AI suggestion for expense category"""
    try:
        # Get existing categories from expenses and budgets
        expense_categories = db.query(models.Expense.category).distinct().all()
        budget_categories = db.query(models.Budget.category).distinct().all()
        
        # Combine and deduplicate categories
        existing_categories = list(set(
            [cat[0] for cat in expense_categories] +
            [cat[0] for cat in budget_categories]
        ))
        
        suggested_category = ai_insights.suggest_category(
            description=description,
            amount=amount,
            existing_categories=existing_categories
        )
        
        return {"suggested_category": suggested_category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budget-recommendations")
async def get_budget_recommendations(db: Session = Depends(get_db)):
    """Get AI-powered budget recommendations"""
    try:
        expenses = db.query(models.Expense).all()
        current_budgets = db.query(models.Budget).all()
        
        # Convert SQLAlchemy objects to dictionaries
        expense_data = [
            {
                "date": expense.date.isoformat(),
                "amount": expense.amount,
                "category": expense.category,
                "description": expense.description
            }
            for expense in expenses
        ]
        
        budget_data = [
            {
                "category": budget.category,
                "monthly_limit": budget.monthly_limit
            }
            for budget in current_budgets
        ]
        
        recommendations = ai_insights.get_budget_recommendations(expense_data, budget_data)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 