import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_community import GmailToolkit
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

load_dotenv()

class email_writer:
    def __init__(self,):
        self.token = os.getenv("TOKEN")
        self.client_secrets_file = os.getenv("CLIENT_SECRET_FILE_PATH")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.credentials = get_gmail_credentials(
            token_file=self.token,
            scopes=["https://mail.google.com/"],
            client_secrets_file=self.client_secrets_file,
        )
        self.llm = ChatGoogleGenerativeAI(model = "gemini-1.5-pro",api_key=self.api_key)
        self.api_resource = build_resource_service(credentials=self.credentials)
        self.toolkit = GmailToolkit(api_resource=self.api_resource)
        self.tools = self.toolkit.get_tools()
        self.agent_executor = create_react_agent(self.llm, self.tools)

    def chat(self):
        while True:
            user_input = input("you: ")

            if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"friday: Goodbye! Have a nice day.")
                    break

            events = self.agent_executor.stream(
                {"messages": [("user", user_input)]},
                stream_mode="values",)
            for event in events:
                event["messages"][-1].pretty_print()
                
if __name__ == "__main__":
    token = "email_writer\\token.json"
    credentials = "email_writer\\credentials.json"
    email_writer = email_writer(token = token,credentials=credentials)
    email_writer.chat()