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

# Function to generate Q&A for speech preparation
def generate_speech_qa(speech_text):
    prompt = f"""
    Given the following speech, generate a set of at least 10 relevant questions along with well-structured answers to help with preparation.
    
    Speech:
    {speech_text}
    
    Format:
    {{
        "questions": [
            {{"question": "", "answer": ""}},
            ...
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:\n", response_text)  # Debugging output
        
        return response_text
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I encountered an error while generating the Q&A. Please try again."

# Function to save the Q&A as a text file
def save_report(qa_content):
    file_path = "speech_qa.txt"
    with open(file_path, "w") as file:
        file.write(qa_content)
    return file_path

# Gradio interface
def gradio_interface(speech_text):
    qa_content = generate_speech_qa(speech_text)
    report_path = save_report(qa_content)
    return qa_content, report_path

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter Full Speech", lines=10)
    ],
    outputs=[
        gr.Textbox(label="Generated Q&A for Speech"),
        gr.File(label="Download Q&A Report")
    ],
    title="Speech Q&A Generator",
    description="Paste your full speech to generate a set of potential questions and structured answers to prepare effectively."
)

iface.launch()
