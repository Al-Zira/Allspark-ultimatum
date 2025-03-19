import os  # For interacting with the operating system
import sys  # For system-related functions, such as exiting the script
import yaml  # For reading and parsing YAML configuration files
import google.generativeai as genai  # Importing Google Generative AI SDK for Gemini Pro model
import argparse  # For handling command-line arguments
from dotenv import load_dotenv
load_dotenv()


# Class to interact with Gemini Pro model and find allergy substitutes
class AllergySubstitutefinder:
    def __init__(self):
        # Initialize the generative AI model (Gemini Pro - Flash version for faster responses)
        self.api_key=self._load_api_key()
        self.model=genai.GenerativeModel('gemini-2.0-flash')
    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    
    def get_substituters(self, allergy_items, situation):
        """
        Generate allergy substitutes using the Gemini Pro model.
        
        Parameters:
        - allergy_items (str): Comma-separated allergy items.
        - situation (str): Context (e.g., food, medicine) for suggesting substitutes.
        
        Returns:
        - str: AI-generated response with substitutes and explanations in table format.
        """
        prompt = f"""Suggest substitutes for the following allergy items: {allergy_items}. 
        Situation: {situation}.
        Provide a brief explanation for each substitute in a table format with the columns: Allergy Item, Substitute, Explanation."""
        
        # Generate response using the Gemini Pro model
        response = self.model.generate_content(prompt)
        return response.text  # Return the generated text response

# Main execution block to handle command-line arguments and execute the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Nutrition Fact Checker - Extracts nutrition details from product information or images."
    )
    
    # Define command-line arguments
    parser.add_argument("--allergy_items", nargs='+', type=str, help="allergy items (list)")
    parser.add_argument("--situation", type=str, help="situation ex:food,medicine,etc., (list)")
    
    # Parse arguments from the command line
    args = parser.parse_args()
    
    # Instantiate the AllergySubstitutefinder class
    substituter = AllergySubstitutefinder()
    
    # Get substitutes using the Gemini Pro model
    response = substituter.get_substituters(','.join(args.allergy_items), args.situation)
    
    # Print the generated response
    print(response)
