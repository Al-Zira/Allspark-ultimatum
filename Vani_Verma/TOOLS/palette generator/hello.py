import os
import gradio as gr
import google.generativeai as genai
import json
import cv2
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans
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

# Function to extract dominant colors from an image
def extract_palette(image, num_colors=5):
    """Extracts the dominant colors from an image using KMeans clustering."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    image = image.reshape((-1, 3))  # Flatten the image
    kmeans = KMeans(n_clusters=num_colors, n_init=10, max_iter=300, random_state=42)
    kmeans.fit(image)
    colors = kmeans.cluster_centers_.astype(int)
    return colors.tolist()

# Function to create an image-based color palette visualization
def create_palette_image(palette):
    """Generates a color palette image and saves it."""
    height, width = 100, len(palette) * 100  # Define image size
    palette_image = np.zeros((height, width, 3), dtype=np.uint8)

    for i, color in enumerate(palette):
        palette_image[:, i * 100:(i + 1) * 100] = color  # Fill each color block

    file_path = "palette_output.png"
    cv2.imwrite(file_path, cv2.cvtColor(palette_image, cv2.COLOR_RGB2BGR))  # Convert back to BGR for OpenCV saving
    return file_path

# Function to save palette as a downloadable JSON file
def save_palette(palette):
    """Saves the extracted color palette as a JSON file."""
    file_path = "color_palette.json"
    with open(file_path, "w") as file:
        json.dump({"palette": palette}, file, indent=4)
    return file_path

# Gradio interface
def gradio_interface(image, num_colors):
    """Handles user input and generates the color palette and JSON file."""
    if image is None:
        return "Please upload an image.", None

    # Ensure the image is in the correct format (NumPy array)
    if not isinstance(image, np.ndarray):
        return "Invalid image format.", None

    palette = extract_palette(image, num_colors)
    palette_image_path = create_palette_image(palette)
    report_path = save_palette(palette)
    
    return palette_image_path, report_path

# Gradio UI
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Image(label="Upload an Image", type="numpy"),  # Ensures image is received as a NumPy array
        gr.Slider(3, 10, value=5, step=1, label="Number of Colors")
    ],
    outputs=[
        gr.Image(label="Extracted Color Palette"),  # Now displaying image directly in UI
        gr.File(label="Download Palette JSON")
    ],
    title="Image Palette Generator",
    description="Upload an image and select the number of dominant colors to extract a color palette."
)

iface.launch(share=True)  # Set `share=True` to create a public link
