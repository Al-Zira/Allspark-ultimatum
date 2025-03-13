# Financial Forecast API

A powerful financial analysis API that provides stock data, risk metrics, machine learning predictions, and AI-driven market analysis.

## Project Structure

```
financial_forecast/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py      # FastAPI application and endpoints
│   │   ├── models.py    # Pydantic models for data validation
│   │   └── utils.py     # Utility functions for calculations
│   ├── Dockerfile       # Backend Docker configuration
│   └── requirements.txt # Backend dependencies
├── frontend/
│   ├── app.py          # Streamlit dashboard (example)
│   └── requirements.txt # Frontend dependencies
├── docker-compose.yml  # Docker services configuration
└── README.md
```

## Features

- Real-time financial data retrieval
- Advanced risk metrics calculation
- Machine learning-based price predictions
- AI-powered market analysis
- RESTful API endpoints
- Example Streamlit dashboard
- Containerized backend service

## Setup

### Using Docker (Recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd financial_forecast
```

2. Create a `.env` file in the root directory:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. Build and start the services:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Manual Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd financial_forecast
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Install frontend dependencies (optional):

```bash
cd frontend
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Running the Application

### Using Docker

Start all services:

```bash
docker-compose up
```

Start only the backend:

```bash
docker-compose up backend
```

Stop all services:

```bash
docker-compose down
```

View logs:

```bash
docker-compose logs -f backend
```

### Manual Setup

1. Start the FastAPI backend:

```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the Streamlit frontend (optional):

```bash
cd frontend
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## API Documentation

### Endpoints

1. **Get Financial Data**

```bash
GET /financial-data/{symbol}
```

Parameters:

- `symbol`: Stock symbol (e.g., "AAPL")
- `period`: Time period (default: "2y")

Response:

```json
[
    {
        "date": "2024-01-03T00:00:00",
        "open": 184.22,
        "high": 185.88,
        "low": 183.43,
        "close": 184.25,
        "volume": 58414500
    },
    ...
]
```

2. **Get Risk Metrics**

```bash
GET /risk-metrics/{symbol}
```

Parameters:

- `symbol`: Stock symbol
- `period`: Time period

Response:

```json
{
  "metrics": {
    "value_at_risk": -0.0217,
    "conditional_var": -0.0288,
    "sharpe_ratio": 1.2476,
    "max_drawdown": -0.1546
  },
  "chart_data": {
    "title": "Risk Metrics",
    "x_label": "Metric",
    "y_label": "Value",
    "labels": [
      "Value at Risk",
      "Conditional VaR",
      "Sharpe Ratio",
      "Max Drawdown"
    ],
    "values": [-0.0217, -0.0288, 1.2476, -0.1546]
  }
}
```

3. **Get ML Prediction**

```bash
GET /ml-prediction/{symbol}
```

Parameters:

- `symbol`: Stock symbol
- `period`: Time period

Response:

```json
{
    "prediction": {
        "forecast_values": [...],
        "feature_importance": {
            "ma_10": 0.9254,
            "ma_50": 0.0589,
            "rsi": 0.0118,
            "volume": 0.0039
        },
        "data_points": 240,
        "last_price": 242.68
    },
    "chart_data": {
        "title": "ML Price Forecast (30 Days)",
        "x_label": "Days",
        "y_label": "Price",
        "data": {
            "forecast": [...]
        }
    }
}
```

4. **Get AI Prediction**

```bash
GET /ai-prediction/{symbol}
```

Parameters:

- `symbol`: Stock symbol
- `period`: Time period
- `context`: Analysis context
- `asset_type`: Type of asset

Response:

```json
{
    "prediction": {
        "trend": "Strong upward trend with recent gains",
        "factors": [...],
        "risks": [...],
        "opportunities": [...],
        "forecast": {
            "month1": 5.0,
            "month2": 4.0,
            "month3": 3.5
        }
    },
    "chart_data": {
        "title": "Price Change Forecast (%)",
        "x_label": "Time Period",
        "y_label": "Expected Change (%)",
        "data": {
            "forecast": [5.0, 4.0, 3.5]
        },
        "labels": ["1 Month", "2 Months", "3 Months"]
    }
}
```

## Python Usage Example

```python
import requests

def get_stock_analysis(symbol: str, period: str = "1y"):
    base_url = "http://localhost:8000"

    # Get financial data
    financial_data = requests.get(f"{base_url}/financial-data/{symbol}",
                                params={"period": period}).json()

    # Get risk metrics
    risk_metrics = requests.get(f"{base_url}/risk-metrics/{symbol}",
                              params={"period": period}).json()

    # Get ML prediction
    ml_prediction = requests.get(f"{base_url}/ml-prediction/{symbol}",
                               params={"period": period}).json()

    # Get AI prediction
    ai_prediction = requests.get(f"{base_url}/ai-prediction/{symbol}",
                               params={"period": period,
                                     "context": f"Analyze {symbol} stock performance",
                                     "asset_type": "Stock"}).json()

    return {
        "financial_data": financial_data,
        "risk_metrics": risk_metrics,
        "ml_prediction": ml_prediction,
        "ai_prediction": ai_prediction
    }

# Use the function
analysis = get_stock_analysis("AAPL", "1y")
```

## Dependencies

### Backend

- fastapi
- uvicorn
- pandas
- numpy
- yfinance
- scikit-learn
- xgboost
- python-dotenv
- google-generativeai
- pydantic

### Frontend (Optional)

- streamlit
- pandas
- plotly
- requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
