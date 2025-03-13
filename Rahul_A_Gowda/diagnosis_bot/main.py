import os
from uuid import uuid4
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core import exceptions
import time

load_dotenv()

api_key = os.environ.get('GOOGLE_API_KEY')

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

class FRIDAY:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            api_key=api_key,
            retry_on_failure=True
        )
        self.store = {}
        self.session_id = str(uuid4())
        self.output_parser = StrOutputParser()

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Retrieve the chat history for a given session ID, or create a new one."""
        return self.store.setdefault(session_id, ChatMessageHistory())

    def setup_chain(self):
        """Set up the prompt and chain with the model."""
        prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an AI assistant specializing in medical diagnosis.
        Analyze the patient's symptoms and provide probable causes. Ask clarifying questions if necessary before delivering the diagnosis.
        Respond strictly from a medical perspective, avoiding any unrelated information.
        """),MessagesPlaceholder(variable_name="thinking")
        ])
        return prompt | self.model

    async def chat(self):
        """Main chat loop to handle user input and generate streaming responses."""
        chain = self.setup_chain() 
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)

        while True:
            try:
                user_input = input("you: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"bot: Goodbye, Have a nice day.")
                    break

                config = {"configurable": {"session_id": self.session_id}}
                print(f"bot: ", end="", flush=True)

                try:
                    async for chunk in with_message_history.astream([HumanMessage(content=user_input)], config=config):
                        parsed_output = self.output_parser.parse(chunk.content)
                        cleaned_output = parsed_output.replace("*", "").replace("\n", " ").strip()
                        structured_output = " ".join(cleaned_output.split())
                        print(structured_output, end=" ", flush=True)
                    print()
                except exceptions.ServiceUnavailable:
                    print("\nThe model is currently overloaded. Please wait a moment and try again.")
                    time.sleep(2)  # Add a small delay before retrying
                except exceptions.ResourceExhausted:
                    print("\nAPI quota exceeded. Please try again later.")
                except Exception as e:
                    print(f"\nError: {str(e)}")
            except KeyboardInterrupt:
                print("\nbot: Goodbye! Have a nice day.")
                break
            except Exception as e:
                print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    bot = FRIDAY()
    asyncio.run(bot.chat())