from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ExpenseBase(BaseModel):
    date: datetime = Field(default_factory=datetime.now)
    amount: float
    description: str
    category: str

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    category: str
    monthly_limit: float

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExpenseStats(BaseModel):
    total_spending: float
    average_transaction: float
    total_transactions: int

class CategoryDistribution(BaseModel):
    category: str
    amount: float
    percentage: float

class BudgetAlert(BaseModel):
    category: str
    budget: float
    spent: float
    percentage: float
    status: str

class DashboardData(BaseModel):
    stats: ExpenseStats
    monthly_trend: List[dict]
    category_distribution: List[CategoryDistribution]
    budget_alerts: List[BudgetAlert] 