import os
import json
import tensorflow as tf
from dotenv import load_dotenv
from tensorflow.keras.applications import MobileNetV2  # type: ignore
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input  # type: ignore
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import google.generativeai as genai
import numpy as np
import time

# Function to stream output letter by letter
def stream_output(output_text, delay=0.05):
    """
    Stream output letter by letter with a delay between each character.
    """
    for char in output_text:
        print(char, end='', flush=True)
        time.sleep(delay)

class EducationalContentSummarizer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set GEMINI_API_KEY in the .env file.")
        genai.configure(api_key=self.api_key)
        self.imagenet_class_index = self.load_imagenet_class_index()
        self.model = MobileNetV2(weights="imagenet")

    def load_imagenet_class_index(self):
        file_path = r"C:\\Users\\91843\\OneDrive\\Desktop\\ai tools\\educational_content_summarizer\\imagenet_class_index.json"
        with open(file_path, "r") as f:
            return json.load(f)

    def classify_image(self, image):
        img = tf.image.resize(image, (224, 224))
        img = tf.expand_dims(img, 0)
        img = preprocess_input(img)
        predictions = self.model.predict(img)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]
        class_name = decoded_predictions[0][1]
        confidence = decoded_predictions[0][2]
        return class_name, confidence

    def generate_info_with_gemini(self, prompt):
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.replace("*", "").strip()

    def extract_text_from_image(self, image):
        text = pytesseract.image_to_string(image)
        cleaned_text = " ".join(text.splitlines())
        return cleaned_text.strip()

    def extract_text_from_pdf(self, file_path):
        pdf_reader = PdfReader(file_path)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text.strip()

    def extract_text_from_images_in_pdf(self, file_path):
        images = convert_from_path(file_path)
        extracted_text = ""
        for img in images:
            text = self.extract_text_from_image(img)
            extracted_text += text + "\n"
        return extracted_text.strip()

    def process_image(self, image_path):
        image = Image.open(image_path)
        ocr_text = self.extract_text_from_image(image)
        if ocr_text:
            summary = self.generate_info_with_gemini(f"Summarize and give extra info about the following text: {ocr_text}")
            stream_output(f"Summary:\n{summary}")
        else:
            class_name, confidence = self.classify_image(image)
            info = self.generate_info_with_gemini(f"Provide information about a {class_name}")
            stream_output(f"Description: {info}")

    def process_pdf(self, file_path):
        pdf_text = self.extract_text_from_pdf(file_path)
        if pdf_text:
            summary = self.generate_info_with_gemini(f"Summarize the following text: {pdf_text}")
            stream_output(f"Summary:\n{summary}")
        else:
            image_text = self.extract_text_from_images_in_pdf(file_path)
            if image_text.strip():
                summary = self.generate_info_with_gemini(f"Summarize the following text: {image_text}")
                stream_output(f"Summary:\n{summary}")
            else:
                stream_output("No text could be extracted from the PDF images.")

    def compare_pdfs(self, file_path1, file_path2):
        text1 = self.extract_text_from_pdf(file_path1)
        text2 = self.extract_text_from_pdf(file_path2)
        prompt_text = (
            f"Compare the following two documents and provide a summary of their differences and similarities:\n\n"
            f"Document 1:\n{text1[:1000]}\n\nDocument 2:\n{text2[:1000]}"
        )
        comparison = self.generate_info_with_gemini(prompt_text)
        stream_output(f"Comparison:\n{comparison}")

    def generate_quiz(self, content):
        prompt = f"Generate a multiple-choice quiz based on the following content:\n{content}\nProvide 4 options for each question."
        quiz = self.generate_info_with_gemini(prompt)
        return quiz

    def generate_quiz_from_file(self, file_path):
        pdf_text = self.extract_text_from_pdf(file_path)
        if pdf_text:
            quiz = self.generate_quiz(pdf_text)
        else:
            image_text = self.extract_text_from_images_in_pdf(file_path)
            quiz = self.generate_quiz(image_text)
        stream_output(f"Generated Quiz:\n{quiz}")

if __name__ == "__main__":
    summarizer = EducationalContentSummarizer()

    while True:
        print("\nChoose an option:")
        print("1. Process multiple images")
        print("2. Process multiple PDFs")
        print("3. Compare two PDFs")
        print("4. Generate a quiz from a PDF")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            image_paths = input("Enter the image file paths (comma-separated): ").split(',')
            for image_path in image_paths:
                summarizer.process_image(image_path.strip())

        elif choice == "2":
            pdf_paths = input("Enter the PDF file paths (comma-separated): ").split(',')
            for pdf_path in pdf_paths:
                summarizer.process_pdf(pdf_path.strip())

        elif choice == "3":
            file_path1 = input("Enter the first PDF file path: ")
            file_path2 = input("Enter the second PDF file path: ")
            summarizer.compare_pdfs(file_path1, file_path2)

        elif choice == "4":
            file_path = input("Enter the PDF file path: ")
            summarizer.generate_quiz_from_file(file_path)

        elif choice == "5":
            print("Exiting the application.")
            break

        else:
            print("Invalid choice. Please try again.")
