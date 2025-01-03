import os
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# api_key=os.environ.get('GOOGLE_API_KEY','NOT_SET')  # API Key from environment variable
api_key="AIzaSyDlVWvKtxMoPST4y2uySiibTiKx9-jkTS8"
username=os.environ.get('USER_NAME','NOT_SET').strip()
class FRIDAY:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=api_key)
        self.store = {}
        self.output_parser = StrOutputParser()

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        return self.store.setdefault(session_id, ChatMessageHistory())

    def setup_chain(self, username):
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are FRIDAY, an AI assistant specialized in generating product descriptions. 
            Based on the product details provided by the user, create clear, engaging, and concise descriptions.
            Ask any necessary questions to clarify product details before generating the description.
            Respond only with the product description, and ensure it aligns with any specified parameters.
            Do not provide any other information other than product description.
            I'm {username}.
            """),
            MessagesPlaceholder(variable_name="thinking")
        ])
        return prompt | self.model

    async def chat(self):
        chain = self.setup_chain(username)
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)

        while True:
            try:
                user_input = input("you: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"FRIDAY: Goodbye, {username}! Have a nice day.")
                    break

                config = {"configurable": {"session_id": username}}
                print("FRIDAY: ", end="", flush=True)

                async for chunk in with_message_history.astream([HumanMessage(content=user_input)], config=config):
                    parsed_output = self.output_parser.parse(chunk.content)
                    cleaned_output = parsed_output.replace("*", "").replace("\n", " ").strip()
                    structured_output = " ".join(cleaned_output.split())
                    print(structured_output, end=" ", flush=True)
                print()

            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break

if __name__ == "__main__":
    import asyncio
    bot = FRIDAY()
    asyncio.run(bot.chat())