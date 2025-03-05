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
        "temperature": 0.9,
        "top_p": 1.0,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    }
)

# Function to generate career advice
def generate_career_advice(career_interest, degree, certifications, industry):
    prompt = f"""
    Given the career interest: '{career_interest}', degree: '{degree}', certifications: '{certifications}', and industry: '{industry}', provide career guidance in a structured manner.
    Format the response as follows:

    **Career Path Advisor**

    **Summary:**
    (Brief overview of the career path based on input)

    **Recommended Steps:**
    
    1. (First step)
    2. (Second step)
    3. (Third step)
    
    **Alternative Paths:**
    
    - (Alternative career options)
    
    **Challenges & Considerations:**
    
    - (Potential challenges and how to overcome them)
    
    **Additional Notes:**
    
    - (Other important insights or recommendations)
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:\n", response_text)  # Debugging output
        
        return response_text
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I encountered an error while generating your career advice. Please try again."

# Gradio interface
def gradio_interface(career_interest, degree, certifications, industry):
    return generate_career_advice(career_interest, degree, certifications, industry)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter a Career Interest"),
        gr.Textbox(label="Enter Your Degree"),
        gr.Textbox(label="Enter Relevant Certifications"),
        gr.Textbox(label="Enter Industry Preference")
    ],
    outputs=gr.Textbox(label="Career Advice"),
    title="AI Career Path Advisor",
    description="Enter your career interest, degree, certifications, and industry to receive personalized career advice in a structured format."
)

iface.launch()
