from langchain_neo4j import Neo4jGraph
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    # Connect to Neo4j
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # Create constraints and indexes
    initialization_queries = [
        "CREATE CONSTRAINT patient_name IF NOT EXISTS FOR (p:patient) REQUIRE p.name IS UNIQUE",
        "CREATE INDEX date_index IF NOT EXISTS FOR (d:date) ON (d.date)",
        """
        CREATE CONSTRAINT relationships IF NOT EXISTS FOR ()-[r:ON_THE_DAY]->() REQUIRE r.type IN ['ON_THE_DAY'];
        CREATE CONSTRAINT relationships IF NOT EXISTS FOR ()-[r:HAS_SYMPTOMS]->() REQUIRE r.type IN ['HAS_SYMPTOMS'];
        CREATE CONSTRAINT relationships IF NOT EXISTS FOR ()-[r:HAS_VITALS]->() REQUIRE r.type IN ['HAS_VITALS']
        """
    ]
    
    for query in initialization_queries:
        try:
            graph.query(query)
        except Exception as e:
            print(f"Error executing query: {e}")

if __name__ == "__main__":
    init_database()
