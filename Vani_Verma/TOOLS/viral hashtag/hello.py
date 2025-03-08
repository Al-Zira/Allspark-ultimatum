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

# Function to generate viral hashtags with usage percentage
def generate_hashtags(topic):
    prompt = f"""
    Generate a set of viral hashtags based on the given topic.
    Ensure they are catchy, relevant, and optimized for engagement.
    Additionally, provide an estimated percentage of how frequently each hashtag is used.
    Format: hashtag - percentage
    
    Topic: {topic}
    
    Hashtags:
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:\n", response_text)  # Debugging output
        
        return response_text
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I encountered an error while generating hashtags. Please try again."

# Gradio interface
def gradio_interface(topic):
    return generate_hashtags(topic)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter Topic")
    ],
    outputs=gr.Textbox(label="Generated Hashtags with Usage Percentage", lines=10),
    title="Viral Hashtag Generator",
    description="Enter a topic to generate a list of viral hashtags along with their estimated usage percentage."
)

iface.launch()