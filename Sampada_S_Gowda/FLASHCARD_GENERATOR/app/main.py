import os
import time
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Set your Gemini API Key from the .env file
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Please set GEMINI_API_KEY in the .env file.")

genai.configure(api_key=api_key)


class FlashcardApp:
    def __init__(self):
        # Model configuration
        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "max_output_tokens": 2048,
            "response_mime_type": "text/plain",
        }
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
        )
        self.setup_tesseract()

    def setup_tesseract(self):
        """Specify the Tesseract executable path if necessary"""
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def extract_text_from_file(self, file_path):
        """Extract text from image or PDF file"""
        text = ""
        if file_path.endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                print(f"Failed to read the PDF: {e}")
        else:
            try:
                text = pytesseract.image_to_string(Image.open(file_path))
            except Exception as e:
                print(f"Failed to process the image: {e}")
        return text.strip()

    def handle_text_input(self):
        """Handles multi-line text input from the user."""
        print("Enter the text for flashcards (type 'END' on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":  # Stop reading input when 'END' is entered
                break
            lines.append(line)
        return "\n".join(lines).strip()

    def stream_letter_by_letter(self, text):
        """Simulates letter-by-letter streaming output."""
        for letter in text:
            print(letter, end="", flush=True)
            time.sleep(0.02)  # Adjust speed as needed
        print()  # Newline after streaming

    def generate_flashcards(self, text):
        """Generates flashcards from the provided text using the Gemini API."""
        # Flashcard generation prompt
        flashcard_prompt = (
            f"Generate flashcards based on the following text: '{text}'. "
            "Each flashcard should have a question and an answer based on the content. "
            "Format each flashcard as:\nQ: Question?\nA: Answer"
        )

        # Generate flashcards
        flashcard_response = self.model.start_chat(history=[]).send_message(flashcard_prompt)

        # Stream output letter by letter
        print("\nGenerating flashcards...")
        self.stream_letter_by_letter(flashcard_response.text)

        # Parse generated flashcards
        flashcard_data = flashcard_response.text.strip().split("\n")
        flashcards = []

        current_flashcard = {}
        for line in flashcard_data:
            line = line.strip()
            if line.startswith("Q:"):
                if current_flashcard:
                    flashcards.append(current_flashcard)
                current_flashcard = {"question": line[2:].strip()}
            elif line.startswith("A:"):
                current_flashcard["answer"] = line[2:].strip()

        # Append the last flashcard if it exists
        if current_flashcard:
            flashcards.append(current_flashcard)

        # Display flashcards in terminal
        print("\nFlashcards generated:\n")
        for idx, card in enumerate(flashcards, 1):
            print(f"{idx}. Q: {card['question']}")
            print(f"   A: {card['answer']}\n")

    def run(self):
        """Run the application in terminal."""
        print("Welcome to the Flashcard Generator!")
        print("You can either input a topic or upload a file.")

        # Ask for text input or file path
        print("1. Enter text input")
        print("2. Upload a file")
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice == '1':
            # Handle text input
            text = self.handle_text_input()
            if text:
                self.generate_flashcards(text)
            else:
                print("No text provided. Exiting.")
        elif choice == '2':
            # Handle file upload
            file_path = input("Enter the file path: ").strip()
            if os.path.exists(file_path):
                file_text = self.extract_text_from_file(file_path)
                if file_text:
                    self.generate_flashcards(file_text)
                else:
                    print("No text extracted from the file.")
            else:
                print("File not found. Exiting.")
        else:
            print("Invalid choice. Exiting.")


if __name__ == "__main__":
    flashcard_app = FlashcardApp()
    flashcard_app.run()
