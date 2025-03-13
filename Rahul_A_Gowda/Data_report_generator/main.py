import os
from uuid import uuid4
from dotenv import load_dotenv
from typing import Any, Dict, List, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler
from data_analyzer import DataAnalyzer

load_dotenv()

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens.append(token)
        print(token, end="", flush=True)

class AIChatAssistant:
    def __init__(self, llm_model="gemini-1.5-pro"):
        self.csv_path = os.getenv("CSV_PATH")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        if not self.csv_path or not os.path.exists(self.csv_path):
            raise ValueError("CSV_PATH environment variable is not set or file does not exist")
            
        self.llm = ChatGoogleGenerativeAI(model=llm_model, api_key=self.api_key, streaming=True)
        
        # Initialize data analyzer
        self.data_analyzer = DataAnalyzer(self.csv_path)
        self.analysis_context = self.data_analyzer.get_context_string()
        self.chat_history: List[Union[HumanMessage, AIMessage]] = []

        # Update system prompt to use data analysis context
        self.system_prompt = f"""You are a data analysis expert.
            Provide detailed and accurate insights based on the following data analysis:
            
            {self.analysis_context}
            
            Please provide clear explanations and insights based on the data.
            
            Chat history:
            {{chat_history}}"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
        ])
        
        # Create a simple chain without retrieval since we're using direct context
        self.chain = self.prompt | self.llm

    def ask_question(self, question: str) -> str:
        callback_handler = StreamingCallbackHandler()
        
        response = self.chain.invoke({
            "input": question,
            "chat_history": self.format_chat_history()
        }, config={"callbacks": [callback_handler]})
        
        self.chat_history.extend([
            HumanMessage(content=question),
            AIMessage(content=response.content)
        ])
        
        return response.content

    def format_chat_history(self) -> str:
        formatted_history = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                formatted_history.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_history.append(f"Assistant: {message.content}")
        return "\n".join(formatted_history)

    def run_chat(self):
        detailed_summary = self.ask_question("provide a detailed summary of the report and the patient's condition. Also provide the diet plan and excerise if required")
        print("Bot:", detailed_summary,"\n")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            answer = self.ask_question(user_input)
            print(f"Bot: {answer}\n")
            
if __name__ == "__main__":
    assistant = AIChatAssistant()
    assistant.run_chat()