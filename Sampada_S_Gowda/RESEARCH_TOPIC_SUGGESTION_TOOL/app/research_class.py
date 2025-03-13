import os
from translate import Translator
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Set your Gemini API Key from the .env file
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Please set GEMINI_API_KEY in the .env file.")

genai.configure(api_key=api_key)

# Model configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize the translator
translator = Translator(to_lang="en")

# Available language options
language_options = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic",
}

def translate_text(text, dest_language, chunk_size=400):
    try:
        # Split text into chunks to avoid exceeding translation limits
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        translated_chunks = [Translator(to_lang=dest_language).translate(chunk) for chunk in chunks]
        return ''.join(translated_chunks)
    except Exception as e:
        return f"Error translating text: {e}"

def detect_harmful_content(text):
    # List of harmful content keywords to check for (this can be customized)
    harmful_keywords = ['violence', 'hate', 'abuse', 'terrorism', 'racism', 'discrimination']
    
    # Check if any harmful keyword is in the text
    for keyword in harmful_keywords:
        if keyword.lower() in text.lower():
            return True
    return False

def get_reference_link(ref):
    """Generate a proper clickable reference link."""
    if 'ieee' in ref.lower():  # If the reference contains "IEEE", treat it as an IEEE paper link
        return f"https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText={ref}"
    elif 'http' in ref:  # Handle general URLs (websites or videos)
        return ref
    else:  # For non-URL references (e.g., academic papers, books)
        return f"https://scholar.google.com/scholar?q={ref}"

def generate_research_topics_and_references(keyword, details="", language="en", max_length=50):
    # Translate inputs to English if necessary
    if language != "en":
        keyword = translate_text(keyword, "en")
        details = translate_text(details, "en")

    # Prompt for generating topics
    prompt_topics = f"Generate five short and unique research topics related to {keyword}. Details: {details}."

    try:
        # Generate topics
        response_topics = model.generate_content(prompt_topics)
        topics = [topic.strip().replace('*', '') for topic in response_topics.text.split('\n') if topic.strip()]  # Limit to 5 topics
    except Exception as e:
        return f"Error generating topics: {e}"

    # For each topic, generate a detailed description and references
    detailed_content = ""
    for i, topic in enumerate(topics, start=1):  # Number topics starting from 1
        prompt_description = f"Write a detailed 10-line description for the research topic: {topic}"
        try:
            response_description = model.generate_content(prompt_description)
            description = response_description.text.strip().replace('*', '')
        except Exception as e:
            description = f"Error generating description: {e}"

        # Split description into individual lines (without <br> tags)
        description_lines = description.split('\n')
        description_text = "\n".join(description_lines)

        prompt_references = f"Generate three academic references related to the research topic: {topic}"
        try:
            response_references = model.generate_content(prompt_references)
            references = [ref.strip().replace('*', '') for ref in response_references.text.split('\n') if ref.strip()]
        except Exception as e:
            references = [f"Error generating references: {e}"]

        # Format references and filter harmful content
        safe_references = []
        for ref in references:
            if detect_harmful_content(ref):
                safe_references.append("Harmful content detected in this reference.")
            else:
                # Get the proper clickable link for each reference
                ref_link = get_reference_link(ref)
                safe_references.append(f"[{ref}]({ref_link})")  # Convert to clickable link

        # Format the topic with description and references
        detailed_content += f"""
Topic {i}: {topic}
Description:
{description_text}

References:
{', '.join(safe_references[:3])}

{'-'*40}
"""

    # Implementing letter-by-letter streaming
    result = ""
    for char in detailed_content:
        result += char
        print(char, end='', flush=True)
        time.sleep(0.05)  # Adjust speed of streaming (time in seconds)

    return result if detailed_content else "No topics generated."

def display_language_options():
    print("Select a language from the following options:")
    for code, lang in language_options.items():
        print(f"{code}: {lang}")

    language_code = input("\nEnter the language code (e.g., 'en' for English): ").strip().lower()
    return language_code if language_code in language_options else "en"  # Default to 'en' if invalid

# Example usage
if __name__ == "__main__":
    keyword = input("Enter the keyword for research topics: ").strip()
    details = input("Enter additional details about the research (optional): ").strip()
    
    language = display_language_options()  # Now it asks for language code only once

    topics_with_references = generate_research_topics_and_references(keyword, details, language)
    print(topics_with_references)
