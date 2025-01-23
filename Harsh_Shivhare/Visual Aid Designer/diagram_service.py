import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from mermaid_renderer import MermaidRenderer
import re
import tempfile

class DiagramService:
    SUPPORTED_DIAGRAM_TYPES = [
        "flowchart-diagram", "sequence-diagram", "class-diagram", "state-diagram",
        "entity-relationship-diagram", "gantt-diagram", "pie-chart", "quadrant-chart",
        "reqirement-diagram", "timeline-diagram", "git-diagram", "mind-map-diagram"
    ]

    def __init__(self):
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Initialize components
        self.llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.7, google_api_key=api_key)
        self.renderer = MermaidRenderer()

    def get_diagram_prompt(self, diagram_type):
        """Returns the appropriate prompt template based on diagram type."""
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

        # Add specific diagram type instructions based on the type
        diagram_specific_prompts = {
            "flowchart-diagram": "Create a flowchart diagram showing the process flow with decision points and outcomes.",
            "sequence-diagram": "Create a sequence diagram showing the interactions between components over time.",
            "class-diagram": "Create a class diagram showing the structure with attributes, methods, and relationships.",
            "state-diagram": "Create a state diagram showing different states and their transitions.",
            "entity-relationship-diagram": "Create an ER diagram showing entities, attributes, and relationships.",
            "gantt-diagram": "Create a Gantt chart showing project timeline and dependencies.",
            "pie-chart": "Create a pie chart showing the distribution of components.",
            "quadrant-chart": "Create a quadrant chart showing the positioning of items.",
            "reqirement-diagram": "Create a requirement diagram showing system requirements and dependencies.",
            "timeline-diagram": "Create a timeline diagram showing events in chronological order.",
            "git-diagram": "Create a git graph showing branches and merges.",
            "mind-map-diagram": "Create a mind map showing hierarchical relationships between concepts."
        }

        if diagram_type not in diagram_specific_prompts:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

        return f"{base_prompt}\n\n{diagram_specific_prompts[diagram_type]}\n\n{{user_input}}"

    def clean_mermaid_response(self, response):
        """Cleans the AI response to extract pure Mermaid code."""
        cleaned = response.strip()
        cleaned = re.sub(r'^```mermaid\s*\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)
        cleaned = cleaned.replace('\r\n', '\n')
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        return cleaned

    def generate_diagram(self, diagram_type, description):
        """Generates a diagram based on the type and description."""
        if diagram_type not in self.SUPPORTED_DIAGRAM_TYPES:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

        try:
            # Generate Mermaid code
            template = self.get_diagram_prompt(diagram_type)
            prompt = PromptTemplate(template=template, input_variables=["user_input"])
            chain = LLMChain(prompt=prompt, llm=self.llm)
            mermaid_code = chain.run(user_input=description)
            mermaid_code = self.clean_mermaid_response(mermaid_code)

            # Render diagram to image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                output_path = temp_file.name

            success = self.renderer.render_diagram(mermaid_code, output_path)
            
            if not success:
                raise RuntimeError("Failed to render diagram")

            return {
                "mermaid_code": mermaid_code,
                "image_path": output_path if success else None
            }

        except Exception as e:
            raise RuntimeError(f"Failed to generate diagram: {str(e)}")

if __name__ == "__main__":
    # Example usage
    service = DiagramService()
    try:
        result = service.generate_diagram(
            "class-diagram",
            "Create a class diagram for a simple banking system"
        )
        print("Generated Mermaid Code:\n", result["mermaid_code"])
        print("\nImage saved at:", result["image_path"])
    except Exception as e:
        print(f"Error: {e}") 