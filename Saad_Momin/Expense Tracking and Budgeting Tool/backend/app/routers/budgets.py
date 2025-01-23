from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/", response_model=schemas.Budget)
def create_or_update_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    db_budget = db.query(models.Budget).filter(models.Budget.category == budget.category).first()
    if db_budget:
        for key, value in budget.dict().items():
            setattr(db_budget, key, value)
    else:
        db_budget = models.Budget(**budget.dict())
        db.add(db_budget)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/", response_model=List[schemas.Budget])
def get_budgets(db: Session = Depends(get_db)):
    return db.query(models.Budget).all()

@router.get("/alerts", response_model=List[schemas.BudgetAlert])
def get_budget_alerts(db: Session = Depends(get_db)):
    # Get all budgets
    budgets = db.query(models.Budget).all()
    if not budgets:
        return []
    
    # Get current month's expenses
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    expenses = db.query(models.Expense).filter(models.Expense.date >= start_date).all()
    
    # Calculate spending by category
    expense_df = pd.DataFrame([(e.category, e.amount) for e in expenses], columns=['category', 'amount'])
    category_spending = expense_df.groupby('category')['amount'].sum().to_dict()
    
    alerts = []
    for budget in budgets:
        spent = category_spending.get(budget.category, 0)
        percentage = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
        
        status = "On Track"
        if percentage >= 90:
            status = "Critical"
        elif percentage >= 75:
            status = "Warning"
        
        alerts.append(schemas.BudgetAlert(
            category=budget.category,
            budget=budget.monthly_limit,
            spent=spent,
            percentage=percentage,
            status=status
        ))
    
    return alerts

@router.delete("/{category}")
def delete_budget(category: str, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.category == category).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"} 