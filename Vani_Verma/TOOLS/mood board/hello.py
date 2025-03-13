import os
import gradio as gr
import requests
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
pixabay_api_key = os.getenv("PIXABAY_API_KEY")

if not pixabay_api_key:
    raise ValueError("Pixabay API key not found. Please set PIXABAY_API_KEY in your .env file.")

# Function to fetch images from Pixabay
def fetch_images(query, num_images=5):
    """Fetch images from Pixabay based on the query."""
    url = f"https://pixabay.com/api/?key={pixabay_api_key}&q={query}&image_type=photo&per_page={num_images}"
    response = requests.get(url)
    data = response.json()

    if "hits" not in data or not data["hits"]:
        return "No images found for the given keyword."

    return [img["webformatURL"] for img in data["hits"]]

# Gradio interface function
def mood_board_generator(query, num_images):
    """Fetches images from Pixabay based on user input."""
    image_urls = fetch_images(query, num_images)
    return image_urls

# Gradio UI
iface = gr.Interface(
    fn=mood_board_generator,
    inputs=[
        gr.Textbox(label="Enter a Theme or Keyword"),
        gr.Slider(1, 10, value=5, step=1, label="Number of Images"),
    ],
    outputs=gr.Gallery(label="Fetched Images"),
    title="Mood Board Generator",
    description="Enter a theme (e.g., 'Beach Vibes', 'Minimal Aesthetic') and generate a mood board with images.",
)

iface.launch(share=True)  # Set `share=True` to create a public link
