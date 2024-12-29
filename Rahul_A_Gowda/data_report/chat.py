from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.vectorstores import VectorStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.memory import ConversationBufferMemory
import os


class AIChatAssistant:
    def __init__(self, doc_path, llm_model="gemini-1.5-pro", embedding_model="all-MiniLM-L6-v2"):
        load_dotenv()

        # Load environment variables
        os.environ["google_api_key"] = os.getenv("google_api_key")

        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model=llm_model)

        # Load document
        self.loader = Docx2txtLoader(doc_path)
        self.data = self.loader.load()

        # Create vector store
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=self.data, embedding=HuggingFaceEmbeddings(model_name=embedding_model)
        )
        self.retriever = self.vectorstore.as_retriever()

        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Define prompts
        self.system_prompt = (
            """You are a highly knowledgeable data scientist, capable of answering any questions in the field of AI, including those related to reports provided by the user.
            Dont respond to any other questions about any other field than AI.
            Ensure all answers are concise, accurate, and explicit.
            Don't be concise with your answers."""
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

        # Create chains
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)

    def ask_question(self, question):
        # Add memory context
        input_data = {
            "input": question,
            "chat_history": self.memory.load_memory_variables({})["chat_history"],
        }

        response = self.rag_chain.invoke(input_data)
        # Update memory
        self.memory.save_context({"input": question}, {"output": response["answer"]})
        return response["answer"]

    def run_chat(self):
        detailed_summary = self.ask_question("provide detailed information about the report, machine learning models that can be used as well as the data cleaning technique that can be used")
        print("Bot:", detailed_summary)
        print("bot: {ask_questions('')}")
        print()
        while True:
            user_input = input("You: ")
            
            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            answer = self.ask_question(user_input)
            print(f"you: {user_input}")
            print("Bot:", answer)
            print("****************************************************************************************************************")


# Example usage
if __name__ == "__main__":
    assistant = AIChatAssistant(doc_path="eda_report.docx")
    assistant.run_chat()
