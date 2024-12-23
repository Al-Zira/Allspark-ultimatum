import gradio as gr
import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model
import requests
import base64
from dotenv import load_dotenv
import os
# Initialize the Gemini model
model = gemini_model()

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')


# Function to get Spotify access token
def get_spotify_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(auth_string.encode()).decode()}"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(auth_url, headers=headers, data=data)
    return response.json().get("access_token")

# Function to search for an album and retrieve its details
def search_album_details(album, artist, token):
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": f"album:{album} artist:{artist}",
        "type": "album",
        "limit": 1
    }
    response = requests.get(search_url, headers=headers, params=params)
    albums = response.json().get("albums", {}).get("items", [])
    if albums:
        album_info = albums[0]
        album_image = album_info.get("images", [{}])[0].get("url", "No image available")
        spotify_link = album_info.get("external_urls", {}).get("spotify", "No link available")
        return album_image, spotify_link
    return "No image available", "No link available"

# Function to generate music suggestions based on mood
def suggest_music(mood):
    prompt = f"Suggest some stress-relief music for the mood: {mood}. I want list of items 'Artist-Album' in this format only."
    response = model.generate_content(prompt)
    token = get_spotify_token()
    responses = response.text.split("\n")
    
    results = []
    for item in responses:
        if "-" in item:
            item = item.strip("-")
            artist, album = item.split("-", 1)
            artist = artist.strip()
            album = album.strip()
            album_image, spotify_link = search_album_details(album, artist, token)
            results.append((album_image, album, artist, spotify_link))
    
    return results

# Function to generate jokes
def tell_jokes(mood):
    promt=f"Tell some jokes to relief from the {mood} mood."
    response=model.generate_content(promt)
    return response.text


# Function to generate medications and relief methods
def tell_medications_and_relief_methods(mood):
    # Sample medications and relief methods
    prompt=f"""
    **Medications and Relief Methods for {mood} Relief:**
    - **Medications**: 
       
    - **Relief Methods**:
       
    """
    response=model.generate_content(prompt)
    return response.text

# Gradio output display function for music
def display_music_suggestions(mood):
    suggestions = suggest_music(mood)
    formatted_results = []
    for album_image, album, artist, spotify_link in suggestions:
        formatted_results.append(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <img src="{album_image}" alt="Album Image" style="width: 100px; height: 100px; margin-right: 20px;" />
                <div>
                    <p><strong>Album:</strong> {album}</p>
                    <p><strong>Artist:</strong> {artist}</p>
                    <a href="{spotify_link}" target="_blank">Listen on Spotify</a>
                </div>
            </div>
            """
        )
    return "\n".join(formatted_results)

# Gradio output display function for jokes
def display_jokes(mood):
    return tell_jokes(mood)

# Gradio output display function for medications and relief methods
def display_medications_and_relief_methods(mood):
    return tell_medications_and_relief_methods(mood)

# Function to generate chatbot responses with a friendly tone
def chatbot_response(user_input):
    prompt = f"Respond in a friendly, short, and casual tone to this message: '{user_input}'"
    response = model.generate_content(prompt)
    return response.text.strip()

# Define Gradio interface for the chatbot
def create_chat_interface():
    with gr.Blocks() as demo:
        with gr.Column():
            chatbox = gr.Chatbot(label="Friendly Chatbot", height=400)
            msg_input = gr.Textbox(placeholder="Say something...", label="Your Message", lines=1)
            send_button = gr.Button("Send")
            
            def send_message(msg, history):
                bot_reply = chatbot_response(msg)
                history.append((msg, bot_reply))
                return history, ""
            
            send_button.click(fn=send_message, inputs=[msg_input, chatbox], outputs=[chatbox, msg_input])

    return demo

# Define Gradio interface with multiple tabs
def interface_fn(mood, button_choice):
    if button_choice == "Suggest Music":
        return display_music_suggestions(mood)
    elif button_choice == "Tell Me Some Jokes":
        return display_jokes(mood)
    elif button_choice == "Tell Medications and Relief Methods":
        return display_medications_and_relief_methods(mood)

# Define Gradio interface for the mood-based features
mood_interface = gr.Interface(
    fn=interface_fn,
    inputs=[
        gr.Textbox(label="Describe your mood"),
        gr.Radio(
            choices=["Suggest Music", "Tell Me Some Jokes", "Tell Medications and Relief Methods"],
            label="Choose an option"
        )
    ],
    outputs="html",  # Use HTML to allow custom styling
    title="Stress Management Assistant",
    description="Enter your mood, and select an option to receive music suggestions, jokes, or stress relief advice!"
)

# Define Gradio interface for the chatbot
chatbot_interface = create_chat_interface()

# Define Gradio Tabs for different interfaces
with gr.Blocks() as demo:
    with gr.Tab("Mood-Based Suggestions"):
        mood_interface.render()
    with gr.Tab("Friendly Chatbot"):
        chatbot_interface.render()

# Launch the Gradio app with tabs
if __name__ == "__main__":
    demo.launch()
