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
api_key=os.environ.get('GOOGLE_API_KEY','NOT_SET')  # API Key from environment variable
username=os.environ.get('USER_NAME','NOT_SET')  

class FRIDAY:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=api_key)
        self.store = {}
        self.output_parser = StrOutputParser()

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Retrieve the chat history for a given session ID, or create a new one."""
        return self.store.setdefault(session_id, ChatMessageHistory())

    def setup_chain(self):
        """Set up the prompt and chain with the model."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a resume-building assistant.
            Your task is to gather information from the user and organize it into key resume sections, including:
            - **Professional Summary:** (Provide a brief overview of the user's career highlights and goals)
            - **Education:** (Include degree(s), institution(s), and graduation date(s))
            - **Experience:** (List previous job roles, employers, dates, and main responsibilities and achievements in each role)
            - **Skills:** (List relevant technical, language, or other professional skills)
            - **Achievements:** (Highlight notable achievements, awards, or recognitions)
            - **Projects:** (Detail relevant projects, including goals, methodologies, and outcomes)
            - **Positions of Responsibility:** (Include leadership or volunteer roles with responsibilities and accomplishments)

            Prompt the user for details if information is missing in any section. Respond only with the organized resume content in the specified format. I'm {username}.
            If they do not provide the required or relevant information, ask them for the information to create a resume.
            """),
            MessagesPlaceholder(variable_name="thinking")
        ])
        return prompt | self.model  # Combine prompt and model into a chain

    async def chat(self):
        """Main chat loop to handle user input and generate streaming responses."""
        chain = self.setup_chain()  # Setting up the chain
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)

        while True:
            user_input = input("you: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"bot: Goodbye, {username}! Have a nice day.")
                break

            config = {"configurable": {"session_id": username}}

            print(f"bot: ", end="", flush=True)

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