# Wine Pairing Generator

This project uses Google's Gemini AI to suggest wine pairings for various food items. The AI model provides recommendations for different wine categories, including Red Wine, White Wine, Rosé Wine, Sparkling Wine, and Dessert Wine.

## Project Structure
```
📂 wine_pairing_tool
│-- 📂 app
│   │-- wine_class.py
│   │-- requirements.txt
│   │-- .env (not included in repo)
│-- Dockerfile
│-- README.md
```

## Prerequisites
- Python 3.8+
- Google Gemini API key
- Docker (if running inside a container)

## Installation

1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd code-doc-generator/app
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `app` directory and add your Google Gemini API key:
   ```sh
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Application

Execute the script using:
```sh
python wine_class.py
```

The program will prompt you to enter food items and generate wine pairings accordingly.

## Docker Setup

1. Build the Docker image:
   ```sh
   docker build -t wine-pairing-app .
   ```

2. Run the Docker container:
   ```sh
   docker run --rm -it --env-file .env wine-pairing-app
   ```

## Usage
Once the application is running, enter a list of food items (comma-separated) and receive wine pairing suggestions in a streaming format.


