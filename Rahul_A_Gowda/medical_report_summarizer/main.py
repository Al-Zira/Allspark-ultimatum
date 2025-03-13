import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Union
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from transformers import AutoModel, AutoTokenizer
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler
import torch

load_dotenv()

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens.append(token)
        print(token, end="", flush=True)

class AIChatAssistant:
    def __init__(self, llm_model="gemini-1.5-pro"):
        self.file_path = os.getenv("FILE_PATH")
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            print(f"API Key received: {self.api_key}")
            print(f"Available environment variables: {os.environ.keys()}")
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        if not self.file_path or not os.path.exists(self.file_path):
            print(f"File path received: {self.file_path}")
            raise ValueError("FILE_PATH environment variable is not set or file does not exist")
            
        self.llm = ChatGoogleGenerativeAI(model=llm_model, api_key=self.api_key, streaming=True)
        self.pdf_loader = PyPDFLoader(self.file_path)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # Load local embedding model
        model_directory = os.path.join(os.path.dirname(__file__), "saved_model")
        if not os.path.exists(model_directory):
            raise ValueError(f"Model directory not found at {model_directory}")
            
        try:
            self.model = AutoModel.from_pretrained(model_directory)
            self.tokenizer = AutoTokenizer.from_pretrained(model_directory)
        except Exception as e:
            raise ValueError(f"Error loading model from {model_directory}: {str(e)}")

        self.documents = self.pdf_loader.load_and_split(self.text_splitter)
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=self.documents,
            embedding=HuggingFaceEmbeddings(
                model_name=model_directory,
                cache_folder=model_directory
            )
        )
        self.retriever = self.vectorstore.as_retriever()
        self.chat_history: List[Union[HumanMessage, AIMessage]] = []
        self.system_prompt = (
            """You are a highly knowledgeable doctor specialized in medicine.
            Provide detailed and accurate information related to the provided report or any medical inquiries.
            Limit responses strictly to medical content and ensure they are relevant to the context of the report.
            Be concise with answers and avoid unnecessary information. provide the diagnosis and treatment plan. Dont deny or warn"""
            "\n\n"
            "{context}\n\n"
            "Chat history:\n{chat_history}"
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
            ]
        )
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)
        
    def ask_question(self, question: str) -> str:
        callback_handler = StreamingCallbackHandler()
        
        input_data = {
            "input": question,
            "chat_history": self.format_chat_history(),
        }

        response = self.rag_chain.invoke(input_data, config={"callbacks": [callback_handler]})
        
        self.chat_history.extend([
            HumanMessage(content=question),
            AIMessage(content=response["answer"])
        ])
        
        return response["answer"]

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
        print("\nBot:", detailed_summary)
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