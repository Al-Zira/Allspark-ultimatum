from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import expenses, budgets, insights

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budget Tracker API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses.router)
app.include_router(budgets.router)
app.include_router(insights.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Budget Tracker API"} 