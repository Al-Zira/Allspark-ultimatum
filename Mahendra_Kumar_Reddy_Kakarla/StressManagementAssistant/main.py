import os
import google.generativeai as genai
import argparse
from dotenv import load_dotenv
load_dotenv()


# Initialize the Gemini model

class StressReliefAssistant:
    def __init__(self):
        self.api_key=self._load_api_key()
        self.model=genai.GenerativeModel("gemini-2.0-flash")

    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    # Function to generate music suggestions based on mood
    def suggest_music(self, mood):
        negative_moods = {"sad", "angry", "stressed", "anxious", "frustrated", "depressed"}
        positive_moods = {"happy", "excited", "relaxed", "energetic", "motivated", "joyful"}

        if mood.lower() in negative_moods:
            prompt = f"Suggest uplifting music to help improve the mood: {mood}. Format: 'Artist - Album | Spotify Link'"
        elif mood.lower() in positive_moods:
            prompt = f"Suggest music to enhance the mood: {mood}. Format: 'Artist - Album | Spotify Link'"
        else:
            prompt = f"Suggest stress-relief music for the mood: {mood}. Format: 'Artist - Album | Spotify Link'"

        response = self.model.generate_content(prompt)
        return response.text


        

    # Function to generate jokes
    def get_jokes(self,mood):
        promt=f"Tell some jokes to relief from the {mood} mood."
        response=self.model.generate_content(promt)
        return response.text


    # Function to generate medications and relief methods
    def get_medications_and_relief_methods(self,mood):
        # Sample medications and relief methods
        prompt=f"""
        **Medications and Relief Methods for {mood} Relief:**
        - **Medications**: 

        - **Relief Methods**:

        """
        response=self.model.generate_content(prompt)
        return response.text



# Launch the Gradio app with tabs
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Stress reliefe assistant")
    parser.add_argument("--task", type=str, help="Task to execute: suggest_music,get_jokes,get_medications_and_relief_methods")
    parser.add_argument("--mood",  type=str, help="describe your mood")

    args=parser.parse_args()

    SRA=StressReliefAssistant()

    if args.task=="suggest_music":
        response=SRA.suggest_music(args.mood)
    elif args.task=="get_jokes":
        response=SRA.get_jokes(args.mood)
    elif args.task=="get_medications_and_relief_methods":
        response=SRA.get_medications_and_relief_methods(args.mood)
    print(response)

