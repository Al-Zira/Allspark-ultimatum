# Mindful Moments App

A mindfulness and meditation application with a FastAPI backend and Streamlit frontend.

## Project Structure

```
.
├── backend/
│   └── app/
│       ├── main.py          # FastAPI application
│       ├── database.py      # Database operations
│       ├── models.py        # Pydantic models
│       └── requirements.txt # Backend dependencies
├── frontend/
│   └── app/
│       ├── main.py          # Streamlit application
│       └── requirements.txt # Frontend dependencies
└── README.md
```

## Setup and Installation

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend/app
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The backend API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:

   ```bash
   cd frontend/app
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run main.py
   ```

The frontend will be available at `http://localhost:8501`.

## Features

- Personalized mindfulness activities based on mood, energy level, and interests
- Custom routine creation and management
- Progress tracking with statistics
- Stress relief and sleep practice generators
- User-friendly interface with Streamlit
- RESTful API backend with FastAPI

## API Endpoints

- `GET /users/{user_id}/stats` - Get user statistics
- `GET /users/{user_id}/routines` - Get user's saved routines
- `POST /users/{user_id}/routines` - Create a new routine
- `GET /users/{user_id}/mood` - Get user's mood data
- `POST /users/{user_id}/mood` - Record mood data
- `POST /users/{user_id}/activities` - Create a new activity
- `POST /generate-activity` - Generate personalized activity
- `POST /generate-stress-relief` - Generate stress relief practice
- `POST /generate-sleep-practice` - Generate sleep practice

## Development

The project is split into two main components:

1. **Backend (FastAPI)**

   - Handles data persistence
   - Provides RESTful API endpoints
   - Manages business logic
   - Generates mindfulness activities

2. **Frontend (Streamlit)**
   - Provides user interface
   - Communicates with backend API
   - Handles user interactions
   - Displays progress and statistics

## Note

Make sure both the backend and frontend servers are running simultaneously for the application to work properly. The frontend depends on the backend API being available at `http://localhost:8000`.
