import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found. Please set it in the .env file.")
genai.configure(api_key=api_key)

# Conversion rate (1 USD = 83 INR)
INR_TO_USD = 83

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.9,
        "top_p": 1,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    },
)

class RecipeCostEstimator:
    def __init__(self, model):
        self.model = model

    def generate_recipe_with_cost(self, dish_name, servings):
        prompt = (
            f"Provide a unique recipe for {dish_name}. Include the ingredients, their quantities, "
            f"and an estimated cost for each ingredient in INR. Also, calculate the total estimated cost "
            f"for {servings} servings in INR and USD. Adjust the ingredient quantities accordingly."
        )
        try:
            response = self.model.generate_content(prompt)
            if not response.text or "error" in response.text.lower():
                return "Sorry, the recipe generation failed. Please try again later."
            # Remove unwanted '*' symbol from response
            cleaned_response = response.text.replace('*', '').strip()

            # Implementing letter-by-letter streaming
            result = ""
            for char in cleaned_response:
                result += char
                print(char, end='', flush=True)
                time.sleep(0.05)  # Adjust speed of streaming (time in seconds)
            
            return result
        except Exception as e:
            return f"Error: {str(e)}. Unable to fetch recipe and cost data."

def main():
    print("Welcome to the Recipe Cost Estimator!")
    dish_name = input("Enter the name of the dish: ")
    try:
        servings = int(input("Enter the number of servings: "))
        if servings < 1:
            print("Number of servings should be at least 1.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number for servings.")
        return

    # Create RecipeCostEstimator object
    estimator = RecipeCostEstimator(model)

    # Generate recipe and cost
    recipe_info = estimator.generate_recipe_with_cost(dish_name, servings)

    print("\nRecipe and Estimated Cost:")
    print(recipe_info)

if __name__ == "__main__":
    main()
