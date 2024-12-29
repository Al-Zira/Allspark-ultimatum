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
            ("system", f"""You are ARCHER, a resume-building assistant.
            Your task is to gather information from the user and organize it into key resume sections, including:
            - **Professional Summary:** (Provide a brief overview of the user's career highlights and goals)
            - **Education:** (Include degree(s), institution(s), and graduation date(s))
            - **Experience:** (List previous job roles, employers, dates, and main responsibilities and achievements in each role)
            - **Skills:** (List relevant technical, language, or other professional skills)
            - **Achievements:** (Highlight notable achievements, awards, or recognitions)
            - **Projects:** (Detail relevant projects, including goals, methodologies, and outcomes)
            - **Positions of Responsibility:** (Include leadership or volunteer roles with responsibilities and accomplishments)

            Prompt the user for details if information is missing in any section. Respond only with the organized resume content in the specified format. I'm {self.user_name}.
            """),
            MessagesPlaceholder(variable_name="thinking")
        ])
        return prompt | self.model  # Combine prompt and model into a chain

    def additional_step(self, response_content: str) -> str:
        """An example additional step to chain more logic after model's response."""
        # Let's assume we want to post-process or format the response here.
        # You can add any extra functionality here (e.g., formatting, logging, filtering, etc.).
        return f"{response_content}"

    def chat(self):
        """Main chat loop to handle user input and generate responses."""
        bot_name = "FRIDAY"
        chain = self.setup_chain()  # Setting up the chain
        with_message_history = RunnableWithMessageHistory(chain, self.get_session_history)
        print(f"{bot_name}: hey {self.user_name}, how can I help you today?\n")
        
        while True:
            user_input = input("you: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{bot_name}: Goodbye, {self.user_name}! Have a nice day.")
                break

            config = {"configurable": {"session_id": self.user_name}}
            
            # Invoke the model and get the response
            response = with_message_history.invoke([HumanMessage(content=user_input)], config=config)
            
            # Parse the response content after getting it
            parsed_output = self.output_parser.parse(response.content)
            
            # Pass the parsed output to an additional step in the chain
            final_output = self.additional_step(parsed_output)
            
            # Display the final output
            print(f"{bot_name}: {final_output}")

if __name__ == "__main__":
    bot = FRIDAY()
    bot.chat()
