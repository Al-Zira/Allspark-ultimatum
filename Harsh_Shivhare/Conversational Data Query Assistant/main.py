import os
import time
import uuid
import asyncio
import pandas as pd
import re
import sqlite3
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
import unicodedata
import sys
import time

import warnings
warnings.filterwarnings("ignore")

load_dotenv()
# os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'
# model_path = "/app/.cache/huggingface/models--sentence-transformers--all-MiniLM-L6-v2"
model_path = "/local_model"


class StreamPrinter:
    def __init__(self, delay: float = 0.02):
        self.delay = delay

    def print_stream(self, text: str):
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
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.vector_store = None
        if not all([self.google_api_key, self.pinecone_api_key]):
            raise ValueError("Missing required API keys in environment variables")

        self._initialize_embeddings()
        self._initialize_pinecone()
        self._process_file()

        self.llm = GoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.google_api_key,
            temperature=0.7,
            streaming=True
        )

        self.workflow = StateGraph(state_schema=MessagesState)
        self.memory = MemorySaver()
        self._setup_graph()

        self.PROMPT_CSV = PromptTemplate(
            template="""
            You are a SQL query generator. Using the following database schema:
            Table Name: {table_name}
            {schema}

            Generate an appropriate SQL query to answer this question: {question}

            Special Instructions:
            - For row count: Use "SELECT COUNT(*) as row_count FROM {table_name}"
            - For general queries, use SELECT with appropriate columns
            - Always include essential columns
            - Use LIMIT clause when appropriate
            - Ensure valid and complete SQL syntax

            Question: {question}
            """,
            input_variables=["table_name", "schema", "question"]
        )

        self.PROMPT_PDF = PromptTemplate(
            template="""
            You are a Data Query Assistant specializing in PDF data analysis.
            Perform RAG-based analysis to extract relevant conceptual information from the PDF content.
            Always mention: 'This analysis does not carry any data processing implications.'

            Natural Language Query: {question}
            Context: {context}
            """,
            input_variables=["question", "context"]
        )

        self.PROMPT_EXPLAIN = PromptTemplate(
            template="""
            You are a data analyst. Given the following SQL query result and the user's question, 
            provide a detailed explanation of the result.
            - Provide clear and concise explanations.
            - Ensure the explanation is easy to understand for non-technical users.
            - Highlight any important insights or findings.

            User Question: {question}
            SQL Query Result: {result}

            Explanation:
            """,
            input_variables=["question", "result"]
        )

    # def clean_sql_query(self, query: str) -> str:
    #     """Clean and format SQL query"""
    #     query = re.sub(r'```sql|```', '', query)
    #     query = ' '.join(query.split())
    #     if not query.endswith(';'):
    #         query += ';'
    #     return query
    def clean_sql_query(self, query: str) -> str:
        """Enhanced query cleaning method"""
        # Remove markdown code block markers
        query = re.sub(r'```sql|```|^sql', '', query, flags=re.MULTILINE)
        
        # Remove leading/trailing whitespace and standardize
        query = query.strip()
        
        # Add semicolon if not present
        if not query.endswith(';'):
            query += ';'
        
        return query
    
    def generate_appropriate_query(self, question: str) -> str:
        """Generate an appropriate query based on the question"""
        lower_question = question.lower()
        
        # Specific query patterns
        if 'count' in lower_question or 'number of rows' in lower_question:
            return f"SELECT COUNT(*) as row_count FROM {self.table_name};"
        
        # Add more specific query generation logic here
        
        # Fallback to a generic query
        return f"SELECT * FROM {self.table_name} LIMIT 10;"

    def validate_query(self, query: str) -> bool:
        """Basic SQL injection prevention"""
        lower_query = query.lower()
        forbidden = ['drop', 'truncate', 'delete', 'update', 'insert', 'alter', 'create']
        return not any(word in lower_query for word in forbidden)

    # def execute_query(self, query: str) -> pd.DataFrame:
    #     """Execute SQL query and return results"""
    #     cleaned_query = self.clean_sql_query(query)
    #     if not self.validate_query(cleaned_query):
    #         raise ValueError("Invalid query: Only SELECT statements are allowed")
        
    #     try:
    #         with self.sql_connection as conn:
    #             result = pd.read_sql_query(cleaned_query, conn)
    #             print("result",result)
    #             return result.head()
    #     except Exception as e:
    #         raise Exception(f"Query execution error: {str(e)}\nQuery: {cleaned_query}")
    def execute_query(self, query: str) -> pd.DataFrame:
        """Enhanced query execution with more robust error handling"""
        try:
            cleaned_query = self.clean_sql_query(query)
            
            if not self.validate_query(cleaned_query):
                raise ValueError("Invalid query: Only SELECT statements are allowed")
            
            with self.sql_connection as conn:
                result = pd.read_sql_query(cleaned_query, conn)
                
                # Handle row count queries specially
                if 'row_count' in result.columns:
                    print(f"Total rows: {result['row_count'].values[0]}")
                    return result
                
                return result
        
        except sqlite3.Error as e:
            error_msg = f"SQLite Error: {str(e)}\nQuery: {query}"
            print(error_msg)
            raise ValueError(error_msg)
        
        except Exception as e:
            error_msg = f"Query execution error: {str(e)}\nQuery: {query}"
            print(error_msg)
            raise ValueError(error_msg)

    def _get_file_type(self):
        if self.file_path.lower().endswith('.csv'):
            return 'csv'
        elif self.file_path.lower().endswith('.pdf'):
            return 'pdf'
        raise ValueError("Unsupported file type. Only CSV and PDF files are supported.")

    def _initialize_embeddings(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_path)

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
        self.sql_connection = sqlite3.connect(':memory:')
        df.to_sql('data_table', self.sql_connection, index=False, if_exists='replace')
        self.table_name = 'data_table'
        self.csv_schema = str(df.dtypes)
        print("CSV data loaded into in-memory SQLite database.")

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

    def _clean_text(self, text: str) -> str:
        if not text:
            return ''
        return unicodedata.normalize("NFKD", text).strip()


    def _setup_graph(self):
        def process_query(state: MessagesState):
            query = state["messages"][-1].content
            if self.file_type == 'csv':
                try:
                    # Try to generate query using LLM
                    formatted_prompt = self.PROMPT_CSV.format(
                        table_name=self.table_name,
                        schema=self.csv_schema,
                        question=query
                    )
                    llm_query = self.llm.invoke(formatted_prompt)
                    
                    # Clean and validate LLM-generated query
                    cleaned_query = self.clean_sql_query(llm_query)
                    
                    # Fallback to generated query if LLM fails
                    if not cleaned_query or 'SELECT' not in cleaned_query:
                        cleaned_query = self.generate_appropriate_query(query)
                    
                    # Execute query
                    result = self.execute_query(cleaned_query)
                    
                    # Generate explanation
                    explanation_prompt = self.PROMPT_EXPLAIN.format(
                        question=query,
                        result=result.to_string()
                    )
                    explanation = self.llm.invoke(explanation_prompt)
                    
                    return {"messages": [AIMessage(content=explanation)]}
                
                except Exception as e:
                    return {"messages": [AIMessage(content=f"Error processing query: {str(e)}")]}
                
                # formatted_prompt = self.PROMPT_CSV.format(
                #     table_name=self.table_name,
                #     schema=self.csv_schema,
                #     question=query
                # )
                # response = self.llm.invoke(formatted_prompt)
                # cleaned_query = self.clean_sql_query(response)
                # if not self.validate_query(cleaned_query):
                #     raise ValueError("Invalid query: Only SELECT statements are allowed")
                # result = self.execute_query(cleaned_query)
                # print("result of sql query",result)
                # explanation_prompt = self.PROMPT_EXPLAIN.format(
                #     question=query,
                #     result=result.to_string()
                # )
                # explanation = self.llm.invoke(explanation_prompt)
                # print("explanation",explanation)
                # return {"messages": [AIMessage(content=explanation)]}
            else:
                retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                docs = retriever.get_relevant_documents(query)
                context = "\n".join([doc.page_content for doc in docs])
                formatted_prompt = self.PROMPT_PDF.format(question=query, context=context)
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
            if self.file_type == 'csv':
                formatted_prompt = self.PROMPT_CSV.format(
                    table_name=self.table_name,
                    schema=self.csv_schema,
                    question=query
                )
                async for chunk in self.llm.astream(formatted_prompt):
                    cleaned_query = self.clean_sql_query(chunk)
                    if not self.validate_query(cleaned_query):
                        raise ValueError("Invalid query: Only SELECT statements are allowed")
                    df = self.execute_query(cleaned_query)
                    explanation_prompt = self.PROMPT_EXPLAIN.format(
                        question=query,
                        result=df.to_string()
                    )
                    async for explanation_chunk in self.llm.astream(explanation_prompt):
                        yield explanation_chunk
            else:
                retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
                docs = retriever.get_relevant_documents(query)
                context = "\n".join([doc.page_content for doc in docs])
                formatted_prompt = self.PROMPT_PDF.format(
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

