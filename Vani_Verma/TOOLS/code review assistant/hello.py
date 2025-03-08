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

# Function to review code and provide feedback
def review_code(code_snippet):
    prompt = f"""
    You are a professional code reviewer. Analyze the following code snippet and provide feedback on:
    - Code quality and readability
    - Best practices and improvements
    - Potential optimizations
    - Possible errors or security issues
    
    Respond in the following format:
    
    **Code Review Report**
    
    **Strengths:**
    - (List of positive aspects)
    
    **Areas for Improvement:**
    - (List of suggested improvements)
    
    **Optimization Suggestions:**
    - (Suggestions for making the code more efficient)
    
    **Potential Issues:**
    - (List of potential bugs, security vulnerabilities, or inefficiencies)
    
    Here is the code:
    
    ```python
    {code_snippet}
    ```
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:\n", response_text)  # Debugging output
        
        return response_text
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I encountered an error while reviewing your code. Please try again."

# Gradio interface
def gradio_interface(code_snippet):
    return review_code(code_snippet)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[gr.Textbox(label="Paste Your Code Here", lines=10)],
    outputs=gr.Textbox(label="Code Review Feedback", lines=15),
    title="AI Code Review Assistant",
    description="Paste your code snippet to receive a detailed review, including strengths, areas for improvement, optimization suggestions, and potential issues."
)

iface.launch()