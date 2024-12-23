import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import warnings
warnings.filterwarnings("ignore")
import re

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Initialize Gemini model
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.7, google_api_key=api_key)

def get_diagram_prompt(diagram_type):
    """
    Returns the appropriate prompt template based on diagram type with enhanced instructions.
    """
    base_prompt = """
    You are an expert in creating detailed and professional Mermaid.js diagrams. Your task is to generate a comprehensive, 
    working Mermaid diagram that includes all relevant components, relationships, and proper syntax.

    Guidelines for ALL diagrams:
    1. Include detailed labels and descriptions
    2. Use meaningful node/component names
    3. Add comments where helpful
    4. Include all relevant relationships and connections
    5. Use appropriate styling and formatting
    6. Implement proper nesting and grouping where applicable
    7. Include error paths and alternative flows
    8. Add notes or annotations for complex parts

    IMPORTANT RULES:
    1. Return ONLY the Mermaid code, no explanations or additional text
    2. Ensure proper syntax is followed
    3. Make diagrams comprehensive but not overwhelming
    4. Include at least 5-10 components/nodes minimum
    5. Add relevant relationships between all components
    """

    diagram_prompts = {
        "flowchart-diagram": """
    FLOWCHART SPECIFIC INSTRUCTIONS:
    1. Start with 'graph TD' (top-down) or 'graph LR' (left-right)
    2. Required components:
       - Initial/Start node
       - Process nodes with clear descriptions
       - Decision nodes with all possible outcomes
       - Terminal/End nodes
       - Error handling paths
       - Subgraphs for related processes

    3. Syntax examples:
       - Node definitions:
         A[Regular node] 
         B(Rounded node)
         C{Decision node}
         D((Circular node))
         E>Asymmetric node]
       
       - Connections:
         Basic: A --> B
         Labeled: A -->|Condition| B
         Dashed: A -.-> B
         Thick: A ==> B
       
       - Subgraphs:
         subgraph Process Name
           content
         end
       
       - Styling:
         style A fill:#f9f,stroke:#333,stroke-width:4px
         
    Example structure:
    graph TD
        Start[Start Process] --> Init[Initialize System]
        Init --> Check{System Check}
        Check -->|Success| Process[Main Process]
        Check -->|Failure| Error[Error Handler]
        
        subgraph Main Flow
            Process --> Step1[Process Step 1]
            Step1 --> Step2[Process Step 2]
        end
        
        subgraph Error Handling
            Error --> Retry[Retry Process]
            Retry -->|Success| Process
            Retry -->|Failure| End[Terminate]
        end

    {user_input}    
    """,
        "sequence-diagram": """
    SEQUENCE DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'sequenceDiagram'
    2. Required components:
       - All relevant participants/actors
       - Complete message flows
       - Alternative paths
       - Loop scenarios
       - Error handling
       - Notes where helpful
    
    3. Syntax examples:
       - Participant definitions:
         participant A as "System A"
         actor B as "User B"
       
       - Message types:
         Solid arrow: A->>B: Message
         Dashed: A-->>B: Response
         Dotted: A-.->B: Note
       
       - Control structures:
         alt Successful case
             A->>B: Success
         else error
             A->>B: Error
         end
         
         loop Every minute
             A->>B: Heartbeat
         end
         
         par Parallel tasks
             A->>B: Task 1
         and
             A->>C: Task 2
         end
       
       - Notes:
         Note over A,B: Explanation
         Note right of A: Comment
    
    Example structure:
    sequenceDiagram
        participant U as User
        participant S as System
        participant DB as Database
        
        U->>S: Request Action
        activate S
        
        S->>DB: Query Data
        alt Data found
            DB-->>S: Return Data
            S-->>U: Success Response
        else No data
            DB-->>S: Empty Result
            S-->>U: Not Found Error
        end
        
        loop Validation
            S->>S: Validate Data
        end
        
        Note over S,DB: Critical Section
        deactivate S
    {user_input}    
    """,
        "class-diagram": """
    CLASS DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'classDiagram'
    2. Required components:
       - All relevant classes
       - Attributes with visibility indicators
       - Methods with parameters and return types
       - Complete inheritance hierarchy
       - Relationships between classes
       - Interface implementations

    3. Syntax guidelines:
       - Class definition:
         class ClassName {
             +publicAttribute: Type
             -privateAttribute: Type
             #protectedAttribute: Type
             ~packageAttribute: Type
             +publicMethod(param: Type): ReturnType
         }

       - Relationships:
         Inheritance: ChildClass <|-- ParentClass
         Composition: Class1 *-- Class2
         Aggregation: Class1 o-- Class2
         Association: Class1 --> Class2
         Implementation: Class ..|> Interface

       - Generic types:
         class Generic~T~ {
             -items: T[]
             +add(item: T): void
         }

    Example structure:

    classDiagram
    class Animal {
        +age: int
        +gender: String
        +isMammal(): bool
        +mate(): void
    }
    class Duck {
        +beakColor: String
        +swim(): void
        +quack(): void
    }
    class Fish {
        -sizeInFeet: int
        -canEat(): bool
    }
    class Zebra {
        +isWild: bool
        +run(): void
    }
    class Generic~T~ {
        -items: T[]
        +add(item: T): void
    }
    
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Generic~T~ *-- Animal
    {user_input}
    """,
        "state-diagram": """
    STATE DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'stateDiagram-v2'
    2. Required components:
       - Initial and final states
       - All possible states
       - Transition conditions
       - Composite states
       - Entry/exit points
       - State descriptions
    
    3. Syntax examples:
       - State definitions:
         state "State Name" as S1
         state "Composite State" as CS {
             [*] --> SubState1
             SubState1 --> SubState2
         }
       
       - Transitions:
         Simple: S1 --> S2
         With condition: S1 --> S2: Condition
         With note: note right of S1: State note
       
       - Special states:
         [*] : Initial/Final state
         fork_state <<fork>>
         join_state <<join>>
       
       - Direction:
         direction LR
    
    Example structure:
    stateDiagram-v2
        [*] --> Idle
        
        state "System Running" as SR {
            [*] --> Ready
            
            state "Processing" as P {
                [*] --> Loading
                Loading --> Computing: Data Ready
                Computing --> Complete: Process Done
            }
            
            Ready --> P: Start Process
            P --> Ready: Complete
        }
        
        Idle --> SR: Power On
        SR --> Idle: Shutdown
        
        note right of SR
            System in operational state
            Handling normal processes
        end note
    {user_input}    
    """,
        "entity-relationship-diagram": """
    ER DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'erDiagram'
    2. Required components:
       - All entities with attributes
       - Relationship types
       - Cardinality
       - Attribute types
       - Key fields
    
    3. Syntax examples:
       - Entity definition:
         ENTITY {
             type key_field PK
             type required_field
             type optional_field
         }
       
       - Relationships:
         One-to-One: ||--||
         One-to-Many: ||--|{
         Many-to-Many: }|--|{
       
       - Attributes:
         string
         int
         date
         boolean
    
    Example structure:
    erDiagram
        CUSTOMER ||--o{ ORDER : places
        ORDER ||--|{ LINE_ITEM : contains
        CUSTOMER ||--o{ PAYMENT : makes
        
        CUSTOMER {
            string id PK
            string name
            string email
            date joinDate
            boolean active
        }
        
        ORDER {
            string id PK
            string customerId FK
            date orderDate
            decimal total
            string status
        }
        
        LINE_ITEM {
            string id PK
            string orderId FK
            string productId FK
            int quantity
            decimal price
        }
        
        PAYMENT {
            string id PK
            string customerId FK
            decimal amount
            date paymentDate
            string method
        }
    {user_input}    
    """,
        "gantt-diagram": """
    GANTT DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'gantt'
    2. Required components:
       - Project header
       - Task descriptions
       - Dates or duration
       - Dependencies
    
    3. Syntax examples:
       - Header:
         gantt
    title Project Timeline
       
       - Sections:
         section Section Title
         Task1 :a1, 2024-01-01, 7d
         Task2 :after a1, 5d
    
    Example structure:
    gantt
    title Development Project
    section Planning
        Define Requirements :a1, 2024-01-01, 10d
    section Execution
        Development :a2, after a1, 20d
        Testing :a3, after a2, 15d
    section Deployment
        Rollout :a4, after a3, 5d
    {user_input}    
    """,
        "pie-chart": """
    PIE CHART SPECIFIC INSTRUCTIONS:
    1. Start with 'pie'
    2. Required components:
       - Title
       - Data points with labels
    
    Example structure:
    pie title User Distribution
        "Group A" : 45
        "Group B" : 35
        "Group C" : 20

    {user_input}    
    """,
        "quadrant-chart": """
    QUADRANT CHART SPECIFIC INSTRUCTIONS:
    1. Start with 'quadrantChart'
    2. Required components:
       - Axis labels
       - Points with names and coordinates
    
    Example structure:
    quadrantChart
    x-axis Start --> End
    y-axis Low --> High
        "Project Alpha" : [1, 2]
        "Project Beta" : [3, 4]

    {user_input}    
    """,
        "reqirement-diagram": """
    REQUIREMENT DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'requirementDiagram'
    2. Required components:
       - Requirements with IDs and descriptions
       - Relationships between requirements
    
    Example structure:
    requirementDiagram
        requirement Requirement1 {
            id: R1
            text: "Requirement Description"
        }
        requirement Requirement2 {
            id: R2
            text: "Another Requirement Description"
        }
        Requirement1 --> Requirement2 : depends on
    {user_input}    
    """,
        "timeline-diagram": """
    TIMELINE DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'timeline'
    2. Required components:
       - Key events with labels
       - Dates
       - Optional descriptions
    
    Example structure:
    timeline
        title Project Milestones
        2024-01-01: "Project Kickoff"
        2024-03-15: "Prototype Complete"
        2024-06-30: "Release Candidate"
        2024-12-31: "Project Completion"

    {user_input}    
    """,
        "git-diagram": """
    GIT DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'gitGraph'
    2. Required components:
       - Branches
       - Commits
       - Merges
    
    Example structure:
    gitGraph
        commit id: "Initial Commit"
        branch develop
        commit id: "Develop Feature A"
        checkout main
        merge develop
        commit id: "Release 1.0"

    {user_input}    
    """,
        "mind-map-diagram": """
    MIND MAP DIAGRAM SPECIFIC INSTRUCTIONS:
    1. Start with 'mindmap'
    2. Required components:
       - Root node
       - Branches
       - Leaf nodes
    
    Example structure:
    mindmap
  root((mindmap))
    Origins
      Long history
      ::icon(fa fa-book)
      Popularisation
        British popular psychology author Tony Buzan
    Research
      On effectiveness<br/>and features
      On Automatic creation
        Uses
            Creative techniques
            Strategic planning
            Argument mapping
    Tools
      Pen and paper
      Mermaid

    {user_input}
    """
    }
    if diagram_type not in diagram_prompts:
        raise ValueError(f"Unsupported diagram type: {diagram_type}. Supported types are: {', '.join(diagram_prompts.keys())}")


    return (base_prompt + diagram_prompts[diagram_type]).strip()



def clean_mermaid_response(response):
    cleaned = response.strip()
    cleaned = re.sub(r'^```mermaid\s*\n', '', cleaned)
    cleaned = re.sub(r'\n```$', '', cleaned)
    cleaned = cleaned.replace('\r\n', '\n')
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    return cleaned

def generate_mermaid_code(diagram_type, user_input):
    try:
        template = get_diagram_prompt(diagram_type)
        # Convert all single braces to doubles except for the placeholder
        template = template.replace("{", "{{").replace("}", "}}").replace("{{user_input}}", "{user_input}")
        
        prompt = PromptTemplate(template=template, input_variables=["user_input"])
        chain = LLMChain(prompt=prompt, llm=llm)
        result = chain.run(user_input=user_input)
        
        # Clean response
        result = result.strip()
        if result.startswith("```"):
            result = "\n".join(result.split("\n")[1:-1])
            
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to generate Mermaid.js code: {str(e)}")



if __name__ == "__main__":
    # print(diagram_prompts.keys())
    # diagram_type = input("Enter the diagram type: ")
    # user_input = input("Enter the details for the diagram: ")
    diagram_type='class-diagram'
    user_input='Draw a class diagram for banking system'
    try:
        mermaid_code = generate_mermaid_code(diagram_type, user_input)
        print("Generated Mermaid.js Code:\n", mermaid_code)
    except Exception as e:
        print(f"Error: {e}")

