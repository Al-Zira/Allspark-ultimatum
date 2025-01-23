# AI Speech Outline Generator

This project is split into two parts: a FastAPI backend and a Streamlit frontend. The backend handles the speech outline generation logic using Google's Gemini AI, while the frontend provides a user-friendly interface.

## Project Structure
```
.
├── backend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
└── README.md
```

## Setup

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
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

4. Create a `.env` file in the backend directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
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

4. Start the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

## Usage
1. Make sure both the backend and frontend servers are running
2. Open your browser and go to `http://localhost:8501` to access the Streamlit interface
3. Fill in the speech parameters and click "Generate Outline"
4. The generated outline will be displayed and available for download

## Features
- Multiple language support
- Customizable speech parameters
- Download generated outlines
- Speech statistics
- Modern, user-friendly interface

## API Endpoints
- `POST /generate-outline`: Generate a speech outline
- `GET /health`: Check API health status