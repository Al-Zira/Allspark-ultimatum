# Smart Budget Tracker

A comprehensive budget tracking application with AI-powered insights using FastAPI backend and Streamlit frontend.

## Features

- Expense tracking with AI-suggested categorization
- Budget management with alerts
- Interactive dashboard with spending visualizations
- AI-powered financial insights and recommendations
- Monthly spending trends and category distribution

## Project Structure

```
budget_tracker/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── expenses.py
│   │   │   ├── budgets.py
│   │   │   └── insights.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── ai_insights.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── utils/
│   │   │   └── api_client.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
└── README.md
```

## API Endpoints

### Base Endpoint

```bash
GET / - Welcome message
```

### Expense Endpoints

```bash
# Create new expense
POST /expenses/
{
    "date": "2025-01-06T00:00:00",
    "amount": 100.00,
    "description": "Test Expense",
    "category": "FOOD"
}

# Get all expenses (with optional filters)
GET /expenses/
Query params:
- start_date: datetime
- end_date: datetime
- category: string

# Get expense statistics
GET /expenses/stats
Query params:
- start_date: datetime
- end_date: datetime

# Get category distribution
GET /expenses/distribution

# Get monthly spending trend
GET /expenses/monthly-trend
```

### Budget Endpoints

```bash
# Create or update budget
POST /budgets/
{
    "category": "FOOD",
    "monthly_limit": 500.00
}

# Get all budgets
GET /budgets/

# Get budget alerts
GET /budgets/alerts

# Delete budget
DELETE /budgets/{category}
```

### AI Insights Endpoints

```bash
# Get AI spending analysis
GET /insights/spending-analysis

# Get AI category suggestion
GET /insights/suggest-category
Query params:
- description: string
- amount: float

# Get AI budget recommendations
GET /insights/budget-recommendations
```

## Setup Instructions

### Option 1: Docker Setup (Recommended for Backend)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:

```bash
git clone <repository-url>
cd budget_tracker
```

3. Create a `.env` file in the root directory:

```bash
GOOGLE_API_KEY=your_gemini_api_key
```

4. Build and start the backend container:

```bash
docker-compose up --build -d
```

The backend API will be available at `http://localhost:8000`

To view logs:

```bash
docker-compose logs -f
```

To stop the container:

```bash
docker-compose down
```

### Option 2: Local Setup

1. Clone the repository

```bash
git clone <repository-url>
cd budget_tracker
```

2. Set up environment variables:

Backend `.env`:

```
DATABASE_URL=sqlite:///./expenses.db
GOOGLE_API_KEY=your_gemini_api_key
```

Frontend `.env`:

```
API_BASE_URL=http://127.0.0.1:8000
```

3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Install frontend dependencies:

```bash
cd frontend
pip install -r requirements.txt
```

5. Run the application:

Start backend:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start frontend:

```bash
cd frontend
streamlit run app/main.py
```

## Dependencies

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Google Generative AI
- Pandas
- Python-dotenv

### Frontend

- Streamlit
- Plotly
- Requests
- Python-dotenv
- Pandas

## Features in Detail

### Dashboard

- Total spending overview
- Average transaction analysis
- Monthly spending trends
- Category distribution visualization
- Budget alerts with status indicators

### Expense Management

- Add expenses with AI-suggested categories
- View and filter expenses by date and category
- Automatic date handling and validation

### Budget Management

- Set and update category budgets
- View current budgets and spending
- Delete existing budgets
- Real-time budget alerts

### AI Insights

- Spending pattern analysis
- Smart category suggestions
- Budget recommendations
- Financial advice and tips

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Development

### Backend Container Management

1. Rebuild the container after changes:

```bash
docker-compose build backend
docker-compose up -d
```

2. View container logs:

```bash
docker-compose logs -f backend
```

3. Access container shell:

```bash
docker-compose exec backend bash
```

4. Check container status:

```bash
docker-compose ps
```

### Data Persistence

The backend container uses Docker volumes for data persistence:

- Database files are stored in the `backend_data` volume
- Source code changes are immediately reflected due to volume mounting

### Container Health Monitoring

The backend container includes health checks that:

- Monitor the API endpoint every 30 seconds
- Mark container as unhealthy if the endpoint is unreachable
- Automatically restart the container if needed
