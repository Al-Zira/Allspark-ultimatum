# Recipe Cost Estimator

## Overview
The Recipe Cost Estimator is a command-line application that generates unique recipes, estimates ingredient costs in INR, and converts the total cost to USD. It utilizes Google Gemini AI for recipe generation and cost estimation.

## Features
- Generates unique recipes based on the dish name.
- Estimates ingredient costs in INR and converts them to USD.
- Adjusts ingredient quantities based on the number of servings.
- Provides a dynamic letter-by-letter output simulation for a realistic effect.

## Prerequisites
Ensure the following dependencies are installed:
- Python 3.x
- Required Python packages:
  ```sh
  pip install google-generativeai python-dotenv
  ```
- Google Gemini API key (Set in a `.env` file)

## Setup
1. Clone the repository or download the script.
2. Create a `.env` file in the project directory and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage
1. Run the script:
   ```sh
   python script.py
   ```
2. Enter the name of the dish.
3. Specify the number of servings.
4. View the generated recipe with estimated costs.

## Example Interaction
```
Welcome to the Recipe Cost Estimator!
Enter the name of the dish: Pasta
Enter the number of servings: 2

Generating recipe...
...
Total Cost: 150 INR (1.81 USD)
```

## Running with Docker
You can also run the application inside a Docker container.

### 1️⃣ Build the Docker Image
Navigate to the project directory where the `Dockerfile` is located and run:
```sh
docker build -t recipe-cost-estimator .
```

### 2️⃣ Run the Docker Container
To start the container:
```sh
docker run --rm -it recipe-cost-estimator
```

### 3️⃣ Run in Detached Mode (Optional)
If you want to run the container in the background:
```sh
docker run -d --name recipe_container recipe-cost-estimator
```
To stop the container:
```sh
docker stop recipe_container
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
- If API calls fail, ensure the Gemini API key is correctly set in the `.env` file.
- If the script crashes, check that dependencies are installed properly.
- If the letter-by-letter output is slow, adjust the sleep time in the script.

## License
This project is open-source under the MIT License.

