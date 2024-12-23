import google.generativeai as genai

from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from the .env file

def gemini_model():
  """Loads the Gemini Pro model and returns the pipeline."""
  api_key = os.getenv('API_KEY')
  genai.configure(api_key=api_key)  # Replace with your actual API key

  model = genai.GenerativeModel('gemini-pro')

  return model

def gemini_flas_model():
  """Loads the Gemini Pro Vision model and returns the pipeline."""
  api_key = os.getenv('API_KEY')  # Replace with your actual API key
  genai.configure(api_key=api_key)  # Replace with your actual API key

  model = genai.GenerativeModel('gemini-1.5-flash')  # Use the correct model name
  return model




if __name__=="__main__":
  model=gemini_model()
  print("geminai started")
  print(model.generate_content("what is python").text)
