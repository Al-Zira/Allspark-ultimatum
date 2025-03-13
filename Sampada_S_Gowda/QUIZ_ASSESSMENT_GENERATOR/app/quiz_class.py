import os
import pytesseract
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
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

# Specify the Tesseract executable path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to extract text from files
def extract_text_from_file(file_path):
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

# Function to simulate letter-by-letter streaming output
def stream_letter_by_letter(text):
    """Simulates letter-by-letter streaming output."""
    for letter in text:
        print(letter, end="", flush=True)
        time.sleep(0.02)  # Adjust speed as needed
    print()  # Newline after streaming

# Function to generate quiz
def generate_quiz(text, num_mcq, num_true_false, num_fill_blank):
    # Prepare prompts for generating different types of questions
    mcq_prompt = (
        f"Generate {num_mcq} multiple-choice questions based on the following text: '{text}'. "
        "Each question should have 4 answer options, one of which is correct. "
        "Format as:\nQ1: Question?\nA1: Correct\nA2: Incorrect 1\nA3: Incorrect 2\nA4: Incorrect 3\n"
    )

    true_false_prompt = (
        f"Generate {num_true_false} true/false questions based on the following text: '{text}'. "
        "Each question should be in the format: Q: [Statement]? (Answer: True/False)"
    )

    fill_in_blank_prompt = (
        f"Generate {num_fill_blank} fill-in-the-blank questions based on the following text: '{text}'. "
        "Each question should be in the format: Q: [Sentence with a blank]. Answer: [Correct Answer]"
    )

    # Generate quiz questions
    mcq_response = model.start_chat(history=[]).send_message(mcq_prompt)
    true_false_response = model.start_chat(history=[]).send_message(true_false_prompt)
    fill_in_blank_response = model.start_chat(history=[]).send_message(fill_in_blank_prompt)

    # Parse generated responses
    mcq_data = mcq_response.text.strip().split("\n")
    true_false_data = true_false_response.text.strip().split("\n")
    fill_in_blank_data = fill_in_blank_response.text.strip().split("\n")

    questions = []

    # Process MCQ questions
    current_question = None
    options = []
    correct_answers = []

    for line in mcq_data:
        line = line.strip()
        if line.startswith("Q"):  # Indicates a new question
            if current_question:
                questions.append({
                    "type": "mcq",
                    "question_text": current_question,
                    "choices": options,
                    "correct_answer": correct_answers[-1]  # Last added correct answer
                })
                options = []
            current_question = line  # Set to the current question
        elif line.startswith("A"):  # Indicates an answer option
            option_text = line.split(": ", 1)[1]
            options.append(option_text)
            if line.startswith("A1:"):  # Assuming A1 is the correct answer
                correct_answers.append(option_text)

    # Append the last question if it exists
    if current_question:
        questions.append({
            "type": "mcq",
            "question_text": current_question,
            "choices": options,
            "correct_answer": correct_answers[-1] if correct_answers else None
        })

    # Process True/False questions
    for line in true_false_data:
        if line.strip():
            try:
                question, answer = line.split(" (Answer: ")
                answer = answer.replace(")", "").strip()
                questions.append({
                    "type": "true_false",
                    "question_text": question.strip(),
                    "correct_answer": answer
                })
            except ValueError:
                print(f"Error parsing true/false question: {line}")

    # Process Fill-in-the-Blank questions
    for line in fill_in_blank_data:
        if line.strip():
            try:
                question, answer = line.split(" Answer: ", 1)
                questions.append({
                    "type": "fill_in_blank",
                    "question_text": question.strip(),
                    "correct_answer": answer.strip()
                })
            except ValueError:
                print(f"Error parsing fill-in-the-blank question: {line}")

    return questions

# Function to evaluate the quiz
def evaluate_quiz(questions, user_answers):
    score = 0
    total_questions = len(questions)

    for i, question in enumerate(questions):
        correct_answer = question['correct_answer']
        user_answer = user_answers.get(i + 1)
        if user_answer and user_answer.strip().lower() == correct_answer.strip().lower():
            score += 1

    stream_letter_by_letter(f"Score: {score}/{total_questions}")

# Main execution
def main():
    # Input for topic and file
    text = input("Enter the topic or leave blank to use file text: ").strip()
    file_path = input("Enter the file path (image or PDF) or leave blank to skip: ").strip()

    if file_path:
        file_text = extract_text_from_file(file_path)
        if not file_text and not text:
            print("No text found in the uploaded file or topic provided.")
            return
        text += "\n" + file_text

    if not text:
        print("Please provide a topic or upload a file to generate the quiz and assessment.")
        return

    # Input for the number of questions
    num_mcq = int(input("Enter number of MCQ questions: "))
    num_true_false = int(input("Enter number of True/False questions: "))
    num_fill_blank = int(input("Enter number of Fill-in-the-Blank questions: "))

    # Generate quiz
    questions = generate_quiz(text, num_mcq, num_true_false, num_fill_blank)

    # Display questions
    print("\nGenerated Quiz:")
    for i, question in enumerate(questions):
        stream_letter_by_letter(f"Q{i + 1}: {question['question_text']}")
        if question['type'] == 'mcq':
            for option in question['choices']:
                stream_letter_by_letter(f"  - {option}")

    # Evaluate quiz
    user_answers = {}
    for i in range(1, len(questions) + 1):
        user_answer = input(f"Enter your answer for Question {i}: ")
        user_answers[i] = user_answer

    evaluate_quiz(questions, user_answers)

if __name__ == "__main__":
    main()
