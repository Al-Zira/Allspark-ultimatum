import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Application Settings
    # Financial Calculation Parameters
    DEFAULT_RISK_FREE_RATE = 0.02  # 2% risk-free rate
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    
    # Validation Methods
    @classmethod
    def validate_config(cls):
        """
        Validate critical configuration parameters
        """
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("Gemini API Key is missing")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
