from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import FinancialData, RiskMetrics, MLPrediction, AIPrediction, ChartData
from .utils import (
    load_financial_data,
    calculate_risk_metrics,
    ml_enhanced_prediction,
    get_ai_prediction
)
from typing import List, Dict
import pandas as pd
from datetime import datetime

app = FastAPI(title="Financial Forecast API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Financial Forecast API is running"}

@app.get("/financial-data/{symbol}")
async def get_financial_data(symbol: str, period: str = "2y") -> List[dict]:
    try:
        df = load_financial_data(symbol, period)
        # Convert DataFrame to list of dictionaries with proper formatting
        records = []
        for index, row in df.reset_index().iterrows():
            record = {
                "date": row["Date"].isoformat(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            }
            records.append(record)
        return records
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/risk-metrics/{symbol}")
async def get_risk_metrics(symbol: str, period: str = "2y") -> Dict:
    try:
        df = load_financial_data(symbol, period)
        metrics = calculate_risk_metrics(df)
        
        # Create chart data for risk metrics
        chart_data = {
            "title": "Risk Metrics",
            "x_label": "Metric",
            "y_label": "Value",
            "metrics": metrics,
            "labels": ["Value at Risk", "Conditional VaR", "Sharpe Ratio", "Max Drawdown"],
            "values": [
                metrics["value_at_risk"],
                metrics["conditional_var"],
                metrics["sharpe_ratio"],
                metrics["max_drawdown"]
            ]
        }
        
        return {
            "metrics": metrics,
            "chart_data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ml-prediction/{symbol}")
async def get_ml_prediction(symbol: str, period: str = "2y") -> Dict:
    try:
        df = load_financial_data(symbol, period)
        prediction = ml_enhanced_prediction(df)
        
        # Create chart data for ML prediction
        chart_data = {
            "title": "ML Price Forecast (30 Days)",
            "x_label": "Days",
            "y_label": "Price",
            "data": {
                "forecast": prediction["forecast_values"]
            }
        }
        
        return {
            "prediction": prediction,
            "chart_data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ai-prediction/{symbol}")
async def get_ai_prediction_endpoint(
    symbol: str,
    period: str = "2y",
    context: str = "",
    asset_type: str = "Stock"
) -> Dict:
    try:
        df = load_financial_data(symbol, period)
        prediction = get_ai_prediction(df, context, asset_type)
        
        # Extract forecast values and create labels
        forecast_values = list(prediction["forecast"].values())
        forecast_labels = ["1 Month", "2 Months", "3 Months"]
        
        # Create chart data for price forecast
        chart_data = {
            "title": "Price Change Forecast (%)",
            "x_label": "Time Period",
            "y_label": "Expected Change (%)",
            "data": {
                "forecast": [float(x) for x in forecast_values]  # Ensure values are Python floats
            },
            "labels": forecast_labels
        }
        
        return {
            "prediction": prediction,
            "chart_data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 