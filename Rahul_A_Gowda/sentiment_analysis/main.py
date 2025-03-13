import os
import uuid
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

class FRIDAY:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro",api_key=api_key)
        self.store = {}
        self.output_parser = StrOutputParser()
        self.session_id = str(uuid.uuid4())

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Retrieve the chat history for a given session ID, or create a new one."""
        return self.store.setdefault(session_id, ChatMessageHistory())

    def setup_chain(self):
        """Set up the prompt and chain with the model."""
        prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are FRIDAY, an AI assistant specialized in sentiment analysis.
        Your task is to analyze the sentiment of text provided by the user. Identify whether the sentiment is positive, negative, or neutral, and provide a brief explanation for your analysis.
        If the sentiment is unclear, ask the user for additional context.
        Respond only with the sentiment label (positive, negative, or neutral) and the reasoning behind your analysis.
        """),
        MessagesPlaceholder(variable_name="thinking")
        ])
        return prompt | self.model 

    async def chat(self):
        bot_name = "FRIDAY"
        chain = self.setup_chain()  
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)
        print(f"{bot_name}: Hey, how can I help you today?\n")

        while True:
            user_input = input("you: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{bot_name}: Goodbye, Have a nice day.")
                break

            config = {"configurable": {"session_id": self.session_id}}

            print(f"{bot_name}: ", end="", flush=True)

            async for chunk in with_message_history.astream([HumanMessage(content=user_input)], config=config):
                parsed_output = self.output_parser.parse(chunk.content)
                cleaned_output = parsed_output.replace("*", "").replace("\n", " ").strip()
                structured_output = " ".join(cleaned_output.split())
                print(structured_output, end=" ", flush=True)
            print() 

if __name__ == "__main__":
    import asyncio
    bot = FRIDAY()
    asyncio.run(bot.chat())