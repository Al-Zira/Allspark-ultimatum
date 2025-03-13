from pydantic import BaseModel
from typing import List, Optional, Dict, Union
from datetime import datetime

class ActivityBase(BaseModel):
    text: str
    category: str
    duration: int
    mood_before: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    user_id: int
    rating: Optional[int] = None
    mood_after: Optional[str] = None
    feedback: Optional[str] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime
    routine_id: Optional[int] = None

    class Config:
        from_attributes = True

class RoutineBase(BaseModel):
    name: str
    steps: List[str]
    duration: int
    category: Optional[str] = "Custom"
    description: Optional[str] = ""

class RoutineCreate(RoutineBase):
    pass

class Routine(RoutineBase):
    id: int
    user_id: int
    created_at: datetime
    last_practiced: Optional[datetime] = None
    practice_count: int = 0

    class Config:
        from_attributes = True

class MoodData(BaseModel):
    mood: str
    energy_level: int
    stress_level: int
    notes: Optional[str] = None

class ProgressData(BaseModel):
    date: str
    minutes: int

class UserStats(BaseModel):
    total_minutes: int
    previous_total: int
    today_total: int
    current_streak: int
    monthly_progress: List[ProgressData]

class UserProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    stress_level: Optional[str] = None
    interests: Optional[List[str]] = None
    daily_goal_minutes: Optional[int] = None
    weekly_goal_minutes: Optional[int] = None
    theme: Optional[str] = None
    accent_color: Optional[str] = None
    reminder_time: Optional[str] = None
    enable_notifications: Optional[bool] = None
    preferred_times: Optional[List[str]] = None
    focus_areas: Optional[List[str]] = None
    difficulty_level: Optional[str] = None 