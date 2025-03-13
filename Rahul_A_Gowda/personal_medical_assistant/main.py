from langchain_neo4j import Neo4jGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import os

# Neo4j Connector Class
class Neo4jConnector:
    def __init__(self, url, username, password):
        self.graph = Neo4jGraph(url=url, username=username, password=password)

    def query(self, query, params=None):
        return self.graph.query(query, params=params)

# Graph Manager Class for Patient Data
class PatientGraphManager:
    def __init__(self, connector: Neo4jConnector):
        self.connector = connector

    def name_exists(self, name):
        query = """
        MATCH (patient:patient {name: $name})
        RETURN patient
        """
        return self.connector.query(query, {'name': name})

    def create_patient(self, username, symptoms, vitals):
        query = """
        CREATE (patient:patient {name: $username})
        CREATE (date:date {date: date()})
        CREATE (symptoms:symptoms {list: $symptoms})
        CREATE (vitals:vitals $vitals)
        CREATE (patient)-[:ON_THE_DAY]->(date)
        CREATE (date)-[:HAS_SYMPTOMS]->(symptoms)
        CREATE (date)-[:HAS_VITALS]->(vitals)
        RETURN patient, date, symptoms, vitals
        """
        return self.connector.query(query, {'username': username, 'symptoms': symptoms, 'vitals': vitals})

    def date_exists(self, name):
        query = """
        MATCH (p:patient {name: $name})-[:ON_THE_DAY]->(d:date)
        WHERE d.date = date(date())
        RETURN d.date as date
        """
        return self.connector.query(query, {'name': name})
    
    def past_data(self, username):
        fetch_data_query = """
        MATCH (patient:patient {name: $username})-[:ON_THE_DAY]->(date:date)
        WITH date
        ORDER BY date.date DESC
        LIMIT 4
        MATCH (date)-[:HAS_SYMPTOMS]->(symptoms:symptoms)
        MATCH (date)-[:HAS_VITALS]->(vitals:vitals)
        RETURN {
            date: date.date,
            symptoms: symptoms.list,
            vitals: vitals
        } as records
        """
        result = self.connector.query(fetch_data_query, params={'username': username})
        return str(result)

    def update_symptoms(self, username, symptoms):
        query = """
        MATCH (p:patient {name : $name})-[:ON_THE_DAY]->(d:date)-[:HAS_SYMPTOMS]->(s:symptoms)
        SET s.list = s.list + $symptoms
        """
        return self.connector.query(query, {'name': username, 'symptoms': symptoms})

    def update_vitals(self, username, vitals):
        try:
            query = """
            MATCH (p:patient {name : $name})-[:ON_THE_DAY]->(d:date)-[:HAS_VITALS]->(v:vitals)
            SET v += $vitals
            RETURN v
            """
            return self.connector.query(query, {'name': username, 'vitals': vitals})
        except Exception as e:
            pass

    def create_new_date_entry(self, username, symptoms, vitals):
        try:
            query = """
            MATCH (patient:patient {name: $name})
            CREATE (date:date {date: date()})
            CREATE (symptoms:symptoms {list: $symptoms})
            CREATE (vitals:vitals $vitals)
            CREATE (patient)-[:ON_THE_DAY]->(date)
            CREATE (date)-[:HAS_SYMPTOMS]->(symptoms)
            CREATE (date)-[:HAS_VITALS]->(vitals)
            RETURN patient, date, symptoms, vitals
            """
            return self.connector.query(query, {'name': username, 'symptoms': symptoms, 'vitals': vitals})
        except Exception as e:
            pass

# Pydantic Model for Parsing Medical Info
class MedicalInfo(BaseModel):
    medical_symptoms: Optional[list[str]] = Field(description="Extract valid medical symptoms(do not include medical vitals) from the text. Correct spelling errors, validate that they are real symptoms, and add them to the list only if valid. If no symptoms are found, return [].")
    medical_vitals: Optional[dict[str, str]] = Field(description="Extract valid medical vitals from the text. Correct spelling errors, validate that they are possible for humans, and format keys/values by replacing spaces with underscores. If no valid vitals are found, return {}.")

# Main Medical Application Class
class MedicalApp:
    def __init__(self, neo4j_connector: Neo4jConnector, llm_model,username):
        self.username = username
        self.graph_manager = PatientGraphManager(neo4j_connector)
        self.llm = llm_model
        parser = JsonOutputParser(pydantic_object=MedicalInfo)
        prompt = PromptTemplate(
            template="answer the query based on the format_instructions and strictly do not generate fake symptoms or vitals verfiy.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        self.chain = prompt | self.llm | parser
        
    def get_context_with_past_data(self, username):
        past_data = self.graph_manager.past_data(username)
        if past_data:
            return f"Patient's historical data: {past_data}\n"
        else:
            return "No historical data available for the patient.\n"

    def setup_chat_prompt_template(self, username):
        past_data_context = self.get_context_with_past_data(username)
        self.chat_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=f""""You are a bot specialized in maintaining healthy lifestyle and diagnosing patients based on the health information they provide.
                                    If they don't share health-related details, avoid pressuring them and continue with the conversation about their workouts or diets. Address medical queries, offer clarity, and suggest ways to maintain a healthy lifestyle.
                                    Respond with gentleness, concern, and conciseness.
                                    Use the provided patient context:\n{past_data_context}
                                    Before diagnosing, ensure the past data is relevant based on the symptoms and vitals' dates.
                                    Only reference the context if necessary for follow-up."
                          """),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        # Create the QA chain with the updated prompt
        self.qa_chain = self.chat_prompt_template | self.llm

    def call_model(self, state: MessagesState):
        response = self.qa_chain.invoke(state["messages"])
        return {"messages": response}

    def cypher_generator(self, user_input):
        response = self.chain.invoke(user_input)
        print(f"respones : {response}")
        symptoms = response.get('medical_symptoms', [])
        vitals = response.get('medical_vitals', {})

        if not self.graph_manager.name_exists(self.username):
            self.graph_manager.create_patient(self.username, symptoms, vitals)
        else:
            if self.graph_manager.date_exists(self.username):
                if symptoms:
                    self.graph_manager.update_symptoms(self.username, symptoms)
                if vitals:
                    self.graph_manager.update_vitals(self.username, vitals)
            else:
                self.graph_manager.create_new_date_entry(self.username, symptoms, vitals)
        
    def setup_workflow(self, username):
        # Set up the chat prompt template with the user's past data
        self.setup_chat_prompt_template(username)
        
        workflow = StateGraph(state_schema=MessagesState)
        
        workflow.add_edge(START,"qa_agent")
        workflow.add_node("qa_agent",self.call_model)
        workflow.add_edge("qa_agent",END)

        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    load_dotenv()
    
    neo4j_url = os.getenv("NEO4J_URI", "neo4j+s://4cc743c4.databases.neo4j.io")
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "i4KWVEy2TBVJD4HtCTLiq5MLjM8uVtq_jMAd4W6j8OM")
    api_key = os.getenv("GOOGLE_API_KEY")
    connector = Neo4jConnector(neo4j_url, neo4j_username, neo4j_password)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=api_key)
    username = input("Enter your username: ").lower()
    app_instance = MedicalApp(neo4j_connector=connector, llm_model=llm,username=username)
    app = app_instance.setup_workflow(username)
    
    while True:
        query = input("you: ")
        if query.lower() == "exit":
            break
        input_messages = [HumanMessage(query)]
        app_instance.cypher_generator(input_messages)
        config = {"configurable": {"thread_id": username}}
        response = app.invoke({"messages": input_messages}, config)["messages"][-1].pretty_print()
        print("\n")