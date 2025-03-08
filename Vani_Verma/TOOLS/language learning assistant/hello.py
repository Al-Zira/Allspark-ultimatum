import os
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

# Define the model to use
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config={
        "temperature": 0.7,
        "top_p": 1.0,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    }
)

# Function to provide language learning tips
def get_language_learning_tips():
    tips = [
        "Practice daily by speaking with native speakers or using language exchange apps.",
        "Use flashcards to memorize new words and phrases.",
        "Watch movies, listen to music, and read books in the target language.",
        "Think in the language you're learning instead of translating in your head.",
        "Try shadowing: listen to native speakers and repeat what they say immediately.",
        "Keep a journal in your target language to improve writing skills.",
        "Engage with AI chatbots to practice conversational skills.",
        "Set realistic goals, such as learning 5 new words per day.",
        "Use spaced repetition systems (SRS) to retain vocabulary effectively.",
        "Surround yourself with the language by changing your device settings to the target language."
    ]
    return "\n".join(tips)

# Function to provide translations and language teaching
def translate_and_teach(text, target_language):
    prompt = f"""
    Translate the following text to {target_language} and provide a brief language lesson including grammar or cultural context.
    
    Text: {text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error in translation: {e}"

# Chatbot loop
def chatbot():
    print("\nWelcome to the Language Learning Assistant!\n")
    print("You can ask for language learning tips, translations, or language lessons. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Assistant: Goodbye! Keep practicing your language skills! 👋")
            break
        elif "tips" in user_input.lower():
            print("Assistant: Here are some language learning tips:")
            print(get_language_learning_tips())
        elif "translate" in user_input.lower() or "teach" in user_input.lower():
            try:
                text = input("Enter the text to translate and learn from: ")
                target_language = input("Enter the target language: ")
                translation_and_teaching = translate_and_teach(text, target_language)
                print(f"Assistant: Here is your translation and lesson in {target_language}:\n{translation_and_teaching}")
            except Exception as e:
                print(f"Assistant: Error in translation and teaching: {e}")
        else:
            print("Assistant: I can provide language learning tips, translations, and lessons. Try asking for 'tips', 'translate', or 'teach'.")

if __name__ == "__main__":
    chatbot()
