import os
import time
import PyPDF2
from dotenv import load_dotenv

# Import LangChain modules
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

# Load environment variables from .env file
load_dotenv()

class ContractReviewAssistant:
    def __init__(self, contract_pdf_path):
        # Initialize the language model (Groq)
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama3-groq-70b-8192-tool-use-preview",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Memory to hold conversation history
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Extract data from the contract PDF
        contract_text = self.extract_text_from_pdf(contract_pdf_path)

        # Generate a system prompt based on the contract text
        self.create_system_prompt_file(contract_text)

        # Load the system prompt from the file with utf-8 encoding
        with open("system_prompt.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read().strip()

        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([ 
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        # Create the conversation chain
        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """
        Extract text from a PDF file.
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return text.strip()
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def create_system_prompt_file(self, contract_text):
        """
        Generate and save a system prompt based on the contract text.
        """
        system_prompt = f"""
        You are a contract review assistant. Your task is to help users understand the terms and conditions of the contract provided.
        Answer the user's questions based on the content of the contract. Provide clear and concise explanations.
        If a question cannot be answered based on the contract, inform the user accordingly.

        Contract Text:
        {contract_text}
        """

        # Write the prompt to system_prompt.txt using utf-8 encoding
        with open("system_prompt.txt", "w", encoding="utf-8") as file:
            file.write(system_prompt.strip())
    def process(self, text):
        # Add user message to memory
        self.memory.chat_memory.add_user_message(text)

        # Measure response time
        start_time = time.time()
        response = self.conversation.invoke({"text": text})  # Get response from LLM
        end_time = time.time()

        # Add AI response to memory
        self.memory.chat_memory.add_ai_message(response['text'])

        elapsed_time = int((end_time - start_time) * 1000)

        return response['text']


# Main function to interact with the contract review assistant
def main():
    # File path
    contract_pdf_path = r"DOC-20240902-WA0008 (1).pdf"  # Update with the actual PDF path

    # Initialize the assistant
    assistant = ContractReviewAssistant(contract_pdf_path)

    print("Contract Review Assistant: Welcome! You can ask me questions about the contract.")
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit", "goodbye", "bye"}:
            print("Contract Review Assistant: Thank you for your questions. Goodbye!")
            break

        # Process the input and get the assistant's response
        assistant_response = assistant.process(user_input)
        print(f"Contract Review Assistant: {assistant_response}")


if __name__ == "__main__":
    main()