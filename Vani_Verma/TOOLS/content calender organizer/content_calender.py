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
        "temperature": 0.7,  # Controls creativity (higher = more creative)
        "top_p": 1.0,        # Controls diversity of response (1.0 = full diversity)
        "max_output_tokens": 2048,  # Maximum length of the generated response
        "response_mime_type": "text/plain",  # Format of the output response
    }
)

# Define a function to generate content ideas for a calendar
def generate_content_calendar(topic):
    # Generate a prompt for the AI model to create content ideas for the provided topic
    prompt = f"""
    Generate a content calendar with content ideas for the following topic: '{topic}'.
    The content should be relevant, creative, and diverse. Each content idea should be appropriate for a blog, social media post, or any other digital platform. Provide at least 5 content ideas. 
    
    For example:
    - "Introduction to [Topic]"  
    - "Benefits of [Topic]"
    - "How to get started with [Topic]"
    - "Inspiration and Success Stories about [Topic]"
    - "FAQs about [Topic]"
    """
    
    # Request the AI to generate content ideas
    try:
        response = model.generate_content(prompt)
        if not response.text or "error" in response.text.lower():
            return "Sorry, please try again."
        return response.text.strip()
    except Exception as e:
        return f"Error generating content calendar: {str(e)}"

# Set up Gradio interface for user interaction
def gradio_interface(topic):
    return generate_content_calendar(topic)

# Create a simple Gradio interface
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Topic (e.g., Kathak Classes, Yoga Workshop, etc.)")
    ],
    outputs="text",  # The generated response will be text
    live=True,
    title="AI-Powered Content Calendar Generator",
    description="Provide a topic for your content calendar, and receive personalized content ideas for your posts."
)

# Launch the Gradio app (this will open in a browser for you to test)
iface.launch()
