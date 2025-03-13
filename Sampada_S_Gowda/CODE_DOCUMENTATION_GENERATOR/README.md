# Code Documentation Generator

## Overview
The Code Documentation Generator is a terminal-based application that automates the generation of structured documentation for codebases. It analyzes source code, extracts relevant information, and formats it into well-structured documentation. The project utilizes the **Gemini AI API** to enhance documentation with AI-powered explanations.

## Features
- Automatically generate documentation for functions, classes, and modules.
- Extract docstrings and generate summaries for code.
- Save and view generated documentation.
- Download documentation as a text or PDF file.
- Interactive terminal-based interface.

## Tech Stack
- **Python 3.9**
- **Google Gemini AI API**
- **Docker** (for containerization)
- **dotenv** (for environment variables management)

## Installation
### Prerequisites
- **Python 3.9+** installed on your machine
- **Docker** installed (optional for containerized deployment)

### Clone the Repository
```sh
git clone https://github.com/your-repo/code-doc-generator.git
cd code-doc-generator
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
python code_class.py
```
Follow the on-screen prompts to generate documentation for your codebase.

## Docker Setup
### Build and Run the Docker Container
```sh
docker build -t code-doc-generator .
docker run -it --rm -v "$(pwd)/uploads:/app/uploads" code-doc-generator
```

## Environment Variables
| Variable          | Description                   |
|------------------|------------------------------|
| GEMINI_API_KEY   | API key for Google Gemini AI |

## Project Structure
```
📂 code-doc-generator
│-- 📂 app
│   │-- code_class.py
│   │-- requirements.txt
│   │-- .env (not included in repo)
│-- Dockerfile
│-- README.md
```



