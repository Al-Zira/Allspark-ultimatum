import os
import gradio as gr
import google.generativeai as genai
import json
import openai
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO

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

# Function to generate a mood board concept

def generate_mood_board(theme):
    prompt = f"""
    Generate a detailed mood board concept for the given theme.
    Include elements like color schemes, textures, imagery ideas, and overall aesthetic inspiration.
    List the main elements in bullet points.
    
    Theme: {theme}
    
    Mood Board:
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:\n", response_text)  # Debugging output
        
        return response_text
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I encountered an error while generating the mood board. Please try again."

# Function to generate an image using DALL·E API
def generate_image_from_prompt(prompt):
    dalle_api_url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-2",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        response = requests.post(dalle_api_url, headers=headers, json=payload)
        response_json = response.json()
        image_url = response_json["data"][0]["url"]
        return image_url
    except Exception as e:
        print("Error generating image:", e)
        return None

# Function to generate a mood board image
def generate_mood_board_image(theme):
    mood_board_description = generate_mood_board(theme)
    image_url = generate_image_from_prompt(mood_board_description)
    
    if image_url:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img
    else:
        return "Error generating mood board image."

# Gradio interface
def gradio_interface(theme):
    return generate_mood_board_image(theme)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter Theme")
    ],
    outputs=gr.Image(label="Generated Mood Board Image"),
    title="Mood Board Generator",
    description="Enter a theme to generate a visual mood board with aesthetic elements, colors, and textures."
)

iface.launch()
