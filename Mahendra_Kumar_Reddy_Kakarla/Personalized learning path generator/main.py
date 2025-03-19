import os
import sys
import yaml
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

class LearningPathGenerator:
    def __init__(self):
        """Initialize the learning path generator with the AI model."""
        self.api_key=self._load_api_key()
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    
    def generate_learning_path(self, skill_set, interests, goals):
        """Generates a structured learning path based on user skills, interests, and goals."""
        prompt = f"""
        Based on the following details:
        - Skills: {', '.join(skill_set)}
        - Interests: {', '.join(interests)}
        - Goals: {goals}
        
        Generate a detailed learning path. Break it down into steps and organize them as a to-do list.
        If there are any courses or books available, provide 3-4 recommendations for each step along with links if available.
        """
        
        # Generate a response from the AI model
        response = self.model.generate_content(prompt)
        return response.text.strip()

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing for command-line input
    parser = argparse.ArgumentParser(description="Learning Path Generator")
    parser.add_argument("--skill_set", nargs='+', type=str, help="User's skill set (list)")
    parser.add_argument("--interests", nargs='+', type=str, help="User's interests (list)")
    parser.add_argument("--goals", type=str, help="User's goals (string)")
    
    args = parser.parse_args()
    
    # Create an instance of the LearningPathGenerator
    generator = LearningPathGenerator()
    
    # Generate the learning path based on user input
    result = generator.generate_learning_path(args.skill_set, args.interests, args.goals)
    
    # Print the generated learning path
    print(result)
