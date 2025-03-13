import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found. Please set it in the .env file.")

# Configure Gemini API
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # Use the correct Gemini model name
    generation_config={
        "temperature": 0.7,
        "top_p": 0.9,
        "max_output_tokens": 2048,
    },
)

def generate_documentation_for_code(code_snippet):
    """
    Generates documentation and code explanation for the provided code snippet using Gemini AI.
    """
    prompt = f"""
    Generate detailed documentation and explanation for the following code. Include the following sections:
    - Description: An overview of what the code does.
    - Examples: How to run the application or use the code.
    - Dependencies: List any necessary dependencies.
    - Error Handling: Common errors and how they are handled.
    - Usage Scenarios: Real-world scenarios for using this code.
    {code_snippet}
    """
    
    try:
        # Generate content from Gemini model
        response = model.generate_content(prompt)
        
        # Extract and format the documentation content from the response
        if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
            documentation = response.candidates[0].content
            if isinstance(documentation, str):
                return documentation.replace("*", "").strip()
            elif hasattr(documentation, 'parts') and len(documentation.parts) > 0:
                return documentation.parts[0].text.replace("*", "").strip()
            else:
                return "No documentation generated."
        else:
            return "No documentation generated."
    except Exception as e:
        return f"Error generating documentation: {str(e)}"

def process_code_input(code_input):
    """
    Processes the input code provided by the user and generates documentation and explanations.
    """
    if not code_input.strip():
        return "No code provided."
    
    # Generate documentation using Gemini API
    documentation = generate_documentation_for_code(code_input)
    return documentation

def process_uploaded_file(file_path):
    """
    Processes the uploaded code file and generates documentation and explanations.
    """
    try:
        # Get the upload folder from environment variable, default to '/app/uploads'
        upload_folder = os.getenv('UPLOAD_FOLDER', '/app/uploads')
        
        # Ensure the file path is within the container's accessible directory
        full_file_path = os.path.join(upload_folder, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            return f"File not found: {full_file_path}"
        
        # Open the file using the file path
        with open(full_file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()  # Read the file content as a string
        
        # Generate documentation using Gemini API
        documentation = generate_documentation_for_code(code_content)
        return documentation
    except Exception as e:
        return f"Failed to process file {file_path}: {str(e)}"

def download_documentation(documentation):
    """
    Saves the generated documentation to a README.md file.
    """
    output_file = "README.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print(f"Documentation saved to {output_file}")

def stream_output(output_text, delay=0.05):
    """
    Stream output letter by letter with a delay between each character.
    """
    for char in output_text:
        print(char, end='', flush=True)
        time.sleep(delay)

# Command-line interface for code input or file upload
def main():
    print("Code Documentation Generator")
    print("Choose an option:")
    print("1. Enter Code Snippet")
    print("2. Upload Code File")
    
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print("Enter your code snippet. Type 'DONE' to finish entering the code.")
        
        code_lines = []
        while True:
            line = input()  # Accepts input line-by-line
            if line.strip().lower() == "done":  # Stop when user types 'DONE'
                break
            code_lines.append(line)
        
        # Join the lines into a single code snippet
        code_input = "\n".join(code_lines)
        
        documentation = process_code_input(code_input)
        
        # Stream the generated documentation letter by letter
        print("\nGenerated Documentation:\n")
        stream_output(documentation)
        
        save_choice = input("\nDo you want to save the documentation to a README.md file? (yes/no): ").strip().lower()
        if save_choice == "yes":
            download_documentation(documentation)
    
    elif choice == "2":
        file_path = input("Enter the file name of your code file (ensure it is in the /app/uploads directory): ").strip()
        documentation = process_uploaded_file(file_path)
        
        # Stream the documentation letter by letter
        print("\nGenerated Documentation:\n")
        stream_output(documentation)
        
        save_choice = input("\nDo you want to save the documentation to a README.md file? (yes/no): ").strip().lower()
        if save_choice == "yes":
            download_documentation(documentation)
    
    else:
        print("Invalid choice. Exiting.")
        return

if __name__ == "__main__":
    main()
