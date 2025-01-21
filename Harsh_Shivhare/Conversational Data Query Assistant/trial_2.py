import os
import pandas as pd
from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient
from dotenv import load_dotenv
from langchain.chains import StuffDocumentsChain, LLMChain
import warnings
from typing import List
from dataclasses import dataclass

warnings.filterwarnings("ignore")


@dataclass
class Config:
    """Configuration class for API keys and settings"""
    GOOGLE_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "aizira"
    PINECONE_ENVIRONMENT: str = "us-east-1"
    EMBEDDING_MODEL: str = 'sentence-transformers/all-MiniLM-L6-v2'
    LLM_MODEL: str = 'gemini-pro'
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5


class DocumentProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        self.pinecone_client = PineconeClient(api_key=config.PINECONE_API_KEY)
        self.vector_store = Pinecone(
            embedding=self.embeddings,
            index_name=config.PINECONE_INDEX_NAME
        )
        self.llm = GoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=0.7,
            api_key=config.GOOGLE_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            keep_separator=True
        )

    def check_namespace(self, namespace: str) -> bool:
        try:
            index = self.pinecone_client.Index(self.config.PINECONE_INDEX_NAME)
            stats = index.describe_index_stats()
            return namespace in stats.get('namespaces', {})
        except Exception as e:
            raise ValueError(f"Error checking namespace: {e}")

    def process_file(self, file_path: str) -> Document:
        try:
            if file_path.endswith('.pdf'):
                pdf_reader = PdfReader(file_path)
                text = " ".join(page.extract_text() for page in pdf_reader.pages)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                text = "\n".join(
                    f"{col}: {value}" 
                    for _, row in df.iterrows() 
                    for col, value in row.items()
                )
            else:
                raise ValueError("Unsupported file format. Please use PDF or CSV.")
            return Document(page_content=text, metadata={"source": file_path})
        except Exception as e:
            raise ValueError(f"Error processing file: {e}")

    def create_vector_store(self, docs: List[Document], namespace: str) -> Pinecone:
        try:
            vector_store = Pinecone.from_documents(
                documents=docs,
                embedding=self.embeddings,
                index_name=self.config.PINECONE_INDEX_NAME,
                namespace=namespace
            )
            return vector_store
        except Exception as e:
            raise ValueError(f"Error creating vector store: {e}")


class ChatBot:
    def __init__(self, config: Config):
        self.config = config
        self.processor = DocumentProcessor(config)
        self.docsearch = None
        self.namespace = None
        self._setup_prompts()

    def _setup_prompts(self):
        self.document_prompt = PromptTemplate(
            template="{page_content}",
            input_variables=["page_content"]
        )
        self.main_prompt = PromptTemplate(
            template="""
            You are a Conversational Data Query Assistant.
            Question: {question}
            Context: {context}
            Provide a comprehensive answer based on the context.
            """,
            input_variables=["context", "question"]
        )

    def upload_file(self, file_path: str) -> str:
        try:
            self.namespace = os.path.splitext(os.path.basename(file_path))[0]
            if self.processor.check_namespace(self.namespace):
                self.docsearch = Pinecone(
                    index_name=self.config.PINECONE_INDEX_NAME,
                    embedding=self.processor.embeddings,
                    namespace=self.namespace
                )
                return f"Using existing namespace: {self.namespace}"
            doc = self.processor.process_file(file_path)
            docs = self.processor.text_splitter.split_documents([doc])
            self.docsearch = self.processor.create_vector_store(docs, self.namespace)
            return f"Processed {len(docs)} chunks from {file_path}"
        except Exception as e:
            return f"Error processing file: {str(e)}"

    def respond(self, message: str) -> str:
        if self.docsearch is None:
            return "Please upload a document first."
        try:
            retriever = self.docsearch.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.config.TOP_K_RESULTS},
                namespace=self.namespace
            )
            documents = retriever.get_relevant_documents(message)
            if not documents:
                return "No relevant documents found."
            llm_chain = LLMChain(llm=self.processor.llm, prompt=self.main_prompt)
            chain = StuffDocumentsChain(
                llm_chain=llm_chain,
                document_prompt=self.document_prompt,
                document_variable_name="context"
            )
            result = chain.invoke({"input_documents": documents, "question": message})
            sources = set(doc.metadata.get('source', 'Unknown') for doc in documents)
            return f"{result['output_text']}\n\nSources: {', '.join(sources)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"


def main():
    load_dotenv()
    config = Config(
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
        PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
    )
    chatbot = ChatBot(config)

    print("ASSISTANT: Welcome! I am your Conversational Data Query Assistant.")
    print("ASSISTANT: First, please provide the path to your document (PDF or CSV).")

    file_path = input("YOU: ").strip()

    if not os.path.exists(file_path):
        print("ASSISTANT: The file path you entered does not exist. Please restart and try again.")
        return

    upload_response = chatbot.upload_file(file_path)
    print(f"ASSISTANT: {upload_response}")

    while True:
        print("ASSISTANT: You can now ask me questions about the document or type 'exit' to end the session.")
        query = input("YOU: ").strip()

        if query.lower() == 'exit':
            print("ASSISTANT: Goodbye! Have a great day!")
            break

        response = chatbot.respond(query)
        print(f"ASSISTANT: {response}")


if __name__ == "__main__":
    main()

