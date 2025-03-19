import time
import PyPDF2
import yaml
import sys
import os
import docx
import asyncio
# Import LangChain modules
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

from dotenv import load_dotenv
load_dotenv()

class ContractReviewAssistant:
    def __init__(self, contract_folder_path, API_KEY=None):
        """Initialize the contract review assistant with LLM and conversation memory."""
        self.file_path = contract_folder_path  # Store contract folder path
        self.api_key=self._load_api_key()
        # ✅ Properly initialize the GoogleGenerativeAI model with API key
        self.llm = GoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            streaming=True
        )

        # Memory buffer to store chat history
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Extract text data from all contract files in the folder
        contract_text = self._read_file(contract_folder_path)

        # Generate and save the system prompt based on contract text
        self.create_system_prompt_file(contract_text)

        # Load the system prompt from the saved file
        with open("system_prompt.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()

        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),  # System prompt as initial instruction
            MessagesPlaceholder(variable_name="chat_history"),  # Include conversation history
            HumanMessagePromptTemplate.from_template("{text}")  # User's input
        ])

        # Create a conversation chain with memory
        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    
    def _read_file(self, folder_path):
        """Reads and combines content from all PDF and DOCX files in the specified folder."""
        combined_text = ""

        # Iterate over each file in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext == ".pdf":
                combined_text += self._read_pdf(file_path) + "\n"
            elif file_ext in [".doc", ".docx"]:
                combined_text += self._read_docx(file_path) + "\n"

        if not combined_text.strip():
            raise ValueError("No valid contract files found in the folder.")

        return combined_text.strip()

    def _read_pdf(self, file_path):
        """Extracts text from a PDF file."""
        text = ""
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")
        return text.strip()

    def _read_docx(self, file_path):
        """Extracts text from a DOCX file."""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs]).strip()
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {e}")

    def create_system_prompt_file(self, contract_text):
        """Generates and saves a system prompt file based on contract text."""
        system_prompt = f"""
        You are a contract review assistant. Your task is to help users understand the terms and conditions of the contract provided.
        Answer the user's questions based on the content of the contract. Provide clear and concise explanations.
        If a question cannot be answered based on the contract, inform the user accordingly.

        Contract Text:
        {contract_text}
        """

        with open("system_prompt.txt", "w", encoding="utf-8") as file:
            file.write(system_prompt.strip())

    def process(self, text):
        """Processes user input, generates a response using the LLM, and tracks response time."""
        self.memory.chat_memory.add_user_message(text)  # Store user input in memory

        # Measure LLM response time
        start_time = time.time()
        response = self.conversation.invoke({"text": text})  # Get response from LLM
        end_time = time.time()

        self.memory.chat_memory.add_ai_message(response['text'])  # Store AI response in memory

        elapsed_time = int((end_time - start_time) * 1000)  # Convert response time to milliseconds
        return response['text']

# Main function to interact with the assistant
async def contract_assistant():
    contract_folder_path = "contracts"  # Define folder containing contract documents

    # ✅ Pass only folder path (API_KEY is now handled inside the class)
    assistant = ContractReviewAssistant(contract_folder_path)

    print("Contract Review Assistant: Welcome! You can ask me questions about the contract.")
    while True:
        user_input = await asyncio.to_thread(input, "You: ")  # Get user input asynchronously
        if user_input.lower() in {"exit", "quit", "goodbye", "bye"}:  # Check for exit commands
            print("Contract Review Assistant: Thank you for your questions. Goodbye!")
            break

        assistant_response = assistant.process(user_input)  # Process user input
        print(f"Contract Review Assistant: {assistant_response}")

# ✅ Fixed Syntax Error - Removed `:` at the end
if __name__ == "__main__":
    asyncio.run(contract_assistant())
