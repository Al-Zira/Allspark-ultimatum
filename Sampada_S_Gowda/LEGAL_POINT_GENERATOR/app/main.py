import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

class LegalPointGenerator:
    def __init__(self):
        """
        Initialize the Legal Point Generator, loading API keys and configuring the Gemini model.
        """
        # Load environment variables
        load_dotenv()

        # Load and configure Gemini API Key
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set it in the .env file.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 2048,
                "response_mime_type": "text/plain",
            },
        )

    def extract_text_from_pdf(self, file_path, max_pages=10):
        """
        Extracts text from a PDF file, with an optional limit on the number of pages.
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for i, page in enumerate(reader.pages):
                    if i >= max_pages:
                        break
                    text += page.extract_text() or ""
            return text.strip()[:5000]  # Limit extracted text to 5000 characters
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    def extract_text_from_image(self, image_path):
        """
        Extract text from an image using OCR.
        """
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()[:5000]  # Limit text to 5000 characters
        except Exception as e:
            return f"Error extracting text from image: {str(e)}"

    def generate_legal_argument_from_text(self, text):
        """
        Generate legal argument using Gemini API.
        """
        prompt = f"""
        Analyze the following case document and generate a detailed legal argument:
        {text}

        The argument should include:
        1. A summary of the legal issue
        2. A discussion of the key arguments and counterarguments
        3. A detailed reference to any supporting documents, precedents, or case law (if not explicitly provided in the case)
        4. A conclusion with a suggested legal relief or outcome
        """
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.replace("*", "").strip()
            else:
                return "No legal argument generated. Please try again."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def stream_text(self, text, delay=0.05):
        """
        Stream the text letter by letter with a delay between each letter.
        """
        for char in text:
            yield char
            time.sleep(delay)

    def process_document(self, file_path):
        """
        Handles document processing and generates legal arguments.
        """
        file_ext = file_path.split('.')[-1].lower()

        if file_ext == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext in ['jpg', 'jpeg', 'png']:
            text = self.extract_text_from_image(file_path)
        elif file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()
        else:
            return "Unsupported file format."

        if not text:
            return "No readable text found in the document."

        return self.generate_legal_argument_from_text(text)

    def process_text_input(self, input_text):
        """
        Process raw text input and generate legal arguments.
        """
        if not input_text.strip():
            return "Input text is empty. Please provide valid legal text."
        return self.generate_legal_argument_from_text(input_text)

# Command-line interface
if __name__ == "__main__":
    generator = LegalPointGenerator()
    
    print("Welcome to the Legal Point Generator!")
    print("Choose an option:")
    print("1. Upload a document")
    print("2. Enter legal text manually")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        file_path = input("Enter the path to the document (PDF, image, or text file): ").strip()
        if not os.path.exists(file_path):
            print("File not found. Please provide a valid file path.")
        else:
            result = generator.process_document(file_path)
            print("\nGenerated Legal Argument:\n")
            # Stream the result letter by letter
            for char in generator.stream_text(result):
                print(char, end="", flush=True)
    elif choice == "2":
        input_text = input("Enter the legal text: ").strip()
        result = generator.process_text_input(input_text)
        print("\nGenerated Legal Argument:\n")
        # Stream the result letter by letter
        for char in generator.stream_text(result):
            print(char, end="", flush=True)
    else:
        print("Invalid choice. Exiting.")
