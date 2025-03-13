import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import gradio as gr

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
print(api_key)

# Create an instance of the LLM
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

def format_text(text: str) -> str:
    """Format text into readable paragraphs"""
    paragraphs = text.split('\n')
    formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    return formatted_text

def validate_inputs(role: str, field: str, service_type: str, document_type: str, text: str) -> tuple[bool, str]:
    """Validate all inputs before processing"""
    if not all([role, field, service_type, document_type, text]):
        return False, "All fields are required. Please fill in missing information."
    return True, ""

def academic_writer(role: str, field: str, service_type: str, document_type: str, text: str) -> str:
    """Process academic writing request with user inputs"""
    
    # Validate inputs
    is_valid, error_message = validate_inputs(role, field, service_type, document_type, text)
    if not is_valid:
        return error_message
    
    prompt = PromptTemplate.from_template('''
    USER INPUT
    Current Role: {role}
    Field of Study: {field}
    Service Type: {service_type}
    Document Type: {document_type}
    Text: {text}

    SYSTEM PROMPT
    As an academic writing assistant, analyze the provided text based on the user's role {role}, field {field}, and requested service {service_type} for their {document_type}. Focus on providing tailored feedback following these guidelines:

    For Improve Writing:
    - Evaluate structure and flow
    - Assess academic tone
    - Review argument strength
    - Check clarity and concision

    For Research & Cite:
    - Review research methodology
    - Check citation format
    - Evaluate literature integration
    - Verify reference accuracy

    For Help Me Write:
    - Analyze outline structure
    - Evaluate thesis clarity
    - Review argument development
    - Assess content organization

    For Fix Grammar Issues:
    - Identify grammar errors
    - Review punctuation
    - Check sentence structure
    - Suggest word choice improvements

    Provide feedback in this structure:
    1. Initial Assessment (2-3 sentences)
    2. Specific Improvements (bullet points)
    3. Next Steps (2-3 action items)

    Remember:
    - Maintain academic integrity
    - Focus on teaching
    - Provide specific examples
    - Keep feedback constructive
    ''')
    
    output_parser = StrOutputParser()
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser, verbose=True)

    # Send all inputs to the chain
    result = chain.invoke({
        "role": role,
        "field": field,
        "service_type": service_type,
        "document_type": document_type,
        "text": text
    })
    
    return format_text(result["text"])

# Define input options
ROLES = ["Student (Undergraduate)", "Student (Graduate)", "Student (PhD)", "Researcher", "Professor", "Professional", "Other"]
FIELDS = ["Sciences", "Humanities", "Engineering", "Business", "Other"]
SERVICE_TYPES = ["Improve Writing", "Research & Cite", "Help Me Write", "Fix Grammar Issues"]
DOCUMENT_TYPES = ["Essay", "Thesis", "Research Paper", "Report", "Dissertation", "Other"]

# Create Gradio interface
with gr.Blocks(title="Academic Writing Assistant") as demo:
    gr.Markdown("# Academic Writing Assistant")
    gr.Markdown("Enter your details and text below for academic writing assistance. All fields are required.")
    
    with gr.Row():
        with gr.Column():
            role = gr.Dropdown(
                choices=ROLES,
                label="Current Role*",
                info="Select your current academic role"
            )
            field = gr.Dropdown(
                choices=FIELDS,
                label="Field of Study*",
                info="Select your field of study"
            )
        
        with gr.Column():
            service_type = gr.Dropdown(
                choices=SERVICE_TYPES,
                label="Service Type*",
                info="Select the type of assistance needed"
            )
            document_type = gr.Dropdown(
                choices=DOCUMENT_TYPES,
                label="Document Type*",
                info="Select the type of document"
            )
    
    text_input = gr.Textbox(
        label="Your Text*",
        placeholder="Enter your text here...",
        lines=10,
        info="Enter the text you want to analyze or improve"
    )
    
    submit_btn = gr.Button("Get Feedback", variant="primary")
    
    output = gr.Textbox(
        label="Feedback",
        lines=15,
        show_copy_button=True
    )
    
    # Connect the inputs to the academic_writer function
    submit_btn.click(
        fn=academic_writer,
        inputs=[role, field, service_type, document_type, text_input],
        outputs=output,
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()