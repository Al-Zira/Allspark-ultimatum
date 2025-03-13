# Educational Content Summarizer

## Overview
The Educational Content Summarizer is an AI-powered tool that extracts and summarizes key points from educational materials, including text, images, and PDFs. It uses the **Gemini AI API** to generate concise and meaningful summaries to enhance learning efficiency.

## Features
- Extracts text from educational documents and images using **Tesseract OCR**.
- Generates structured summaries with key points using **Gemini AI**.
- Supports multiple formats: **text, PDFs, and images**.
- Provides AI-enhanced explanations for complex topics.
- Allows **image classification** using **MobileNetV2**.
- Compares two PDFs to identify key differences and similarities.
- Generates **multiple-choice quizzes** based on extracted content.
- Interactive and user-friendly **command-line interface**.

## Tech Stack
- **Python 3.9**
- **Google Gemini AI API**
- **Tesseract OCR** (for text extraction from images)
- **TensorFlow & MobileNetV2** (for image classification)
- **PyPDF2 & pdf2image** (for PDF text and image extraction)
- **Flask & Gradio** (for potential UI integration)

## Installation
### Prerequisites
- **Python 3.9+** installed on your machine
- **Tesseract OCR** installed (for image text extraction)

### Clone the Repository
```sh
git clone https://github.com/your-repo/edu-content-summarizer.git
cd edu-content-summarizer
```

### Setup Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Set Up API Key
Create a `.env` file in the project root and add:
```sh
GEMINI_API_KEY=your_api_key_here
```

## Usage
Run the application with:
```sh
python app/edu_class.py
```
Follow the on-screen prompts to:
1. **Process multiple images**: Extract text or classify objects in images.
2. **Process multiple PDFs**: Summarize text-based and image-based PDFs.
3. **Compare two PDFs**: Analyze differences and similarities.
4. **Generate quizzes**: Create multiple-choice quizzes from extracted content.

## Docker Deployment
You can also run the application using Docker.

### Build and Run the Docker Container
```sh
docker build -t edu-content-summarizer .
docker run -it --rm -v "$(pwd)/uploads:/app/uploads" edu-content-summarizer
```

## Project Structure
```
📂 edu-content-summarizer
│-- 📂 app
│   │-- edu_class.py
│   │-- imagent_class.json
│   │-- requirements.txt
│   │-- .env (not included in repo)
│-- Dockerfile
│-- README.md
```



