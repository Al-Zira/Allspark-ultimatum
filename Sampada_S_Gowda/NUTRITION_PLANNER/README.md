# Nutrition Planner CLI

## Description
The Nutrition Planner CLI is a command-line tool that generates personalized daily meal plans based on user input. It leverages the Gemini AI model to suggest meal options tailored to an individual's age, weight, height, gender, activity level, health goals, allergies, dietary preferences, and medical conditions.

## Features
- Accepts user input for personalized meal planning.
- Uses the Gemini AI API to generate meal plans.
- Simulates letter-by-letter streaming of responses.
- Suggests meal timings for better scheduling.

## Prerequisites
- Python 3.7+
- A Gemini AI API key
- Required Python libraries: `google-generativeai`, `python-dotenv`

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/nutrition-planner-cli.git
   cd nutrition-planner-cli
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up your `.env` file:
   ```sh
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
   Replace `your_api_key_here` with your actual Gemini AI API key.

## Usage
Run the CLI application:
```sh
python nutrition_class.py
```
Follow the on-screen prompts to enter your details and receive a personalized meal plan.

## Environment Variables
The application uses a `.env` file to store the Gemini API key. Ensure your `.env` file is set up correctly before running the program.

## Example Input & Output
### Input:
```
Enter your age: 25
Enter your weight (kg): 70
Enter your height (cm): 175
Enter your gender (male/female): male
Enter your activity level (sedentary, light, moderate, intense, very_intense): moderate
Enter your health goal (weight_loss, muscle_gain, maintenance): muscle_gain
Enter any allergies (comma-separated): nuts, dairy
Enter your dietary preference (vegan, vegetarian, non-vegetarian): non-vegetarian
Enter any medical conditions (comma-separated): none
```

### Output (Example):
```
Generating meal plan...
Breakfast Option 1: Scrambled eggs with whole wheat toast and avocado.
Breakfast Option 2: Greek yogurt with granola and mixed berries (Dairy-Free Alternative: Coconut Yogurt).
Breakfast Option 3: Protein smoothie with banana, oats, and almond milk.
...

Suggested Meal Times:
Breakfast: 7:00 AM - 9:00 AM
Lunch: 12:00 PM - 2:00 PM
Dinner: 6:00 PM - 8:00 PM
Snacks: 10:00 AM - 11:00 AM or 3:00 PM - 4:00 PM
```
  ```

## Running with Docker
### 1. Build the Docker Image
```bash
docker build -t nutrition_planner .
```

### 2. Run the Container
```bash
docker run --env-file .env -it nutrition_planner



