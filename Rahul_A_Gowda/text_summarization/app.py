import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class text_summarizer:
    def __init__(self,api_key):
        os.environ["GOOGLE_API_KEY"] = os.getenv("groq_api_key")
        llm = ChatGoogleGenerativeAI(model_name = "gemini-1.5-pro")
        loader = PyPDFLoader("notes.pdf")
        docs = loader.load_and_split()
        split_docs = RecursiveCharacterTextSplitter(chunk_size=6500, chunk_overlap=400).split_documents(docs)

        chain = load_summarize_chain(
            llm=llm,
            chain_type="refine",
            verbose=True,
        )

        output_summary = chain({"input_documents": split_docs}, return_only_outputs=True)
        
        print(output_summary)

if __name__ == "__main__":
    bot = FRIDAY()
    bot.chat()