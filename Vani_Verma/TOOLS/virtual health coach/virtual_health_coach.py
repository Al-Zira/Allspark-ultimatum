import os
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")

# Configure the Google Generative AI API with the provided API key
genai.configure(api_key=api_key)

# Define the model to use
model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",  # Use the appropriate model name
    generation_config={
        "temperature": 0.9,  # Controls creativity (higher = more creative)
        "top_p": 1.0,        # Controls diversity of response (1.0 = full diversity)
        "max_output_tokens": 2048,  # Maximum length of the generated response
        "response_mime_type": "text/plain",  # Format of the output response
    }
)

# Define a function to generate personalized health guidance
def generate_health_guidance(fitness_goal, gender, age, daily_activity_level, training_frequency, sleep_quality, diet_preference, mental_health_status, stress_level):
    # Craft a detailed prompt based on the provided inputs
    prompt = f"""
    Generate personalized health guidance based on the following inputs:
    - Fitness Goal: {fitness_goal}
    - Gender: {gender}
    - Age: {age}
    - Daily Activity Level: {daily_activity_level} (Sedentary, Lightly active, Moderately active, Very active)
    - Training Frequency: {training_frequency} (Days per week)
    - Sleep Quality: {sleep_quality} (Good, Fair, Poor)
    - Diet Preference: {diet_preference} (Vegetarian, Vegan, High-protein, Balanced, etc.)
    - Mental Health Status: {mental_health_status} (Stressed, Anxious, Calm, etc.)
    - Stress Level: {stress_level} (Low, Moderate, High)
    
    Provide personalized recommendations for:
    - Fitness Plan: Tailored to the user's fitness goal, activity level, and training frequency.
    - Nutrition Plan: Diet suggestions based on the user's preferences and lifestyle.
    - Mental Wellness: Techniques for managing stress and improving mental well-being.
    - Sleep & Recovery: Suggestions to improve sleep quality.
    """

    # Generate the health guidance using the AI model
    try:
        response = model.generate_content(prompt)
        if not response.text or "error" in response.text.lower():
            return "Sorry, please try again."
        return response.text.strip()
    except Exception as e:
        return f"Error generating health guidance: {str(e)}"

# Set up Gradio interface for user interaction
def gradio_interface(fitness_goal, gender, age, daily_activity_level, training_frequency, sleep_quality, diet_preference, mental_health_status, stress_level):
    return generate_health_guidance(fitness_goal, gender, age, daily_activity_level, training_frequency, sleep_quality, diet_preference, mental_health_status, stress_level)

# Create a simple Gradio interface
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Fitness Goal (e.g., Build muscle, Lose fat, Improve endurance)"),
        gr.Textbox(label="Gender (Male, Female, Non-binary)"),
        gr.Textbox(label="Age (e.g., 25, 40)"),
        gr.Textbox(label="Daily Activity Level (Sedentary, Lightly active, Moderately active, Very active)"),
        gr.Textbox(label="Training Frequency (Days per week, e.g., 3)"),
        gr.Textbox(label="Sleep Quality (Good, Fair, Poor)"),
        gr.Textbox(label="Diet Preference (e.g., Vegetarian, Vegan, High-protein, Balanced)"),
        gr.Textbox(label="Mental Health Status (e.g., Stressed, Calm, Anxious)"),
        gr.Textbox(label="Stress Level (Low, Moderate, High)")
    ],
    outputs="text",  # The generated response will be text
    live=True,
    title="Virtual Health Coach AI",
    description="Provide your health data, and receive personalized guidance for fitness, nutrition, mental wellness, and overall lifestyle improvement."
)

# Launch the Gradio app (this will open in a browser for you to test)
iface.launch()
