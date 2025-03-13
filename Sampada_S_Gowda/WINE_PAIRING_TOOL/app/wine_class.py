import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found. Please set it in the .env file.")
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.9,
        "top_p": 1,
        "max_output_tokens": 2048,
        "response_mime_type": "text/plain",
    },
)

# Function to generate wine pairing based on multiple food items
def generate_best_wine_pairing(food_items):
    # Create a prompt that includes all the food items
    food_description = ", ".join(food_items)  # Combine food items into a single string
    prompt = f"Suggest 3 wines for each of the following categories (Red Wine, White Wine, Rosé Wine, Sparkling Wine, Dessert Wine) for the combination of food items: {food_description}. Please explain why each wine is a good match for the food combination and why it belongs in its respective category. Provide 3 wine suggestions per category. Do not use any symbols like '*' in the response. Provide a clear, detailed explanation for each wine pairing."

    try:
        response = model.generate_content(prompt)
        # Remove '*' symbol from the response just in case
        cleaned_response = response.text.strip().replace("*", "")
        
        return cleaned_response if response.text else "No wine pairing generated."
    except Exception as e:
        return f"Error: {str(e)}"

# Function for letter-by-letter streaming
def letter_by_letter_streaming(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)  # Adjust speed of streaming (time in seconds)

def main():
    # Infinite loop for continuous input in the terminal
    while True:
        # Prompt the user for food items
        food_items = input("Enter food items (comma separated, e.g., chicken, pizza, biryani) or type 'exit' to quit: ")
        
        if food_items.lower() == 'exit':
            print("Exiting the wine pairing tool.")
            break
        
        # Split the input into a list of food items (comma separated)
        food_items_list = [item.strip() for item in food_items.split(",")]
        
        # Generate wine pairing suggestion
        wine_suggestions = generate_best_wine_pairing(food_items_list)
        
        # Output the wine suggestions with letter-by-letter streaming
        print(f"\nSuggested wines for {', '.join(food_items_list)}:")
        letter_by_letter_streaming(wine_suggestions)  # Stream output letter by letter
        print("\n")  # Add a newline after the streaming output

if __name__ == "__main__":
    # Start the terminal-based wine pairing tool
    main()
