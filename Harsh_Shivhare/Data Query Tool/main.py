from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
import pandas as pd
from typing import List, Dict, Generator
from dataclasses import dataclass
import re
import warnings
import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

@dataclass
class Config:
    """Configuration class for API keys and database settings"""
    GOOGLE_API_KEY: str
    DB_CONNECTION_STRING: str
    LLM_MODEL: str = 'gemini-2.0-flash'
    MAX_ROWS: int = 1000  # Limit for safety

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

class DatabaseManager:
    def __init__(self, config: Config):
        self.config = config
        self.engine = create_engine(config.DB_CONNECTION_STRING)
        self.inspector = inspect(self.engine)
        
        # Initialize LLM with streaming
        self.llm = GoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=0.3,
            api_key=config.GOOGLE_API_KEY,
            streaming=True
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
        self.stream_printer = StreamPrinter()

    def _setup_prompts(self):
        """Initialize prompt templates"""
        self.sql_generation_prompt = PromptTemplate(
            template="""
            You are a versatile query generator for various databases. Using the following database schema:
{schema}

Generate a query to answer this question: {question}

Rules:
1. Return ONLY the query without any markdown formatting or explanation.
2. Use only SELECT (or equivalent) statements for relational databases and aggregation pipelines for MongoDB.
3. Include essential columns/fields only.
4. Always include a LIMIT clause where applicable.
5. Use appropriate date functions or operators for the specific database:
   - MySQL: DATE_FORMAT, MONTH, YEAR
   - PostgreSQL: TO_CHAR, EXTRACT
   - MongoDB: $dateToString, $month, $year
6. For monthly trends:
   - MySQL: DATE_FORMAT(date_column, '%%Y-%%m')
   - PostgreSQL: TO_CHAR(date_column, 'YYYY-MM')
   - MongoDB: {$dateToString: {format: "%Y-%m", date: "$date_field"}}

Example format for monthly trends:
- MySQL/PostgreSQL:
SELECT TO_CHAR(sale_date, 'YYYY-MM') AS month, SUM(quantity) AS total_quantity 
FROM sales 
GROUP BY month 
ORDER BY month 
LIMIT 12;

- MongoDB:
db.sales.aggregate([
    {
        $project: {
            month: { $dateToString: { format: "%Y-%m", date: "$sale_date" } },
            quantity: 1
        }
    },
    {
        $group: {
            _id: "$month",
            total_quantity: { $sum: "$quantity" }
        }
    },
    { $sort: { _id: 1 } },
    { $limit: 12 }
]);

            """,
            input_variables=["schema", "question"]
        )

        self.response_prompt = PromptTemplate(
            template="""
            Based on the following data results:
            {data}
            
            Provide a clear, concise answer to the question: {question}
            Provide relevant explanation to it
            
            Include relevant details from the data.
            """,
            input_variables=["data", "question"]
        )

    def stream_response(self, chain: LLMChain, inputs: Dict) -> Generator[str, None, None]:
        """Stream the response from the LLM chain"""
        response_tokens = []
        for chunk in chain.stream(inputs):
            if chunk.get('text'):
                response_tokens.append(chunk['text'])
                yield chunk['text']

    def query(self, user_question: str):
        """Process a single user query and stream the response"""
        try:
            # Generate SQL query
            sql_chain = LLMChain(llm=self.db_manager.llm, prompt=self.sql_generation_prompt)
            sql_query = ""
            print("\nGenerating SQL query...\n")
            for chunk in self.stream_response(sql_chain, {
                "schema": self.schema_info,
                "question": user_question
            }):
                sql_query += chunk
                
            # Clean and execute the SQL query
            results_df = self.db_manager.execute_query(sql_query)
            
            if results_df.empty:
                self.stream_printer.print_stream("No data found for your query.")
                return

            # Generate and stream the response
            response_chain = LLMChain(llm=self.db_manager.llm, prompt=self.response_prompt)
            print("\nAnalyzing results...\n")
            for chunk in self.stream_response(response_chain, {
                "data": results_df.to_string(),
                "question": user_question
            }):
                self.stream_printer.print_stream(chunk)

            # Print SQL query and results
            print("\n\nSQL Query Used:")
            print(f"```sql\n{sql_query}\n```")
            print("\nResults:")
            print(results_df.to_string())
            print("\n")
            
        except Exception as e:
            self.stream_printer.print_stream(f"Error processing query: {str(e)}")

def get_db_connection_string() -> str:
    """Prompt user for database connection string"""
    print("\nPlease enter your database connection string.")
    print("Example format: mysql+pymysql://username:password@host:port/db_name")
    while True:
        connection_string = input("\nDatabase connection string: ").strip()
        if connection_string:
            return connection_string
        print("Connection string cannot be empty. Please try again.")

def main():
    load_dotenv()
    # Get Google API key from environment variables
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set")
        return

    # Get database connection string from user
    db_connection_string = get_db_connection_string()
    
    # Initialize config and query bot
    config = Config(
        GOOGLE_API_KEY=google_api_key,
        DB_CONNECTION_STRING=db_connection_string
    )
    
    try:
        query_bot = QueryBot(config)
        print("\nConnection successful! You can now start asking questions.")
        
        while True:
            user_question = input("\nAsk a question (or type 'exit' to quit): ")
            if user_question.lower() == 'exit':
                break
                
            query_bot.query(user_question)
            
    except Exception as e:
        print(f"\nError initializing QueryBot: {str(e)}")
        return

if __name__ == "__main__":
    main()