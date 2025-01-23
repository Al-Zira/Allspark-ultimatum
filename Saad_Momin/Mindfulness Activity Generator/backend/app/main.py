from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
from datetime import datetime

from database import Database
from models import (
    Activity, ActivityCreate,
    Routine, RoutineCreate,
    MoodData, UserStats, UserProfile
)
from activity_generator import MindfulnessActivityGenerator

app = FastAPI(title="Mindful Moments API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and activity generator
db = Database()
generator = MindfulnessActivityGenerator()

@app.get("/")
async def root():
    return {"message": "Welcome to Mindful Moments API"}

@app.get("/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: int):
    return db.get_user_stats(user_id)

@app.get("/users/{user_id}/routines", response_model=List[Routine])
async def get_user_routines(user_id: int):
    routines = db.get_user_routines(user_id)
    # Add user_id to each routine
    for routine in routines:
        routine['user_id'] = user_id
    return routines

@app.post("/users/{user_id}/routines", response_model=Routine)
async def create_routine(user_id: int, routine: RoutineCreate):
    routine_dict = routine.dict()
    routine_dict['user_id'] = user_id
    db.save_routine(user_id, routine_dict)
    return {
        **routine_dict,
        "id": 1,
        "user_id": user_id,
        "created_at": datetime.now(),
        "last_practiced": None,
        "practice_count": 0
    }

@app.get("/users/{user_id}/mood", response_model=dict)
async def get_mood_data(user_id: int, days: Optional[int] = 30):
    return db.get_mood_data(user_id, days)

@app.post("/users/{user_id}/mood")
async def record_mood(user_id: int, mood_data: MoodData):
    # Implementation for recording mood data
    return {"status": "success"}

@app.post("/users/{user_id}/activities", response_model=Activity)
async def create_activity(user_id: int, activity: ActivityCreate):
    activity_dict = activity.dict()
    activity_id = db.save_activity(user_id, activity_dict)
    return {
        **activity_dict,
        "id": activity_id,
        "user_id": user_id,
        "created_at": datetime.now(),
        "completed": False
    }

@app.post("/generate-activity")
async def generate_activity(
    mood: str,
    energy_level: int,
    stress_level: int,
    time_available: int,
    interests: str
):
    # Convert interests string to list
    interests_list = interests.split(',') if interests else ["Meditation"]
    
    user_profile = {
        'mood': mood,
        'energy_level': energy_level,
        'stress_level': stress_level,
        'time_available': time_available,
        'interests': interests_list
    }
    
    activity = generator.generate_personalized_activity(
        user_profile=user_profile,
        mood=mood,
        energy_level=energy_level,
        stress_level=stress_level,
        time_available=time_available,
        interests=interests_list
    )
    
    return {
        "category": "Personalized Practice",
        "text": activity['text'] if isinstance(activity, dict) else activity,
        "duration": time_available
    }

@app.post("/generate-stress-relief")
async def generate_stress_relief(stress_trigger: str, stress_level: int):
    practice = generator.generate_stress_relief_practice(stress_trigger, stress_level)
    return {"practice": practice}

@app.post("/generate-sleep-practice")
async def generate_sleep_practice(sleep_quality: str, stress_level: int):
    practice = generator.generate_sleep_recommendation(sleep_quality, stress_level)
    return {"practice": practice}

@app.post("/users/{user_id}/activities/{activity_id}/complete")
async def complete_activity(
    user_id: int,
    activity_id: int,
    mood_after: Optional[str] = None
):
    """Complete an activity and record it in practice history."""
    if db.complete_activity(user_id, activity_id, mood_after):
        return {"status": "success"}
    raise HTTPException(status_code=400, message="Failed to complete activity")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 