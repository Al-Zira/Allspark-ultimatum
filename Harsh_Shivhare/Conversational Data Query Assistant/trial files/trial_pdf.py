import os
import uuid
import asyncio
from typing import List, AsyncGenerator
from PyPDF2 import PdfReader
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient
from langchain.schema import Document
from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

class CustomerServiceBot:
    def __init__(self, pdf_path: str):
        load_dotenv()
        
        # Initialize configurations
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = "us-east-1"
        self.index_name = "aizira"
        self.namespace = "default"
        
        if not all([self.google_api_key, self.pinecone_api_key]):
            raise ValueError("Please set all required API keys in .env file")
            
        # Initialize Pinecone
        self.pinecone_client = PineconeClient(api_key=self.pinecone_api_key)
        
        # Initialize components
        self.embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        # Initialize LLM with streaming
        self.llm = GoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=self.google_api_key,
            temperature=0.7,
            streaming=True
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Initialize vector store
        self.vector_store = self.process_pdf(pdf_path)
        
        # Initialize LangGraph components
        self.workflow = StateGraph(state_schema=MessagesState)
        self.memory = MemorySaver()
        self.setup_graph()
        
        self.PROMPT = PromptTemplate(
            template="""You are a Conversational Data Query Assistant. Please answer the following question using the provided context.

                    Question: {question}

                    Context: {context}

                    Your response should be clear, detailed, and in a natural, engaging conversational tone. 
                    Make sure to use the context effectively to provide an accurate answer.""",
            input_variables=["question", "context"]
        )

    def setup_graph(self):
        def process_query(state: MessagesState):
            # Get the latest message
            current_query = state["messages"][-1].content
            
            # Use vector store to get relevant context
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3},
                namespace=self.namespace
            )
            docs = retriever.get_relevant_documents(current_query)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Format prompt with context
            formatted_prompt = self.PROMPT.format(
                context=context,
                question=current_query
            )
            
            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)
            return {"messages": [response]}

        # Add nodes and edges to the graph
        self.workflow.add_node("process_query", process_query)
        self.workflow.add_edge(START, "process_query")
        
        # Compile the graph with memory
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        # Generate a unique thread ID for this conversation
        self.thread_id = uuid.uuid4()
        self.config = {"configurable": {"thread_id": self.thread_id}}    

    async def get_context_and_response(self, query: str) -> AsyncGenerator[str, None]:
        """Get context and generate streaming response"""
        try:
            # Get relevant documents
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3},
                namespace=self.namespace
            )
            docs = retriever.get_relevant_documents(query)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Format prompt
            formatted_prompt = self.PROMPT.format(
                context=context,
                question=query
            )
            
            # Stream the response
            async for chunk in self.llm.astream(formatted_prompt):
                yield chunk
                
        except Exception as e:
            yield f"Error: {str(e)}"

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        text = re.sub(r'\s+', ' ', text)
        text = text.replace(' v ', 'v')
        text = text.replace(' e ', 'e')
        text = text.replace(' r ', 'r')
        text = ' '.join(text.split())
        return text

    def process_pdf(self, pdf_path: str) -> Pinecone:
        """Process PDF file with improved text extraction"""
        try:
            index = self.pinecone_client.Index(self.index_name)
            stats = index.describe_index_stats()
            
            if self.namespace in stats.get('namespaces', {}):
                print(f"Using existing document: {self.namespace}")
                return Pinecone(
                    index_name=self.index_name,
                    embedding=self.embeddings,
                    namespace=self.namespace
                )
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    cleaned_text = self.clean_text(text)
                    text_parts.append(cleaned_text)
                
                full_text = ' '.join(text_parts)
                print(f"Extracted and cleaned text length: {len(full_text)} characters")
                
                doc = Document(page_content=full_text, metadata={"source": pdf_path})
            
            splits = self.text_splitter.split_documents([doc])
            print(f"Created {len(splits)} text chunks")
            
            vector_store = Pinecone.from_documents(
                documents=splits,
                embedding=self.embeddings,
                index_name=self.index_name,
                namespace=self.namespace
            )
            
            print(f"Successfully processed {len(splits)} sections from PDF")
            return vector_store
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

async def run_chat_interface():
    """Run the terminal-based chat interface with streaming support"""
    PDF_PATH = "Allspark-ultimatum/Harsh_Shivhare/Conversational Data Query Assistant/Predicting_Sentiment_with_Traditional_ML_Technique__1725483289.pdf"
    
    print("\n=== Welcome to Conversation Data Query Assistant ===")
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    bot = CustomerServiceBot(PDF_PATH)
    
    while True:
        user_input = input("\nUser: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nAI: Thank you for chatting with me. Have a great day!")
            break
            
        if user_input:
            print("\nAI: ", end='', flush=True)
            
            try:
                async for chunk in bot.get_context_and_response(user_input):
                    print(chunk, end='', flush=True)
                print()  # New line after response
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_chat_interface())