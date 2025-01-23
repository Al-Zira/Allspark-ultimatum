from pydantic import BaseModel
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Legal Citation API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for validating and processing legal citations across multiple jurisdictions"
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React default
        "http://localhost:8000",  # Local development
        "http://localhost",
        "https://localhost",
        "https://localhost:3000",
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = {
        "case_sensitive": True
    }

@lru_cache()
def get_settings():
    return Settings() 