import google.generativeai as genai
import os
from typing import Dict, List, Union
import logging
from config import GEMINI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class MindfulnessActivityGenerator:
    def __init__(self):
        """Initialize the activity generator."""
        self.model = model
        
    def generate_personalized_activity(
        self,
        user_profile: Dict,
        mood: str,
        energy_level: int,
        stress_level: int,
        time_available: int,
        interests: List[str]
    ) -> Dict:
        """Generate a personalized mindfulness activity."""
        try:
            prompt = f"""
            Create a mindful activity for someone who:
            - Current mood: {mood}
            - Energy level: {energy_level}/10
            - Stress level: {stress_level}/10
            - Has {time_available} minutes available
            - Interests: {', '.join(interests)}

            Format the response as a structured activity with:
            1. A title
            2. Clear step-by-step instructions
            3. Expected benefits
            4. Duration: {time_available} minutes
            """

            response = self.model.generate_content(prompt)
            activity_text = response.text
            
            return {
                "text": activity_text,
                "duration": time_available,
                "category": "Personalized Practice"
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized activity: {str(e)}")
            # Return a default meditation activity as fallback
            return {
                "text": f"""
=== Today's Mindfulness Activity ===
Category: Basic Meditation

Instructions:
STEPS:
1. Find a comfortable seated position
2. Close your eyes and take three deep breaths
3. Focus on your natural breathing pattern
4. When your mind wanders, gently return to your breath
5. Continue for the remaining time
6. Slowly open your eyes when ready

BENEFITS:
- Reduced stress and anxiety
- Improved focus and clarity
- Better emotional regulation
- Enhanced self-awareness

Press Enter to start the practice...
                """,
                "duration": time_available,
                "category": "Basic Meditation"
            }

    def generate_stress_relief_practice(self, stress_trigger: str, stress_level: int) -> str:
        """Generate a stress relief practice based on the trigger and level."""
        try:
            prompt = f"""
            Create a quick stress relief practice for someone who:
            - Is experiencing stress from: {stress_trigger}
            - Current stress level: {stress_level}/10

            Format as a short, practical exercise with:
            1. Immediate action steps
            2. Breathing technique
            3. Positive affirmation
            4. Duration: 2-5 minutes
            """

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating stress relief practice: {str(e)}")
            return """
Quick Stress Relief Practice (2-5 minutes):

1. Take 3 deep breaths, counting to 4 on inhale and 6 on exhale
2. Gently roll your shoulders back and release tension
3. Place one hand on your heart and say "I am calm and capable"
4. Continue breathing slowly for 1 minute
5. Open your eyes when ready
            """

    def generate_sleep_recommendation(self, sleep_quality: str, stress_level: int) -> str:
        """Generate sleep practice recommendations."""
        try:
            prompt = f"""
            Create a bedtime practice for someone who:
            - Reports {sleep_quality} sleep quality
            - Has a stress level of {stress_level}/10

            Format as a gentle routine with:
            1. Pre-bed activities
            2. Relaxation technique
            3. Mindful breathing exercise
            4. Duration: 5-10 minutes
            """

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating sleep recommendation: {str(e)}")
            return """
Bedtime Relaxation Practice (5-10 minutes):

1. Dim the lights and find a comfortable position
2. Take 5 deep, slow breaths
3. Progressive relaxation: tense and release each muscle group
4. Visualize a peaceful place
5. Continue slow breathing until you feel sleepy
            """ 