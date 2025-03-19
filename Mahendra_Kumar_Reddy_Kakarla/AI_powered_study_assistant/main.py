import yaml
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
from PIL import Image
import sys
import asyncio
from dotenv import load_dotenv
load_dotenv()


class AIProcessor:
    """
    AIProcessor class handles various AI-related tasks using the Google Generative AI model.
    """
    def __init__(self):
        # Initialize the model instance
        self.api_key=self._load_api_key()
        self.model = GenerativeModel("gemini-2.0-flash")
    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    def image_summary(self, prompt="Describe the image in detail."):
        """
        Generates a detailed summary for each image in the 'images/' directory.
        """
        image_summaries = []
        image_dir = "images"  # Directory containing images
        if not os.path.exists(image_dir):
            return "Images folder not found. Ensure 'images/' is mounted."
        
        for image_name in os.listdir(image_dir):
            if image_name.lower().endswith((".jpg", ".jpeg")):
                image_path = os.path.join(image_dir, image_name)
                image_base64 = Image.open(image_path)  # Open the image
                response = self.model.generate_content([image_base64, prompt])  # Generate image description
                summary = response.text if response else "No summary generated."
                image_summaries.append(f"{image_name}: {summary}")
        
        return "\n".join(image_summaries) if image_summaries else "No valid images found."

    def text_summary(self, text, prompt="Summarize the text in detail."):
        """
        Generates a summary for a given text.
        """
        response = self.model.generate_content([text, prompt])
        return response.text if response else "No summary generated."

    def find_resources(self, topic):
        """
        Finds useful resources such as articles, videos, and links related to the given topic.
        """
        if not topic.strip():
            return "Please enter a valid topic."
        prompt = f"List all the useful resources, articles, YouTube videos, and links related to the topic: \"{topic}\" in markdown format."
        response = self.model.generate_content(prompt)
        return response.text if response else "No resources found."

    async def generate_test_and_evaluate(self, prompt):
        """
        Generates a multiple-choice test based on the given prompt and evaluates the user's answers.
        """
        if not prompt.strip():
            return "Please enter a valid prompt."

        # Generate test questions
        test_prompt = f"Generate a multiple-choice, one-line, and fill-in-the-blanks test with some questions based on the following prompt: \"{prompt}\" in markdown format."
        response = self.model.generate_content(test_prompt)
        test_questions = response.text if response else "No test generated."

        print("Generated Test Questions:")
        print(test_questions)

        # Wait for user input (answers)
        user_answers = await asyncio.to_thread(input, "\nEnter your answers separated by (,): ")

        # Evaluate the answers based on the test generated
        eval_prompt = f"Evaluate the user's answers and provide a score. Also, return the correct answers. Here are the questions: {test_questions} and here are the user answers: {user_answers}. If answers are not correct or there are no answers, give a score accordingly. Rule: First give score, then provide feedback."
        eval_response = self.model.generate_content(eval_prompt)

        return eval_response.text if eval_response else "No evaluation generated."

if __name__ == "__main__":
    import argparse
    
    # Argument parser for command-line interaction
    parser = argparse.ArgumentParser(description="AI Task Processor")
    parser.add_argument("task", type=str, help="Task to execute: text_summary, image_summary, find_resources, generate_test, evaluate_answers")
    parser.add_argument("--input", type=str, help="Input text or image name", required=False)
    parser.add_argument("--prompt", type=str, default="", help="Prompt text for the task")
    parser.add_argument("--answers", type=str, help="User answers for evaluation", required=False)
    
    args = parser.parse_args()
    processor = AIProcessor()
    
    # Handle different task types based on user input
    if args.task == "text_summary":
        print(processor.text_summary(args.input, args.prompt))
    elif args.task == "image_summary":
        print(processor.image_summary(args.prompt))
    elif args.task == "find_resources":
        print(processor.find_resources(args.input))
    elif args.task == "generate_test_and_evaluate":
        print(asyncio.run(processor.generate_test_and_evaluate(args.input)))
    else:
        print("Invalid task. Choose from: text_summary, image_summary, find_resources, generate_test, evaluate_answers.")