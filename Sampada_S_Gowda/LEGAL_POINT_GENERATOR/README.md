
# Legal Point Generator

## Overview
The **Legal Point Generator** is a terminal-based application designed to analyze legal documents and generate structured legal arguments using **Google Gemini AI**. It supports PDF, image, and text file inputs, extracting key legal points and formulating arguments based on precedents and case laws.

## Features
- Extracts text from PDFs, images (OCR), and text files.
- Generates legal arguments with structured analysis.
- Provides legal issue summaries, key arguments, and references.
- Supports interactive terminal-based usage.
- Streams generated responses dynamically for a smooth user experience.

## Tech Stack
- **Python 3.9**
- **Google Gemini AI API**
- **PyPDF2** (for PDF text extraction)
- **Pillow & pytesseract** (for OCR image text extraction)
- **dotenv** (for environment variable management)

## Installation
### Prerequisites
- **Python 3.9+** installed on your machine

### Clone the Repository
```sh
git clone https://github.com/your-repo/legal-point-generator.git
cd legal-point-generator
```

### Setup Virtual Environment
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
python main.py
```
Follow the on-screen prompts to:
1. Upload a PDF, image, or text file.
2. Manually enter legal text.
3. Receive a generated legal argument based on the input.

## Environment Variables
| Variable          | Description                   |
|------------------|------------------------------|
| GEMINI_API_KEY   | API key for Google Gemini AI |



