import os
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv
import plotly.graph_objects as go

# Load environment variables from .env file (where your GEMINI_API_KEY should be stored)
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")

# Configure the Google Generative AI API with the provided API key
genai.configure(api_key=api_key)

# Function to generate content ideas using Google Generative AI API with prompt engineering
def generate_content_ideas(topic):
    # Prompt engineering for better categorization of content ideas
    prompt = f"""
    Generate a list of 10 creative content ideas for the topic: '{topic}'.
    Organize the ideas into categories: 'Introduction', 'Benefits', 'How-to', 'Inspiration', and 'FAQs'. 
    Each idea should be one sentence and belong to one of the categories. 
    The response should be in the following format:
    - Introduction: "Content idea here"
    - Benefits: "Content idea here"
    - How-to: "Content idea here"
    - Inspiration: "Content idea here"
    - FAQs: "Content idea here"
    Please ensure there are at least 2 ideas in each category.
    """
    
    try:
        # Request the AI to generate content ideas based on the engineered prompt using the correct method 'generate()'
        response = genai.GenerativeModel.generate(model_name="gemini-1.0-pro", prompt=prompt)
        content_ideas = response.text.strip().split('\n')

        # Clean the content ideas, extracting just the text after the category
        structured_ideas = {category: [] for category in ['Introduction', 'Benefits', 'How to', 'Inspiration', 'FAQs']}
        
        for idea in content_ideas:
            for category in structured_ideas.keys():
                if category.lower() in idea.lower():
                    # Extract the content idea by splitting after the colon
                    content_text = idea.split(':')[1].strip()
                    structured_ideas[category].append(content_text)
                    break
        
        return structured_ideas
    except Exception as e:
        return f"Error generating content ideas: {str(e)}"

# Create a function to generate a bar chart using Plotly
def generate_visualization(content_ideas):
    # Count how many content ideas fall into each category (e.g., "Introduction", "How-to", etc.)
    category_counts = {category: len(ideas) for category, ideas in content_ideas.items()}

    # Prepare data for the Plotly chart
    categories = list(category_counts.keys())
    counts = list(category_counts.values())

    # Create a bar chart using Plotly
    fig = go.Figure(data=[go.Bar(x=categories, y=counts, marker_color='skyblue')])

    fig.update_layout(
        title='Content Ideas Distribution by Category',
        xaxis_title='Categories',
        yaxis_title='Number of Ideas',
    )

    # Return Plotly chart in HTML format for Gradio to display
    return fig.to_html(full_html=False)

# Set up Gradio interface for user interaction
def gradio_interface(topic):
    content_ideas = generate_content_ideas(topic)
    
    if isinstance(content_ideas, str):  # In case of an error generating content ideas
        return content_ideas
    
    chart_html = generate_visualization(content_ideas)
    return chart_html

# Create a simple Gradio interface with visualization
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter Topic (e.g., Yoga, Cooking, Fitness)")
    ],
    outputs="html",  # The generated output will be an HTML (Plotly chart)
    live=True,
    title="AI-Powered Content Ideas Visualization with Prompt Engineering",
    description="Provide a topic to generate content ideas, categorize them, and visualize their distribution across different categories."
)

# Launch the Gradio app (this will open in a browser for you to test)
iface.launch()
