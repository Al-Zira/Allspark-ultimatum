import os
import time
import uuid
import asyncio
import pandas as pd
import re
from typing import Optional, AsyncGenerator
from PyPDF2 import PdfReader
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_google_genai import GoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import re
import unicodedata
import sys
import time

import warnings
warnings.filterwarnings("ignore")

load_dotenv()

class StreamPrinter:
    """Handles streaming output with typewriter effect"""
    def __init__(self, delay: float = 0.02):
        self.delay = delay

    def print_stream(self, text: str):
        """Print text with a typewriter effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(self.delay)

class DataQueryAssistant:
    def __init__(
        self,
        file_path: str,
        pinecone_index_name: str = "aizira",
        namespace: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        google_api_key: Optional[str] = None,
        pinecone_api_key: Optional[str] = None,
    ):
        self.file_path = file_path
        self.file_type = self._get_file_type()
        self.pinecone_index_name = pinecone_index_name
        self.namespace = namespace or os.path.basename(file_path)
        self.embedding_model = embedding_model
        
        # Validate and initialize API keys
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not all([self.google_api_key, self.pinecone_api_key]):
            raise ValueError("Missing required API keys in environment variables")

        # Initialize components
        self._initialize_embeddings()
        self._initialize_pinecone()
        self._process_file()
        
        # Initialize LLM with streaming
        self.llm = GoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.google_api_key,
            temperature=0.7,
            streaming=True
        )
        
        # Initialize workflow
        self.workflow = StateGraph(state_schema=MessagesState)
        self.memory = MemorySaver()
        self._setup_graph()
        
        # Unified prompt template
        self.PROMPT = PromptTemplate(
            template="""You are a Data Query Assistant specializing in both CSV and PDF data analysis. Answer the question using the provided context.

            Question: {question}

            Context: {context}

            Provide a clear, detailed response in a natural conversational tone. 
            For CSV data: Include numerical insights where relevant. 
            For PDF content: Focus on conceptual understanding.
            Always mention: 'This analysis does not carry any data processing implications.'""",
            input_variables=["question", "context"]
        )

    def _get_file_type(self):
        if self.file_path.lower().endswith('.csv'):
            return 'csv'
        elif self.file_path.lower().endswith('.pdf'):
            return 'pdf'
        raise ValueError("Unsupported file type. Only CSV and PDF files are supported.")

    def _initialize_embeddings(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

    def _initialize_pinecone(self):
        self.pinecone_client = PineconeClient(api_key=self.pinecone_api_key)
        
        if self.pinecone_index_name not in self.pinecone_client.list_indexes().names():
            print(f"Creating new Pinecone index: {self.pinecone_index_name}")
            sample_embedding = self.embeddings.embed_query("sample")
            self.pinecone_client.create_index(
                name=self.pinecone_index_name,
                dimension=len(sample_embedding),
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not self.pinecone_client.describe_index(self.pinecone_index_name).status["ready"]:
                time.sleep(1)

    def _process_file(self):
        if self.file_type == 'csv':
            self._process_csv()
        else:
            self._process_pdf()

    def _process_csv(self):
        df = pd.read_csv(self.file_path)
        documents = [
            Document(
                page_content="\n".join([f"{col}: {val}" for col, val in row.items()]),
                metadata={"source": self.file_path, "row": idx},
            )
            for idx, row in df.iterrows()
        ]
        
        index = self.pinecone_client.Index(self.pinecone_index_name)
        stats = index.describe_index_stats()

        if self.namespace in stats.get('namespaces', {}):
            print(f"Using existing document: {self.namespace}")
            self.vector_store = Pinecone.from_existing_index(  # Changed here
                index_name=self.pinecone_index_name,
                embedding=self.embeddings,
                namespace=self.namespace
            )
            return
        
        self.vector_store = Pinecone.from_documents(
            documents=documents,
            embedding=self.embeddings,
            index_name=self.pinecone_index_name,
            namespace=self.namespace,
        )

    def _process_pdf(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        index = self.pinecone_client.Index(self.pinecone_index_name)
        stats = index.describe_index_stats()

        if self.namespace in stats.get('namespaces', {}):
            print(f"Using existing document: {self.namespace}")
            self.vector_store = Pinecone.from_existing_index(  # Changed here
                index_name=self.pinecone_index_name,
                embedding=self.embeddings,
                namespace=self.namespace
            )
            return
        
        with open(self.file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                cleaned_text = self._clean_text(text)
                text_parts.append(cleaned_text)
            
            full_text = ' '.join(text_parts)
            doc = Document(page_content=full_text, metadata={"source": self.file_path})
        
        splits = text_splitter.split_documents([doc])
        self.vector_store = Pinecone.from_documents(
            documents=splits,
            embedding=self.embeddings,
            index_name=self.pinecone_index_name,
            namespace=self.namespace,
        )

    # def _clean_text(self, text: str) -> str:
    #     text = re.sub(r'\s+', ' ', text)
    #     replacements = {' v ': 'v', ' e ': 'e', ' r ': 'r'}
    #     for k, v in replacements.items():
    #         text = text.replace(k, v)
    #     return ' '.join(text.split())

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text from PDF extraction artifacts"""
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Remove non-ASCII characters (optional, configure based on needs)
        text = text.encode('ascii', 'ignore').decode('utf-8')
        
        # Common PDF cleaning patterns
        cleaning_patterns = [
            (r'\s+', ' '),                   # Collapse whitespace
            (r'-\n(\w+)', r'\1'),            # Fix hyphenated line breaks
            (r'(?<=\w)\s?-\s?(?=\w)', '-'),  # Fix spaced hyphens in words
            (r'\s*([,:;.!?])\s*', r'\1 '),   # Normalize punctuation spacing
            (r'\s*’\s*', "'"),               # Fix spaced apostrophes
            (r'“|”', '"'),                   # Normalize smart quotes
            (r'\s*/\s*', '/'),               # Fix spaced slashes
            (r'(\d)\s+(\d)', r'\1\2'),       # Fix spaced numbers
            (r'\t', ' '),                    # Replace tabs with spaces
            (r'^https?:\/\/.*[\r\n]*', '')   # Remove URLs
        ]

        # Apply regex patterns
        for pattern, replacement in cleaning_patterns:
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

        # Replace common spaced abbreviations
        abbreviation_map = {
            r'\bv\b': 'vs',
            r'\be\b': 'e.g',
            r'\bi\b': 'i.e',
            r'\br\b': 'r.t',
            r'\bw\b': 'with',
            r'\bc\b': 'ch.'
        }
        
        for pattern, replacement in abbreviation_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Remove leftover line breaks and trim whitespace
        text = re.sub(r'\n+', ' ', text).strip()
        
        # Final whitespace cleanup
        return ' '.join(text.split())

    def _setup_graph(self):
        def process_query(state: MessagesState):
            query = state["messages"][-1].content
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(query)
            context = "\n".join([doc.page_content for doc in docs])
            
            formatted_prompt = self.PROMPT.format(
                question=query,
                context=context
            )
            response = self.llm.invoke(formatted_prompt)
            return {"messages": [AIMessage(content=response)]}

        self.workflow.add_node("process_query", process_query)
        self.workflow.add_edge(START, "process_query")
        self.app = self.workflow.compile(checkpointer=self.memory)
        self.thread_id = uuid.uuid4()
        self.config = {"configurable": {"thread_id": self.thread_id}}

    async def stream_response(self, query: str) -> AsyncGenerator[str, None]:
        """Stream response generator"""
        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(query)
            context = "\n".join([doc.page_content for doc in docs])
            
            formatted_prompt = self.PROMPT.format(
                question=query,
                context=context
            )
            
            async for chunk in self.llm.astream(formatted_prompt):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

async def run_chat():
    file_path = input("Enter path to CSV/PDF file: ")
    assistant = DataQueryAssistant(file_path=file_path)
    stream_printer = StreamPrinter()  # Create printer instance
    
    print("\nData Query Assistant: Ready to analyze your file. Type 'exit' to end.")
    while True:
        try:
            query = input("\nYou: ")
            if query.lower() in ['exit', 'quit']:
                break
                
            print("\nAssistant: ", end='', flush=True)
            async for chunk in assistant.stream_response(query):
                stream_printer.print_stream(chunk)  # Use stream printer
            print()
            
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_chat())