import os
import asyncio
from typing import Optional, Tuple, Dict, AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

@dataclass
class WritingRequest:
    """Data class to hold writing request parameters"""
    role: str
    field: str
    service_type: str
    document_type: str
    text: str

class AcademicWritingConfig:
    """Configuration class for Academic Writing Assistant"""
    ROLES = [
        "Student (Undergraduate)", 
        "Student (Graduate)", 
        "Student (PhD)", 
        "Researcher", 
        "Professor", 
        "Professional", 
        "Other"
    ]
    
    FIELDS = [
        "Sciences", 
        "Humanities", 
        "Engineering", 
        "Business", 
        "Other"
    ]
    
    SERVICE_TYPES = [
        "Improve Writing", 
        "Research & Cite", 
        "Help Me Write", 
        "Fix Grammar Issues"
    ]
    
    DOCUMENT_TYPES = [
        "Essay", 
        "Thesis", 
        "Research Paper", 
        "Report", 
        "Dissertation", 
        "Other"
    ]

    @staticmethod
    def get_prompt_template() -> str:
        """Returns the prompt template for the LLM"""
        return '''
        USER INPUT
        Current Role: {role}
        Field of Study: {field}
        Service Type: {service_type}
        Document Type: {document_type}
        Text: {text}

        SYSTEM PROMPT
        As an academic writing assistant, analyze the provided text based on the user's role {role}, field {field}, and requested service {service_type} for their {document_type}. Focus on providing tailored feedback following these guidelines:

        For Improve Writing:
        - Evaluate structure and flow
        - Assess academic tone
        - Review argument strength
        - Check clarity and concision

        For Research & Cite:
        - Review research methodology
        - Check citation format
        - Evaluate literature integration
        - Verify reference accuracy

        For Help Me Write:
        - Analyze outline structure
        - Evaluate thesis clarity
        - Review argument development
        - Assess content organization

        For Fix Grammar Issues:
        - Identify grammar errors
        - Review punctuation
        - Check sentence structure
        - Suggest word choice improvements

        Provide feedback in this structure:
        1. Initial Assessment (2-3 sentences)
        2. Specific Improvements (bullet points)
        3. Next Steps (2-3 action items)

        Remember:
        - Maintain academic integrity
        - Focus on teaching
        - Provide specific examples
        - Keep feedback constructive
        '''

class InputValidator:
    """Class for handling input validation"""
    
    @staticmethod
    def validate_request(request: WritingRequest) -> Tuple[bool, str]:
        """Validate all inputs before processing"""
        if not all([
            request.role, 
            request.field, 
            request.service_type, 
            request.document_type, 
            request.text
        ]):
            return False, "All fields are required. Please fill in missing information."
        return True, ""

def get_user_choice(options: list, prompt: str) -> str:
    """Helper function to get user choice from a list of options"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")

def get_user_text() -> str:
    """Helper function to get multiline text input from user"""
    print("\nEnter your text (press Ctrl+D on Unix/Linux or Ctrl+Z on Windows + Enter when finished):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)

class AcademicWritingAssistant:
    """Main class for handling academic writing assistance"""
    
    def __init__(self):
        """Initialize the Academic Writing Assistant"""
        load_dotenv()
        self.api_key = os.environ['GOOGLE_API_KEY']
        self.llm = GoogleGenerativeAI(
            model='gemini-2.0-flash',
            temperature=0.9,
            api_key=self.api_key
        )
        self.prompt_template = PromptTemplate.from_template(
            AcademicWritingConfig.get_prompt_template()
        )
        self.validator = InputValidator()

    async def aprocess_request(self, request: WritingRequest) -> AsyncIterator[str]:
        """Process academic writing request with streaming"""
        # Validate inputs
        is_valid, error_message = self.validator.validate_request(request)
        if not is_valid:
            yield error_message
            return

        # Format the prompt
        formatted_prompt = self.prompt_template.format(
            role=request.role,
            field=request.field,
            service_type=request.service_type,
            document_type=request.document_type,
            text=request.text
        )

        try:
            # Stream the response directly from the LLM
            async for chunk in self.llm.astream(formatted_prompt):
                yield chunk
        except Exception as e:
            yield f"Error during processing: {str(e)}"

async def main():
    """Example usage of the Academic Writing Assistant with user input"""
    # Initialize the assistant
    assistant = AcademicWritingAssistant()

    print("Welcome to the Academic Writing Assistant!")
    
    # Get user inputs for all parameters
    role = get_user_choice(
        AcademicWritingConfig.ROLES,
        "What is your role?"
    )
    
    field = get_user_choice(
        AcademicWritingConfig.FIELDS,
        "What is your field of study?"
    )
    
    service_type = get_user_choice(
        AcademicWritingConfig.SERVICE_TYPES,
        "What type of service do you need?"
    )
    
    document_type = get_user_choice(
        AcademicWritingConfig.DOCUMENT_TYPES,
        "What type of document are you working on?"
    )
    
    text = get_user_text()

    # Create request with user inputs
    request = WritingRequest(
        role=role,
        field=field,
        service_type=service_type,
        document_type=document_type,
        text=text
    )

    print("\nAnalyzing your text...\n")
    
    # Process the request with streaming
    async for chunk in assistant.aprocess_request(request):
        print(chunk, end='', flush=True)
    print("\n\nAnalysis complete!")

if __name__ == "__main__":
    asyncio.run(main())