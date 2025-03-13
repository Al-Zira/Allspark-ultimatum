import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found. Please set it in the .env file.")
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.9,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    },
)

# Function to simulate letter-by-letter streaming without *
def letter_by_letter_stream(text, delay=0.05):
    for char in text:
        if char != "*":  # Skip the * symbol
            print(char, end="", flush=True)
            time.sleep(delay)  # Add delay to simulate real-time typing effect

# Function to generate meal plans with streaming
def generate_daily_meal_plan_with_streaming(age, weight, height, gender, activity_level, health_goal, allergies, dietary_preference, medical_condition):
    prompt = (
        f"Create a 1-day meal plan with 3 different options for Breakfast, Lunch, Dinner, and Snacks. "
        f"Consider the following nutritional requirements: Age: {age}, Weight: {weight}kg, Height: {height}cm, Gender: {gender}, "
        f"Activity Level: {activity_level}, Health Goal: {health_goal}. Exclude allergies: {allergies}. "
        f"Consider dietary preference ({dietary_preference}) and medical conditions ({medical_condition})."
    )

    try:
        # Assuming the API provides streaming responses in chunks
        response_stream = model.generate_content(prompt, stream=True)  # Enable streaming

        print("Generating meal plan...\n")
        for chunk in response_stream:
            if chunk.text:
                letter_by_letter_stream(chunk.text)  # Simulate letter-by-letter display

        meal_times = suggest_meal_times()
        meal_times_text = "\n\nSuggested Meal Times:\n" + "\n".join(f"{meal}: {time}" for meal, time in meal_times.items())
        letter_by_letter_stream(meal_times_text)

    except Exception as e:
        print(f"Error: {str(e)}")

# Function to suggest meal times
def suggest_meal_times():
    return {
        "Breakfast": "7:00 AM - 9:00 AM",
        "Lunch": "12:00 PM - 2:00 PM",
        "Dinner": "6:00 PM - 8:00 PM",
        "Snacks": "10:00 AM - 11:00 AM or 3:00 PM - 4:00 PM"
    }

# Main function to run in terminal
def run_cli():
    print("Welcome to the Nutrition Planner!")
    try:
        # Collect user input
        age = int(input("Enter your age: "))
        weight = float(input("Enter your weight (kg): "))
        height = float(input("Enter your height (cm): "))
        gender = input("Enter your gender (male/female): ").lower()
        activity_level = input("Enter your activity level (sedentary, light, moderate, intense, very_intense): ").lower()
        health_goal = input("Enter your health goal (weight_loss, muscle_gain, maintenance): ").lower()
        allergies = input("Enter any allergies (comma-separated): ")
        dietary_preference = input("Enter your dietary preference (vegan, vegetarian, non-vegetarian): ").lower()
        medical_condition = input("Enter any medical conditions (comma-separated): ")

        # Generate meal plan with streaming
        generate_daily_meal_plan_with_streaming(
            age, weight, height, gender, activity_level, health_goal, allergies, dietary_preference, medical_condition
        )

    except ValueError as e:
        print(f"Invalid input. Error: {str(e)}")

if __name__ == "__main__":
    run_cli()
