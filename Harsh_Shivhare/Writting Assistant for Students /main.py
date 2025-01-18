import os
import re
import time
import sys
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Create an instance of the LLM
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

def remove_markdown(text: str) -> str:
    """
    Remove markdown formatting from text.
    """
    
    # Remove headers
    text = re.sub(r'#+\s*', '', text)
    # Remove bold/italic
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
    # Remove bullet points
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def format_text(text: str) -> str:
    """
    Format text into clean paragraphs without markdown.
    """
    clean_text = remove_markdown(text)
    
    # Split into paragraphs and clean up
    paragraphs = clean_text.split('\n')
    formatted_text = "\n\n".join(p.strip() for p in paragraphs if p.strip())
    
    return formatted_text

class StreamPrinter:
    """Handles streaming output with typewriter effect"""
    def __init__(self, delay: float = 0.02):
        self.delay = delay

    def print_stream(self, text_generator):
        """Print text with a typewriter effect from a generator"""
        for chunk in text_generator:
            for char in chunk:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(self.delay)

class WritingAssistant:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate.from_template('''
            You are a Writing Assistant AI helping with a {ASSIGNMENT_TYPE} in {SUBJECT} at {ACADEMIC_LEVEL} level.
            Length requirement: Approximately {WORD_COUNT} words.
            Special requirements: {REQUIREMENTS}

            Please provide structured feedback in clear paragraphs:

            1. Suggestions for structure and organization
            2. Content improvement recommendations
            3. Grammar and style feedback
            4. Specific examples to illustrate points

            Guidelines:
            - Assist in improving the content
            - Explain your suggestions clearly
            - Maintain academic integrity
            - Keep the student's original voice

            Topic or current work:
            {topic}

            What aspects would you like to improve?
            ''')
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, output_parser=StrOutputParser())
    
    def stream_response(self, inputs: dict) -> str:
        """Stream the response from the LLM chain"""
        response = ''
        for chunk in self.chain.stream(inputs):
            if chunk.get('text'):
                response += chunk['text']
                yield chunk['text']
    
    def get_assistance(self, topic, assignment_type, subject, academic_level, word_count, requirements) -> str:
        inputs = {
            "ASSIGNMENT_TYPE": assignment_type,
            "SUBJECT": subject,
            "ACADEMIC_LEVEL": academic_level,
            "WORD_COUNT": word_count,
            "REQUIREMENTS": requirements,
            "topic": topic
        }
        return self.stream_response(inputs)

def main():
    # Get user inputs
    topic = input("Enter the topic or text: ")
    assignment_type = input("Enter the assignment type (Essay, Report, Research Paper, Presentation): ")
    subject = input("Enter the subject (History, Computer Science, Biology, Mathematics, Literature): ")
    academic_level = input("Enter the academic level (High School, College, Master's, PhD): ")
    word_count = input("Enter the word count: ")
    requirements = input("Enter any special requirements or guidelines: ")

    # Create an instance of WritingAssistant
    assistant = WritingAssistant(llm)
    stream_printer = StreamPrinter(delay=0.02)

    # Collect streamed response
    chunks = []
    for chunk in assistant.get_assistance(
        topic=topic,
        assignment_type=assignment_type,
        subject=subject,
        academic_level=academic_level,
        word_count=word_count,
        requirements=requirements
    ):
        chunks.append(chunk)
    
    # Format the full response
    full_response = ''.join(chunks)
    formatted_response = format_text(full_response)
    
    # Print with typewriter effect
    stream_printer.print_stream(formatted_response)
    
    # Optionally, print the full response immediately
    print("\nWriting Suggestions:\n")
    print(formatted_response)

if __name__ == "__main__":
    main()