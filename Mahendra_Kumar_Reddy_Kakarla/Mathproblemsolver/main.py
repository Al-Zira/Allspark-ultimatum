import os
import sys
import yaml
import argparse
from google.generativeai import GenerativeModel
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

"""
Math Problem Solver

This script solves math problems from either text input or images. It uses Google's Gemini AI model to generate step-by-step solutions based on the provided math problems. The script supports:
- Extracting and solving math problems from images.
- Solving math problems provided as text input.
- Using API credentials from a YAML configuration file.

Usage:
    python script.py get_answer_for_text --question "What is the integral of x^2?"
    python script.py get_answer_from_image
"""



class MathProblemSolver:
    def __init__(self):
        # Initialize the Google Generative AI model with Gemini 2.0 Flash
        self.api_key=self._load_api_key()
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    

    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    def get_answer_from_image(self):
        """
        Extract and solve mathematical problems from images stored in the 'images' directory.
        
        The function processes images, extracts math-related content, and solves the problem step by step.
        """
        prompt = """
        You are a professional mathematics problem solver. Analyze the given image and extract the math problem. Then, provide a step-by-step solution using standard mathematical methods.
        
        Ensure that:
        - The solution is accurate and well-explained.
        - Only legitimate mathematical problems are solved.
        - If the image does not contain a math problem, respond with: "No valid math problem detected in the image."
        """
        
        image_summaries = []  # List to store image processing results
        image_dir = "images"  # Directory where images are stored
        
        if not os.path.exists(image_dir):
            return "Images folder not found. Ensure 'images/' is mounted."
        
        # Iterate through images in the directory
        for image_name in os.listdir(image_dir):
            if image_name.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(image_dir, image_name)
                image_base64 = Image.open(image_path)  # Open image using PIL
                
                # Generate solution using AI model
                response = self.model.generate_content([image_base64, prompt])
                summary = response.text if response else "No summary generated."
                
                # Store the result in the list
                image_summaries.append(f"{image_name}: {summary}")
        
        return "\n".join(image_summaries) if image_summaries else "No valid images found."
    
    def get_answer_for_text(self, question):
        """
        Solve a math problem given as text input.
        
        Uses Gemini AI model to generate a step-by-step solution based on the provided problem.
        """
        prompt = f"""
        You are an expert mathematics problem solver. Please solve the following problem with detailed, step-by-step explanations:
        
        **Problem**: {question}
        
        **Solution**:
        - Ensure the solution follows proper mathematical rules and methods.
        - If the question is unrelated to math, respond with: "I'm here to assist with math-related questions only. Feel free to ask about Algebra, Calculus, Trigonometry, or other math topics."
        """
        
        response = self.model.generate_content(prompt)  # Generate content from the AI model
        return response.text if response else "Error generating response."
    
if __name__ == "__main__":
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Math Problem Solver - Solves math problems from text input or images.")
    parser.add_argument("task", type=str, help="Task to execute: get_answer_for_text, get_answer_from_image")
    parser.add_argument("--question", type=str, help="Math question/problem (for text input).", required=False)
    
    args = parser.parse_args()
    
    # Instantiate the MathProblemSolver class
    solver = MathProblemSolver()
    
    # Execute tasks based on user input
    if args.task == "get_answer_for_text":
        if not args.question:
            print("Error: --question argument is required for get_answer_for_text task.")
            sys.exit(1)
        response = solver.get_answer_for_text(args.question)
    elif args.task == "get_answer_from_image":
        response = solver.get_answer_from_image()
    else:
        print("Error: Invalid task specified. Use 'get_answer_for_text' or 'get_answer_from_image'.")
        sys.exit(1)
    
    print(response)  # Print the generated response
