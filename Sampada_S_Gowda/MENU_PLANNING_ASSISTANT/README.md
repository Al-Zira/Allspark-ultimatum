# Menu Planning Assistant

## Overview
The Menu Planning Assistant is a Python-based tool that generates personalized meal plans based on user inputs such as age, weight, height, gender, activity level, dietary preferences, allergies, and medical conditions. It utilizes the Gemini AI model to generate meal plans and suggest meal times and supplements.

## Features
- Calculates daily caloric and macronutrient requirements.
- Generates a 7-day meal plan tailored to user needs.
- Provides supplement recommendations.
- Suggests meal timings.
- Saves the meal plan to a text file.
- Streams the output in a user-friendly manner.

## Prerequisites
- Python 3.8+
- Google Generative AI API Key
- Docker (if running in a containerized environment)

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/menu-planning-assistant.git
cd menu-planning-assistant
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root and add:
```env
GEMINI_API_KEY=your_api_key_here
```

## Usage
Run the script using:
```bash
python menu_class.py
```
Follow the prompts to enter personal details and generate a customized meal plan.

## Running with Docker
### 1. Build the Docker Image
```bash
docker build -t menu-planning-assistant .
```

### 2. Run the Container
```bash
docker run --env-file .env -it menu-planning-assistant
```

## Project Structure
```
menu-planning-assistant/
│── menu_class.py      # Main script
│── requirements.txt     # Dependencies
│── Dockerfile           # Docker setup
│── .env                 # API Key (not included in repo)
│── README.md            # Documentation
```



