import gradio as gr
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import warnings
from typing import List, Dict
from dataclasses import dataclass
import re

warnings.filterwarnings("ignore")

@dataclass
class Config:
    """Configuration class for API keys and database settings"""
    GOOGLE_API_KEY: str
    DB_CONNECTION_STRING: str
    LLM_MODEL: str = 'gemini-pro'
    MAX_ROWS: int = 1000  # Limit for safety

class DatabaseManager:
    def __init__(self, config: Config):
        self.config = config
        self.engine = create_engine(config.DB_CONNECTION_STRING)
        self.inspector = inspect(self.engine)
        
        # Initialize LLM
        self.llm = GoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=0.3,  # Lower temperature for more precise SQL generation
            api_key=config.GOOGLE_API_KEY
        )

    def get_schema_info(self) -> Dict:
        """Get database schema information"""
        schema_info = {}
        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            schema_info[table_name] = {
                'columns': [{'name': col['name'], 'type': str(col['type'])} 
                          for col in columns]
            }
        return schema_info

    def clean_sql_query(self, query: str) -> str:
        """Clean and format SQL query"""
        query = re.sub(r'```sql|```', '', query)
        query = ' '.join(query.split())
        if not query.endswith(';'):
            query += ';'
        return query

    def validate_query(self, query: str) -> bool:
        """Basic SQL injection prevention"""
        lower_query = query.lower()
        forbidden = ['drop', 'truncate', 'delete', 'update', 'insert', 'alter', 'create']
        return not any(word in lower_query for word in forbidden)

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        cleaned_query = self.clean_sql_query(query)
        if not self.validate_query(cleaned_query):
            raise ValueError("Invalid query: Only SELECT statements are allowed")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(cleaned_query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df.head(self.config.MAX_ROWS)
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}\nQuery: {cleaned_query}")

class QueryBot:
    def __init__(self, config: Config):
        self.config = config
        self.db_manager = DatabaseManager(config)
        self._setup_prompts()
        self.schema_info = self.db_manager.get_schema_info()

    def _setup_prompts(self):
        """Initialize prompt templates"""
        self.sql_generation_prompt = PromptTemplate(
            template="""
            You are a MySQL query generator. Using the following database schema:
            {schema}
            
            Generate a SQL query to answer this question: {question}
            
            Rules:
            1. Return ONLY the SQL query without any markdown formatting or explanation
            2. Use only SELECT statements
            3. Include essential columns only
            4. Always include LIMIT clause
            5. Use proper spacing between SQL keywords
            6. Use MySQL date functions (DATE_FORMAT, MONTH, YEAR) instead of SQLite's strftime
            7. For monthly trends, use DATE_FORMAT(date_column, '%%Y-%%m')
            
            Example format for monthly trends:
            SELECT DATE_FORMAT(sale_date, '%%Y-%%m') as month, SUM(quantity) as total_quantity FROM sales GROUP BY month ORDER BY month LIMIT 12;
            """,
            input_variables=["schema", "question"]
        )

        self.response_prompt = PromptTemplate(
            template="""
            Based on the following data results:
            {data}
            
            Provide a clear, concise answer to the question: {question}
            Provide relevant explanation to it
            
            Include relevant numbers and specific details from the data.
            """,
            input_variables=["data", "question"]
        )

    def respond(self, message: str, history: List) -> str:
        """Generate response to user query"""
        try:
            sql_chain = LLMChain(llm=self.db_manager.llm, prompt=self.sql_generation_prompt)
            sql_response = sql_chain.invoke({
                "schema": self.schema_info,
                "question": message
            })
            sql_query = sql_response['text'].strip()
            
            results_df = self.db_manager.execute_query(sql_query)
            
            if results_df.empty:
                return "No data found for your query."
            
            response_chain = LLMChain(llm=self.db_manager.llm, prompt=self.response_prompt)
            response = response_chain.invoke({
                "data": results_df.to_string(),
                "question": message
            })['text']
            
            result_text = "\nResults:\n" + results_df.to_string()
            
            return f"{response}\n\nSQL Query Used:\n```sql\n{sql_query}\n```{result_text}"
            
        except Exception as e:
            return f"Error processing query: {str(e)}"

def create_interface() -> gr.Blocks:
    """Create and configure the Gradio interface"""
    def set_connection_string(db_connection_string):
        try:
            config = Config(
                GOOGLE_API_KEY="AIzaSyBsATgW0xI0cngZ01zn9KGAnqTFzPPeA7A",  # Replace with actual key
                DB_CONNECTION_STRING=db_connection_string
            )
            querybot = QueryBot(config)
            return querybot, "Connection successful! You can now ask queries."
        except Exception as e:
            return None, f"Error setting up connection: {str(e)}"

    querybot = None

    with gr.Blocks(title="Dynamic Database Query Assistant") as interface:
        gr.Markdown("# Dynamic Database Query Assistant")
        gr.Markdown("""
        Enter your database connection string to start interacting with your data:
        Examples:
        - mysql+pymysql://username:password@host:port/db_name
        """)

        db_connection_input = gr.Textbox(label="Database Connection String")
        status_output = gr.Textbox(label="Status", interactive=False)
        connect_button = gr.Button("Connect")

        chatbot_interface = gr.ChatInterface(
            lambda message, history: querybot.respond(message, history) if querybot else "Please set up the database connection first.",
            chatbot=gr.Chatbot(height=400),
            textbox=gr.Textbox(
                placeholder="Ask a question about your data...",
                container=False,
                scale=7
            )
        )

        def on_connect(db_connection_string):
            nonlocal querybot
            querybot, message = set_connection_string(db_connection_string)
            return message

        connect_button.click(on_connect, inputs=db_connection_input, outputs=status_output)

    return interface

def main():
    interface = create_interface()
    interface.launch(share=True)

if __name__ == "__main__":
    main()
