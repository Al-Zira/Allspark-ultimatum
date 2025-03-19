import sys
import os
import PyPDF2  # Library for reading PDF files
import docx  # Library for reading DOCX files
import asyncio  # Library for asynchronous operations
import google.generativeai as genai  # Google AI model for processing contracts
import yaml  # Library for parsing YAML configuration files
from dotenv import load_dotenv
load_dotenv()
# Path to the configuration file containing credentials


class ContractAnalyzer:
    def __init__(self, file_name):
        # Define the folder where contract files are stored (inside a container)
        self.contracts_folder = "/contracts"  
        self.file_path = os.path.join(self.contracts_folder, file_name)

        # Check if the contract file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File '{file_name}' not found in {self.contracts_folder}.")

        # Read the content of the contract file
        self.file_content = self._read_file()
        if not self.file_content:  # Ensure the contract is not empty
            raise ValueError("Error: The contract file is empty.")

        # Initialize the Google AI model for contract analysis
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
    
    def _read_file(self):
        """Determines the file type and reads its content accordingly."""
        file_ext = os.path.splitext(self.file_path)[1].lower()  # Extract file extension
        if file_ext == ".pdf":
            return self._read_pdf()  # Read PDF file
        elif file_ext in [".doc", ".docx"]:
            return self._read_docx()  # Read DOCX file
        else:
            raise ValueError("Unsupported file format.")  # Raise error for unsupported formats

    def _read_pdf(self):
        """Extracts text content from a PDF file."""
        text = ""
        try:
            with open(self.file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)  # Initialize PDF reader
                for page in reader.pages:
                    page_text = page.extract_text()  # Extract text from each page
                    if page_text:
                        text += page_text + "\n"  # Append extracted text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")  # Handle PDF reading errors
        return text.strip()  # Return cleaned text

    def _read_docx(self):
        """Extracts text content from a DOCX file."""
        try:
            doc = docx.Document(self.file_path)  # Open DOCX file
            return "\n".join([para.text for para in doc.paragraphs]).strip()  # Extract text
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {e}")  # Handle DOCX reading errors

    def analyze_contract(self):
        """Processes the contract using AI and provides a legal review."""
        prompt = f"""
        contract: {self.file_content}
        Reviews above legal contract and highlights areas that require attention or possible negotiation points.
        
        1. Clauses that may be unfavorable to the user.
        2. Clauses that may be ambiguous or open to interpretation.
        3. Clauses that may have legal implications or risks.
        4. Clauses that may be outdated or irrelevant in the current legal landscape.
        5. Any other areas that may require attention or negotiation.
        6. Summarize the main points of the contract in a few sentences.

        Don't give a deep explanation of each above point; just give a short summary of each point and the specific clause that falls under that point.

        Please provide a detailed analysis in markdown format.
        """
        try:
            response = self.model.generate_content(prompt)  # Generate AI response
            return response.text  # Return analyzed contract text
        except Exception as e:
            raise RuntimeError(f"Error during AI processing: {e}")  # Handle AI processing errors

async def get_review():
    """Main function to get contract review asynchronously."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_name>")  # Ensure correct usage
        sys.exit(1)

    file_name = sys.argv[1]  # Get the filename from command-line arguments

    try:
        analyzer = ContractAnalyzer(file_name)  # Initialize contract analyzer
        analysis = analyzer.analyze_contract()  # Perform contract analysis
        print(analysis)  # Print the result
    except Exception as e:
        print(f"Error: {e}")  # Handle exceptions and print error messages

if __name__ == "__main__":
    asyncio.run(get_review())  # Run the asynchronous function