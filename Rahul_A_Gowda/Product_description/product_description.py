import os
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Load environment variables from .env file
os.environ["GOOGLE_API_KEY"] = os.getenv("google_api_key")

class FRIDAY:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        self.store = {}
        self.output_parser = StrOutputParser()

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Retrieve the chat history for a given session ID, or create a new one."""
        return self.store.setdefault(session_id, ChatMessageHistory())

    def setup_chain(self):
        """Set up the prompt and chain with the model."""
        self.user_name = input("Enter your username: ")
        prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are FRIDAY, an AI assistant specialized in generating product descriptions.
        Based on the product details provided by the user, create clear, engaging, and concise descriptions.
        Ask any necessary questions to clarify product details before generating the description.
        Respond only with the product description, and ensure it aligns with any specified parameters.
        Do not provide any other information other than product description
        I'm {self.user_name}.
        """),MessagesPlaceholder(variable_name="thinking")
        ])
        return prompt | self.model  # Combine prompt and model into a chain

    async def chat(self):
        """Main chat loop to handle user input and generate streaming responses."""
        bot_name = "FRIDAY"
        chain = self.setup_chain()  # Setting up the chain
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)
        print(f"{bot_name}: Hey {self.user_name}, how can I help you today?\n")

        while True:
            user_input = input("you: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{bot_name}: Goodbye, {self.user_name}! Have a nice day.")
                break

            config = {"configurable": {"session_id": self.user_name}}

            print(f"{bot_name}: ", end="", flush=True)

            # Invoke the model and stream the response
            async for chunk in with_message_history.astream([HumanMessage(content=user_input)], config=config):
                parsed_output = self.output_parser.parse(chunk.content)
                cleaned_output = parsed_output.replace("*", "").replace("\n", " ").strip()  # Remove asterisks, newlines, and extra whitespace
                structured_output = " ".join(cleaned_output.split())  # Ensure consistent spacing
                print(structured_output, end=" ", flush=True)
            print()  # Print a newline after the complete response

if __name__ == "__main__":
    import asyncio
    bot = FRIDAY()
    asyncio.run(bot.chat())