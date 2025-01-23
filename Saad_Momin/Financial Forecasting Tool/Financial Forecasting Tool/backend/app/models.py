from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class FinancialData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class RiskMetrics(BaseModel):
    value_at_risk: float
    conditional_var: float
    sharpe_ratio: float
    max_drawdown: float

class MLPrediction(BaseModel):
    forecast_values: List[float]
    feature_importance: Dict[str, float]
    data_points: int
    last_price: float

class AIPrediction(BaseModel):
    trend: str
    factors: List[str]
    risks: List[str]
    opportunities: List[str]
    forecast: Dict[str, float]
    current_price: float
    price_change: float
    volatility: float

class ChartData(BaseModel):
    title: str
    x_label: str
    y_label: str
    data: Dict[str, List[float]] 