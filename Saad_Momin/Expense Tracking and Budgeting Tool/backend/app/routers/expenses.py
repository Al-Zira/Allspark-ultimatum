from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)

@router.post("/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/", response_model=List[schemas.Expense])
def get_expenses(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Expense)
    
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if category:
        query = query.filter(models.Expense.category == category)
    
    return query.all()

@router.get("/stats", response_model=schemas.ExpenseStats)
async def get_expense_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Expense)
    
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    
    expenses = query.all()
    if not expenses:
        return schemas.ExpenseStats(
            total_spending=0,
            average_transaction=0,
            total_transactions=0
        )
    
    total = sum(expense.amount for expense in expenses)
    return schemas.ExpenseStats(
        total_spending=total,
        average_transaction=total / len(expenses),
        total_transactions=len(expenses)
    )

@router.get("/distribution", response_model=List[schemas.CategoryDistribution])
async def get_category_distribution(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    if not expenses:
        return []
    
    df = pd.DataFrame([(e.category, e.amount) for e in expenses], columns=['category', 'amount'])
    total = df['amount'].sum()
    distribution = df.groupby('category')['amount'].sum().reset_index()
    
    return [
        schemas.CategoryDistribution(
            category=row['category'],
            amount=float(row['amount']),
            percentage=float((row['amount'] / total) * 100)
        )
        for _, row in distribution.iterrows()
    ]

@router.get("/monthly-trend")
async def get_monthly_trend(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    if not expenses:
        return []
    
    df = pd.DataFrame([(e.date, e.amount) for e in expenses], columns=['date', 'amount'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    monthly = df.groupby('month')['amount'].sum().reset_index()
    
    return monthly.to_dict('records') 