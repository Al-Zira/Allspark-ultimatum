# Quiz Generator and Evaluator CLI

## Overview
This is a command-line application that generates quizzes from text input, images, or PDFs using Google Gemini AI. It allows users to create multiple-choice questions (MCQs), true/false questions, and fill-in-the-blank questions based on extracted or provided content. Users can then answer the generated questions, and the application evaluates their performance.

## Features
- Extracts text from images and PDFs using Tesseract OCR.
- Generates quizzes based on user-provided topics or extracted text.
- Supports MCQs, true/false, and fill-in-the-blank questions.
- Simulates letter-by-letter output for an engaging experience.
- Evaluates user answers and provides a score.

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- Required Python packages:
  ```sh
  pip install pytesseract Pillow google-generativeai python-dotenv PyPDF2
  ```
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (Set up the path in the script if necessary)
- Google Gemini API key (Set in a `.env` file)

## Setup
1. Clone the repository or download the script.
2. Create a `.env` file in the project directory and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Ensure Tesseract OCR is installed and update its path in the script if needed:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Usage
1. Run the script:
   ```sh
   python script.py
   ```
2. Follow the prompts to enter a topic or upload an image/PDF.
3. Specify the number of MCQ, true/false, and fill-in-the-blank questions.
4. Answer the generated questions.
5. View your score after evaluation.

## Example Interaction
```
Enter the topic or leave blank to use file text: Artificial Intelligence
Enter the file path (image or PDF) or leave blank to skip:
Enter number of MCQ questions: 2
Enter number of True/False questions: 2
Enter number of Fill-in-the-Blank questions: 1

Generated Quiz:
Q1: What is AI?
  - A technology that enables machines to think
  - A programming language
  - A hardware device
  - A type of database
...
Enter your answer for Question 1: A technology that enables machines to think
...
Score: 4/5
```

## Running with Docker
You can also run the application inside a Docker container.

### 1️⃣ Build the Docker Image
Navigate to the project directory where the `Dockerfile` is located and run:
```sh
docker build -t quiz-app .
```

### 2️⃣ Run the Docker Container
To start the container:
```sh
docker run --rm -it quiz-app
```

### 3️⃣ Run in Detached Mode (Optional)
If you want to run the container in the background:
```sh
docker run -it --rm -v "$(pwd)/uploads:/app/uploads" quiz-app
```
To stop the container:
```sh
docker stop quiz_container
```

### 4️⃣ Verify Running Containers
Check if your container is running:
```sh
docker ps
```
To see all containers (including stopped ones):
```sh
docker ps -a
```

## Troubleshooting
- If text extraction fails, check if Tesseract is installed and correctly configured.
- If the Gemini API key is missing, ensure it is correctly set in the `.env` file.
- If the script crashes, verify that dependencies are installed.

## License
This project is open-source under the MIT License.

