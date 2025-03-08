import os
import gradio as gr
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")

# Configure the Google Generative AI API with the provided API key
genai.configure(api_key=api_key)

# Define the models to use
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config={
        "temperature": 0.7,
        "top_p": 1.0,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    }
)

# Function to generate a workout plan
def generate_workout_plan(fitness_level, goal, workout_preference, available_equipment, workout_duration):
    prompt = f"""
    Generate a detailed weekly workout plan based on the user's inputs.
    Include exercises, sets, reps, rest periods, and any additional guidance.
    
    Fitness Level: {fitness_level}
    Goal: {goal}
    Workout Preference: {workout_preference}
    Available Equipment: {available_equipment}
    Workout Duration: {workout_duration} minutes per session
    
    Workout Plan:
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:\n", response_text)  # Debugging output
        
        return response_text
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I encountered an error while generating the workout plan. Please try again."

# Function to save the workout plan as a text file
def save_report(workout_plan):
    file_path = "workout_plan.txt"
    with open(file_path, "w") as file:
        file.write(workout_plan)
    return file_path

# Gradio interface
def gradio_interface(fitness_level, goal, workout_preference, available_equipment, workout_duration):
    workout_plan = generate_workout_plan(fitness_level, goal, workout_preference, available_equipment, workout_duration)
    report_path = save_report(workout_plan)
    return workout_plan, report_path

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter Your Fitness Level (Beginner, Intermediate, Advanced)"),
        gr.Textbox(label="Enter Your Fitness Goal (Weight Loss, Muscle Gain, Endurance, etc.)"),
        gr.Textbox(label="Workout Preference (Cardio, Strength, Yoga, etc.)"),
        gr.Textbox(label="Available Equipment (Dumbbells, Resistance Bands, None, etc.)"),
        gr.Number(label="Workout Duration (Minutes per Session)")
    ],
    outputs=[
        gr.Textbox(label="Generated Workout Plan"),
        gr.File(label="Download Workout Plan Report")
    ],
    title="Workout Plan Generator",
    description="Enter your fitness level, goal, workout preference, available equipment, and session duration to generate a personalized workout plan."
)

iface.launch()