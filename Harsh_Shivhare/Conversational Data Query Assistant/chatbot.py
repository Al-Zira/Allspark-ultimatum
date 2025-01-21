import os
import gradio as gr
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
from typing import Tuple, List, Optional
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
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
        
        # Initialize Pinecone client
        self.pinecone_client = PineconeClient(api_key=config.PINECONE_API_KEY)
        
        # Initialize LangChain's Pinecone vector store
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
        """Check if a namespace exists in the Pinecone index."""
        try:
            index = self.pinecone_client.Index(self.config.PINECONE_INDEX_NAME)
            stats = index.describe_index_stats()
            return namespace in stats.get('namespaces', {})
        except Exception as e:
            raise ValueError(f"Error checking namespace: {e}")

    def process_pdf(self, file_obj) -> Document:
        """Process PDF file and return Document object"""
        try:
            pdf_reader = PdfReader(file_obj)
            text = " ".join(page.extract_text() for page in pdf_reader.pages)
            return Document(page_content=text, metadata={"source": file_obj.name})
        except Exception as e:
            raise ValueError(f"Error processing PDF: {e}")

    def process_csv(self, file_obj) -> Document:
        """Process CSV file and return Document object"""
        try:
            df = pd.read_csv(file_obj)
            text = "\n".join(
                f"{col}: {value}" 
                for _, row in df.iterrows() 
                for col, value in row.items()
            )
            return Document(page_content=text, metadata={"source": file_obj.name})
        except Exception as e:
            raise ValueError(f"Error processing CSV: {e}")

    def create_vector_store(self, docs: List[Document], namespace: str) -> Pinecone:
        """Create or update vector store with documents"""
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
        """Initialize prompt templates"""
        self.document_prompt = PromptTemplate(
            template="{page_content}",
            input_variables=["page_content"]
        )
        
        self.main_prompt = PromptTemplate(
            template="""
            You are a Conversational Data Query Assistant, designed to help users extract and analyze specific information from datasets or logs based on the provided context.

            Question: {question}
            Context: {context}

            Provide a comprehensive and precise answer based on the given context. If the context does not contain sufficient information to answer the question, clearly state that the answer cannot be found in the provided document.
            """,
            input_variables=["context", "question"]
        )

    def upload_file(self, file) -> str:
        """Process uploaded file and initialize vector store"""
        if file is None:
            return "Please upload a file first."
        
        try:
            self.namespace = os.path.splitext(file.name)[0]
            
            if self.processor.check_namespace(self.namespace):
                self.docsearch = Pinecone(
                    index_name=self.config.PINECONE_INDEX_NAME,
                    embedding=self.processor.embeddings,
                    namespace=self.namespace
                )
                return f"Using existing namespace: {self.namespace}"
            
            # Process document based on file type
            doc = (self.processor.process_pdf(file) 
                  if file.name.endswith('.pdf') 
                  else self.processor.process_csv(file))
            
            # Split document into chunks
            docs = self.processor.text_splitter.split_documents([doc])
            
            # Create vector store
            self.docsearch = self.processor.create_vector_store(docs, self.namespace)
            return f"Successfully processed {len(docs)} chunks from {file.name}"
            
        except Exception as e:
            return f"Error processing file: {str(e)}"

    def respond(self, message: str, history: List) -> str:
        """Generate response to user query"""
        if self.docsearch is None:
            return "Please upload a document first."
        
        try:
            # Retrieve relevant documents
            retriever = self.docsearch.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.config.TOP_K_RESULTS},
                namespace=self.namespace
            )
            documents = retriever.get_relevant_documents(message)
            
            if not documents:
                return "No relevant documents found for this query."
            
            # Generate response using LLM chain
            llm_chain = LLMChain(llm=self.processor.llm, prompt=self.main_prompt)
            chain = StuffDocumentsChain(
                llm_chain=llm_chain,
                document_prompt=self.document_prompt,
                document_variable_name="context"
            )
            
            result = chain.invoke({
                "input_documents": documents,
                "question": message
            })
            
            # Add source information
            sources = set(doc.metadata.get('source', 'Unknown') for doc in documents)
            return f"{result['output_text']}\n\nSources: {', '.join(sources)}"
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

def create_interface(config: Config) -> gr.Blocks:
    """Create and configure the Gradio interface"""
    chatbot = ChatBot(config)
    
    with gr.Blocks(title="Conversational Data Query Assistant") as interface:
        gr.Markdown("# Conversational Data Query Assistant")
        
        with gr.Row():
            file_input = gr.File(
                label="Upload PDF or CSV file",
                file_types=[".pdf", ".csv"]
            )
            upload_status = gr.Textbox(
                label="Upload Status",
                interactive=False
            )
        
        chatbot_interface = gr.ChatInterface(
            chatbot.respond,
            chatbot=gr.Chatbot(height=400),
            textbox=gr.Textbox(
                placeholder="Ask a question about your document...",
                container=False,
                scale=7
            )
        )
        
        file_input.upload(
            fn=chatbot.upload_file,
            inputs=[file_input],
            outputs=[upload_status]
        )
    
    return interface

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize configuration
    config = Config(
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
        PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
    )
    
    # Validate configuration
    if not config.GOOGLE_API_KEY or not config.PINECONE_API_KEY:
        raise ValueError("Please set up your API keys in the .env file")
    
    # Create and launch interface
    interface = create_interface(config)
    interface.launch(share=True)

if __name__ == "__main__":
    main()