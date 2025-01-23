# AI Kitchen Inventory Manager (Separated Backend & Frontend)

## Project Structure

The project is now separated into two main components:

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── models/           # Database models
│   ├── core/             # Core business logic
│   ├── services/         # External service integrations
│   ├── ai/              # AI-related functionality
│   └── config/          # Configuration files
└── requirements.txt     # Backend dependencies
```

### Frontend (Streamlit)

```
frontend/
├── app/
│   ├── main.py          # Streamlit application
│   ├── pages/           # Additional pages
│   ├── components/      # Reusable UI components
│   └── utils/           # Utility functions
└── requirements.txt    # Frontend dependencies
```

## Features

- **Inventory Management**: Add, view, and manage kitchen inventory items
- **AI Price Estimation**: Uses AI to estimate market value of items
- **Expiration Tracking**: Monitors expiration dates and alerts
- **Meal Planning**: Suggests meal ideas based on available ingredients
- **Shopping Recommendations**: Provides smart shopping lists
- **Data Visualization**: Visual insights into inventory status

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the Streamlit application:
   ```bash
   streamlit run app/main.py
   ```
   The web interface will be available at http://localhost:8501

## API Endpoints

### Inventory Management

#### Get All Items

- **GET** `/api/inventory`
- Returns a list of all inventory items
- Response includes: id, name, quantity, unit, category, value_per_unit, total_value, created_at, updated_at

#### Add New Item

- **POST** `/api/inventory`
- Add a new item to inventory
- Request Body (JSON):
  ```json
  {
    "name": "string",
    "quantity": float,
    "unit": "string",
    "category": "string",
    "expiration_date": "YYYY-MM-DDTHH:MM:SS" (optional)
  }
  ```

#### Update Item Quantity

- **PUT** `/api/inventory/{item_id}/quantity`
- Update quantity of an existing item
- Query Parameters:
  - `quantity`: float (new quantity value)
  - `operation`: string (one of: "set", "add", "subtract")

#### Delete Item

- **DELETE** `/api/inventory/{item_id}`
- Remove an item from inventory

### Analytics and Charts

#### Get Inventory Analytics

- **GET** `/api/inventory/analytics`
- Returns overall inventory statistics
- Response includes: total_items, total_value, health_score

#### Get Category Distribution

- **GET** `/api/inventory/charts/category-distribution`
- Returns distribution of items by category
- Response includes count and total value per category

#### Get Value History

- **GET** `/api/inventory/charts/value-history`
- Query Parameters:
  - `days`: int (number of days of history, default: 30)
- Returns inventory value history over time

#### Get Expiration Summary

- **GET** `/api/inventory/charts/expiration-summary`
- Returns summary of item expiration status

### AI-Powered Features

#### Get Recommendations

- **GET** `/api/recommendations`
- Query Parameters (all optional):
  - `dietary`: string (dietary restrictions)
  - `cuisine`: string (preferred cuisine type)
  - `difficulty`: string (cooking difficulty level)
  - `time`: int (available cooking time in minutes)
- Returns meal and shopping recommendations

#### Clear Recommendation Context

- **POST** `/api/recommendations/clear-context`
- Clears the recommendation system's context

#### Get Expiring Items

- **GET** `/api/expiring-items`
- Query Parameters:
  - `days_threshold`: int (days threshold for expiration warning, default: 7)
- Returns items nearing expiration

#### Suggest Category

- **GET** `/api/category/suggest`
- Query Parameters:
  - `item_name`: string (name of the item to categorize)
- Returns AI-suggested category for an item

#### Get Market Price

- **GET** `/api/market-price`
- Query Parameters:
  - `item_name`: string (name of the item)
  - `category`: string (optional, category of the item)
- Returns AI-estimated market price for an item

### Example Usage with curl

```bash
# Add new item
curl -X POST "http://localhost:8000/api/inventory" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tomatoes", "quantity": 5, "unit": "kg", "category": "produce"}'

# Get inventory
curl http://localhost:8000/api/inventory

# Update quantity
curl -X PUT "http://localhost:8000/api/inventory/1/quantity?quantity=7&operation=set"

# Delete item
curl -X DELETE http://localhost:8000/api/inventory/1

# Get analytics
curl http://localhost:8000/api/inventory/analytics

# Get recommendations
curl "http://localhost:8000/api/recommendations?cuisine=italian&time=30"
```

## Environment Variables

Create `.env` files in both backend and frontend directories with the following variables:

### Backend `.env`:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### Frontend `.env`:

```
API_URL=http://localhost:8000/api
```

## License

This project is licensed under the MIT License.
