import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

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

class MenuPlanningAssistant:
    def __init__(self):
        pass

    @staticmethod
    def calculate_nutritional_needs(age, weight, height, gender, activity_level, health_goal):
        if not (1 <= age <= 120):
            return "Please provide a realistic age between 1 and 120."
        if not (30 <= weight <= 300):
            return "Please provide a realistic weight between 30 kg and 300 kg."
        if not (50 <= height <= 300):
            return "Please provide a realistic height between 50 cm and 300 cm."

        bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "male" else -161)
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "intense": 1.725,
            "very_intense": 1.9
        }
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)

        if health_goal == "weight_loss":
            calorie_goal = tdee - 500
        elif health_goal == "muscle_gain":
            calorie_goal = tdee + 500
        else:
            calorie_goal = tdee

        proteins = weight * 2.2
        fats = calorie_goal * 0.25 / 9
        carbs = (calorie_goal - (proteins * 4 + fats * 9)) / 4

        return {
            "calories": calorie_goal,
            "proteins": proteins,
            "fats": fats,
            "carbs": carbs
        }

    @staticmethod
    def suggest_supplements(nutritional_needs, dietary_preference):
        suggestions = []
        if nutritional_needs["calories"] < 2000 and dietary_preference != "vegan":
            suggestions.append("Vitamin D: 1000 IU daily.")
        if dietary_preference in ["vegan", "vegetarian"]:
            suggestions.append("Omega-3 supplement: 1000 mg EPA/DHA daily.")
        return suggestions

    @staticmethod
    def generate_meal_plan(nutritional_needs, allergies, dietary_preference, medical_condition, meal_duration=7):
        allergies = [allergy.lower() for allergy in allergies]
        prompt = (
            f"Create a {meal_duration}-day meal plan for the following nutritional requirements: "
            f"Calories: {nutritional_needs['calories']} kcal, Proteins: {nutritional_needs['proteins']} g, "
            f"Fats: {nutritional_needs['fats']} g, Carbs: {nutritional_needs['carbs']} g. "
            f"Exclude ingredients the user is allergic to: {', '.join(allergies)}. "
            f"Provide unique options for Breakfast, Lunch, Dinner, and Snacks for each day, "
            f"taking into account the dietary preference: {dietary_preference} and any medical conditions: {medical_condition}. "
            f"Ensure no repetition of meals across days."
        )
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text.replace("*", "").strip()
            else:
                return "No meal plan generated."
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def suggest_meal_times():
        return {
            "Breakfast": "7:00 AM - 9:00 AM",
            "Lunch": "12:00 PM - 2:00 PM",
            "Dinner": "6:00 PM - 8:00 PM",
            "Snacks": "10:00 AM - 11:00 AM or 3:00 PM - 4:00 PM"
        }

    def generate_weekly_plan(self, age, weight, height, gender, activity_level, health_goal, allergies, dietary_preference, medical_condition):
        nutritional_needs = self.calculate_nutritional_needs(age, weight, height, gender, activity_level, health_goal)
        if isinstance(nutritional_needs, str):
            return nutritional_needs

        meal_plan = self.generate_meal_plan(nutritional_needs, allergies, dietary_preference, medical_condition)
        supplements = self.suggest_supplements(nutritional_needs, dietary_preference)
        meal_times = self.suggest_meal_times()

        plan_text = (
            f"Meal Plan:\n{meal_plan}\n\n"
            f"Supplement Suggestions:\n" + "\n".join(supplements) + "\n\n"
            f"Suggested Meal Times:\n" + "\n".join(f"{meal}: {time}" for meal, time in meal_times.items())
        )

        file_path = "weekly_meal_plan.txt"
        with open(file_path, "w") as file:
            file.write(plan_text)

        return plan_text, file_path

    def stream_output(self, output_text, delay=0.05):
        for char in output_text:
            print(char, end='', flush=True)
            time.sleep(delay)

if __name__ == "__main__":
    assistant = MenuPlanningAssistant()
    print("Welcome to the Menu Planning Assistant!\n")
    
    # Input data
    age = int(input("Enter your age: "))
    weight = float(input("Enter your weight (kg): "))
    height = float(input("Enter your height (cm): "))
    gender = input("Enter your gender (male/female): ").lower()
    activity_level = input("Enter your activity level (sedentary, light, moderate, intense, very_intense): ").lower()
    health_goal = input("Enter your health goal (weight_loss, muscle_gain, maintenance): ").lower()
    allergies = input("Enter any allergies (comma-separated, e.g., nuts, dairy): ").split(",")
    dietary_preference = input("Enter your dietary preference (vegan, vegetarian, non-vegetarian): ").lower()
    medical_condition = input("Enter any medical conditions (comma-separated, e.g., diabetes): ")

    # Generate the plan
    result, file_path = assistant.generate_weekly_plan(
        age, weight, height, gender, activity_level, health_goal, allergies, dietary_preference, medical_condition
    )

    # Stream the generated output letter by letter
    print("\nGenerating meal plan...\n")
    assistant.stream_output(result)
    print(f"\n\nThe plan has also been saved to: {file_path}") 