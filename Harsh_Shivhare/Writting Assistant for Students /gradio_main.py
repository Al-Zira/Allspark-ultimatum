import os
import re
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import gradio as gr

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Create an instance of the LLM
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

def remove_markdown(text: str) -> str:
    """
    Remove markdown formatting from text.
    """
    # Remove headers
    text = re.sub(r'#+\s*', '', text)
    # Remove bold/italic
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
    # Remove bullet points
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text

def format_text(text: str) -> str:
    """
    Format text into clean paragraphs without markdown.
    """
    # Remove markdown
    clean_text = remove_markdown(text)
    
    # Split into paragraphs and clean up
    paragraphs = clean_text.split('\n')
    formatted_text = "\n\n".join(p.strip() for p in paragraphs if p.strip())
    
    return formatted_text

def writing_assistant(topic: str, assignment_type: str, subject: str, academic_level: str, word_count: int, requirements: str) -> str:
    prompt = PromptTemplate.from_template('''You are a Writing Assistant AI helping with a {ASSIGNMENT_TYPE} in {SUBJECT} at {ACADEMIC_LEVEL} level.
Length requirement: Approximately {WORD_COUNT} words.
Special requirements: {REQUIREMENTS}

Please provide structured feedback in clear paragraphs:

1. Suggestions for structure and organization
2. Content improvement recommendations
3. Grammar and style feedback
4. Specific examples to illustrate points

Guidelines:
- Assist in improving the content
- Explain your suggestions clearly
- Maintain academic integrity
- Keep the student's original voice

Topic or current work:
{topic}

What aspects would you like to improve?''')

    chain = LLMChain(llm=llm, proSmpt=prompt, verbose=True)
    
    # Send the input parameters to the chain
    response = chain.invoke({
        "ASSIGNMENT_TYPE": assignment_type,
        "SUBJECT": subject,
        "ACADEMIC_LEVEL": academic_level,
        "WORD_COUNT": word_count,
        "REQUIREMENTS": requirements,
        "topic": topic
    })
    
    return format_text(response['text'])

# Define the Gradio interface with enhanced UI
def run_gradio():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 📝 Advanced Writing Assistant
            #### Get professional feedback and suggestions for your academic writing
            """
        )
        
        with gr.Tab("Writing Assistant"):
            with gr.Column():
                topic_input = gr.Textbox(
                    label="Your Text",
                    placeholder="Enter your topic or paste your current text here...",
                    lines=5,
                    scale=2
                )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        assignment_type = gr.Dropdown(
                            label="📄 Assignment Type",
                            choices=["Essay", "Report", "Research Paper", "Presentation"],
                            value="Essay",
                            container=True
                        )
                        
                        subject = gr.Dropdown(
                            label="📚 Subject",
                            choices=["History", "Computer Science", "Biology", "Mathematics", "Literature"],
                            value="Computer Science",
                            container=True
                        )
                    
                    with gr.Column(scale=1):
                        academic_level = gr.Dropdown(
                            label="🎓 Academic Level",
                            choices=["High School", "College", "Master's", "PhD"],
                            value="College",
                            container=True
                        )
                        
                        word_count = gr.Slider(
                            label="📊 Word Count",
                            minimum=100,
                            maximum=5000,
                            step=100,
                            value=1000,
                            container=True
                        )
                
                requirements = gr.Textbox(
                    label="✨ Special Requirements",
                    placeholder="Enter any special requirements or guidelines...",
                    lines=2
                )
                
                generate_button = gr.Button(
                    "Assist ME!",
                    variant="primary",
                    size="lg"
                )
                
                output_box = gr.Textbox(
                    label="Writing Suggestions",
                    lines=12,
                    interactive=False,
                    container=False
                )
        
        # Add informative footer
        gr.Markdown(
            """
            ### 💡 Tips for best results:
            - Provide clear context about your writing goals
            - Include any specific areas you want to improve
            - Be specific about special requirements
            """
        )
        
        # Define the interaction
        generate_button.click(
            fn=writing_assistant,
            inputs=[topic_input, assignment_type, subject, academic_level, word_count, requirements],
            outputs=output_box
        )
    
    demo.launch()

if __name__ == "__main__":
    run_gradio()