import os
import time
import pandas as pd
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_google_genai import GoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from dotenv import load_dotenv
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import uuid
import warnings
warnings.filterwarnings("ignore")

load_dotenv()


class CSVChatAgent:
    PROMPT = "Context:\n{context}\n\nQuestion:\n{question}"

    def __init__(
        self,
        csv_path: str,
        pinecone_index_name: str = "aizira2",
        namespace: str = "customer-churn-analysis",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        google_api_key: Optional[str] = None,
        pinecone_api_key: Optional[str] = None,
    ):
        self.csv_path = csv_path
        self.pinecone_index_name = pinecone_index_name
        self.namespace = namespace
        self.embedding_model = embedding_model
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")

        # Initialize components
        self._initialize_embeddings()
        self._initialize_pinecone()
        self._process_csv()
        self.llm = GoogleGenerativeAI(
            model="models/gemini-pro", google_api_key=self.google_api_key
        )
        self.workflow = StateGraph(state_schema=MessagesState)
        self.memory = MemorySaver()
        self._setup_graph()
        self.PROMPT = PromptTemplate(
            template="""You are a specialized CSV Data Analysis Assistant with expertise in interpreting and analyzing CSV data files. Please answer the following question using the provided context.

                    Question: {question}

                    Context: {context}

                    Your response should be clear, detailed, and in a natural, engaging conversational tone. 
                    Make sure to use the context effectively to provide an accurate answer.
                    
                    AFTER the output always mention like this does not carry any data analysis processing.""",
            input_variables=["question", "context"],
        )

    def _initialize_embeddings(self):
        """Initialize HuggingFace embeddings model"""
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        self.pinecone_client = PineconeClient(api_key=self.pinecone_api_key)

        # Check if the index exists and create if necessary
        if self.pinecone_index_name not in self.pinecone_client.list_indexes().names():
            print(f"Index '{self.pinecone_index_name}' does not exist. Creating it now...")
            sample_embedding = self.embeddings.embed_query("sample text")
            self.pinecone_client.create_index(
                name=self.pinecone_index_name,
                dimension=len(sample_embedding),
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            # Wait for index to be ready
            while not self.pinecone_client.describe_index(self.pinecone_index_name).status.get(
                "ready"
            ):
                time.sleep(1)
            print("Index is ready.")
        else:
            print(f"Using existing index '{self.pinecone_index_name}'.")

    def _process_csv(self):
        """Process CSV data and upload to Pinecone"""
        df = pd.read_csv(self.csv_path)
        documents = [
            Document(
                page_content="\n".join([f"{col}: {val}" for col, val in row.items()]),
                metadata={"source": self.csv_path, "row": idx},
            )
            for idx, row in df.iterrows()
        ]
        self.vector_store = Pinecone.from_documents(
            documents=documents,
            embedding=self.embeddings,
            index_name=self.pinecone_index_name,
            namespace=self.namespace,
        )

    def _setup_graph(self):
        """Setup Langgraph workflow graph"""

        def process_query(state: MessagesState):
            current_query = state["messages"][-1].content

            # Retrieve relevant context
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}, namespace=self.namespace
            )
            docs = retriever.get_relevant_documents(current_query)
            context = "\n".join([doc.page_content for doc in docs])

            # Format and send to LLM
            formatted_prompt = self.PROMPT.format(context=context, question=current_query)
            response = self.llm.invoke(formatted_prompt)

            # Append assistant response to messages
            return {"messages": [AIMessage(content=response)]}

        # Add nodes and edges to the graph
        self.workflow.add_node("process_query", process_query)
        self.workflow.add_edge(START, "process_query")

        # Compile the workflow with memory
        self.app = self.workflow.compile(checkpointer=self.memory)
        self.thread_id = uuid.uuid4()
        self.config = {"configurable": {"thread_id": self.thread_id}}

    def run_chat(self):
        """Run chat session"""
        print("Customer Data Assistant: Hi! Ask me about the customer data. Type 'exit' to end.")
        while True:
            try:
                query = input("\nYou: ")
                if query.lower() == "exit":
                    break

                # Use HumanMessage instead of dictionary
                state = {"messages": [HumanMessage(content=query)]}  # Changed to HumanMessage
                response = self.app.invoke(state, config=self.config)
                print(f"\nAssistant: {response['messages'][-1].content}")  # Access .content
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break
            except Exception as e:
                print(f"\nError processing request: {e}")

        print("\nAssistant: Goodbye!")


if __name__ == "__main__":
    csv_path = input("Enter the path to your CSV file: ")
    agent = CSVChatAgent(
        csv_path=csv_path,
        pinecone_index_name="aizira2",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    )
    agent.run_chat()