# Flashcard Generator CLI

## Overview
This is a command-line application that generates flashcards from text input, images, or PDFs using Google Gemini AI. Users can provide text manually or upload files, and the application extracts key concepts to create question-answer flashcards.

## Features
- Extracts text from images and PDFs using Tesseract OCR.
- Generates flashcards automatically using Google Gemini AI.
- Provides an interactive experience with letter-by-letter text streaming.
- Supports multi-line text input and file uploads.
- Displays generated flashcards in a structured format.

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
   python flashcard_generator.py
   ```
2. Follow the prompts to enter text or upload an image/PDF.
3. The application will generate flashcards based on the extracted content.
4. View the generated flashcards in the terminal.

## Example Interaction
```
Welcome to the Flashcard Generator!
1. Enter text input
2. Upload a file
Enter your choice (1 or 2): 1

Enter the text for flashcards (type 'END' on a new line to finish):
Artificial Intelligence is the simulation of human intelligence in machines.
END

Generating flashcards...
Q: What is Artificial Intelligence?
A: The simulation of human intelligence in machines.
```

## Running with Docker
You can also run the application inside a Docker container.

### 1️⃣ Build the Docker Image
Navigate to the project directory where the `Dockerfile` is located and run:
```sh
docker build -t flashcard-generator .
docker run -it --rm -v "$(pwd)/uploads:/app/uploads" flashcard-generator

```

### 2️⃣ Run the Docker Container
To start the container:
```sh
docker run -it --rm -v "$(pwd)/uploads:/app/uploads" flashcard-generator
```


```
To stop the container:
```sh
docker stop flashcard_container
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

