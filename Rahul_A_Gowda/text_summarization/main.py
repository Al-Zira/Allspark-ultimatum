import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

class text_summarizer:
    def __init__(self,folder_path):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                    google_api_key=api_key)
        loader = PyPDFLoader(Path(folder_path))
        docs = loader.load_and_split()
        split_docs = RecursiveCharacterTextSplitter(chunk_size=6500, chunk_overlap=400).split_documents(docs)

        chain = load_summarize_chain(
            llm=llm,
            chain_type="refine",
            verbose=False,
        )

        output_summary = chain.invoke({"input_documents": split_docs}, return_only_outputs=True)
        
        print(output_summary['output_text'])

if __name__ == "__main__":
    bot = text_summarizer(folder_path=os.getenv("FILE_PATH"))