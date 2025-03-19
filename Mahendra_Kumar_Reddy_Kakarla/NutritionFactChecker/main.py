import os
import sys
import yaml
import argparse
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
"""
Nutrition Fact Checker

This script extracts nutritional facts from product information or images. It uses Google's Gemini AI model to generate nutrition facts based on the provided product details. The script supports:
- Extracting nutrition facts from product images.
- Extracting nutrition facts from product names and company details.
- Using API credentials from a YAML configuration file.

Usage:
    python script.py --product_Name "Product1" "Product2" --company_name "Company1" "Company2"
"""


class NutritionFactChecker:
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
    def get_nf_from_image(self):
        """
        Extract nutritional facts from product images stored in the 'images' directory.
        
        The function iterates through images, processes them using the Gemini AI model,
        and returns a summary of extracted nutrition facts.
        """
        prompt = """
        As a nutritional expert, please extract the nutritional facts from the following product information using reliable online sources and your knowledge of well-known brands' nutrition profiles:
        
        If specific nutritional information is not available from these sources, provide general nutritional information for the product, including calories, fat, carbs, protein, sugar, sodium, and fiber content. If any of these values are not available, please indicate "Not available".
        
        Guideline: if it is not a food item return politely.
        For example:
        Product Name: extract from image
        - Calories: Not available
        - Fat: Not available
        - Carbs: Not available
        - Protein: Not available
        - Sugar: Not available
        - Sodium: Not available
        - Fiber: Not available
        """
        
        image_summaries = []  # List to store image processing results
        image_dir = "images"  # Directory where images are stored
        
        if not os.path.exists(image_dir):
            return "Images folder not found. Ensure 'images/' is mounted."
        
        # Iterate through images in the directory
        for image_name in os.listdir(image_dir):
            if image_name.lower().endswith((".jpg", ".jpeg")):
                image_path = os.path.join(image_dir, image_name)
                image_base64 = Image.open(image_path)  # Open image using PIL
                
                # Generate nutritional facts using AI model
                response = self.model.generate_content([image_base64, prompt])
                summary = response.text if response else "No summary generated."
                
                # Store the result in the list
                image_summaries.append(f"{image_name}: {summary}")
        
        return "\n".join(image_summaries) if image_summaries else "No valid images found."
    
    def get_nf_from_product_info(self, product_info):
        """
        Extract nutritional facts from product name, company details, and description.
        
        Uses Gemini AI model to generate nutritional information based on product details.
        """
        prompt = f"""
        As a nutritional expert, please extract the nutritional facts from the following product information using reliable online sources and your knowledge of well-known brands' nutrition profiles:
    
        {product_info}
    
        If specific nutritional information is not available from these sources, provide general nutritional information for the product, including calories, fat, carbs, protein, sugar, sodium, and fiber content. If any of these values are not available, please indicate "Not available".
    
        For example:
        - Calories: Not available
        - Fat: Not available
        - Carbs: Not available
        - Protein: Not available
        - Sugar: Not available
        - Sodium: Not available
        - Fiber: Not available
        """
        
        response = self.model.generate_content(prompt)  # Generate content from the AI model
        return response.text  # Return the AI-generated response
    
if __name__ == "__main__":
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Nutrition Fact Checker - Extracts nutrition details from product information or images.")
    parser.add_argument("task", type=str, help="Task to execute: get_nf_from_product_info,get_nf_from_image")
    parser.add_argument("--product_Name",  type=str, help="Product name (list)")
    parser.add_argument("--company_name",  type=str, help="Company name (list)")
    parser.add_argument("--description", type=str, help="Description of the product")
    
    args = parser.parse_args()
    
    # Instantiate the NutritionFactChecker class
    checker = NutritionFactChecker()
    
    # Execute tasks based on user input
    if args.task == "get_nf_from_image":
        response = checker.get_nf_from_image()
        print(response)  # Print the response from image processing
    elif args.task == "get_nf_from_product_info":
        # Combine product name, company name, and description for AI processing
        response = checker.get_nf_from_product_info(" ".join([args.product_Name, args.company_name, args.description]))
        print(response)  # Print the response from product info processing