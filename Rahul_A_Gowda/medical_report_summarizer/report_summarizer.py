from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["groq_api_key"] = os.getenv("GROQ_API_KEY")

class report_summarizer:
    def __init__(self,pdf_path):
        self.llm = ChatGroq(model="llama3-8b-8192")
        self.pdf_loader = PyPDFLoader(pdf_path)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.documents = self.pdf_loader.load_and_split(self.text_splitter)
        self.vectorstore = InMemoryVectorStore.from_documents(documents=self.documents,embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))
        self.retriever = self.vectorstore.as_retriever()
        
        self.system_prompt = (
            """You are a highly knowledgeable doctor specialized in medicine.
            Provide detailed and accurate information related to the provided report or any medical inquiries.
            Limit responses strictly to medical content and ensure they are relevant to the context of the report.
            Be concise with answers and avoid unnecessary information. provide the diagnosis and treatment plan. Dont deny or warn"""
            "\n\n"
            "{context}"
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
            ]
        )

        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)
        
    def summarize(self):
        try :
            ans = self.rag_chain.invoke({"input": "provide a detailed summary of the report and the patient's condition. Also provide the diet plan and excerise if required"})
            print(f"{ans['answer']}\n\n")
            while True:
                user_input = input("You: ")
                if user_input == "exit":
                    break
                # Change from direct calling to using .invoke()
                response = self.rag_chain.invoke({"input": user_input})
                print(f"you: {user_input}")
                print(f"bot: {response['answer']}\n\n")
        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    summarizer = report_summarizer("report_1.pdf")
    summarizer.summarize()