import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import gradio as gr

# Load environment variables
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Create an instance of the LLM
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, google_api_key=api_key)

def format_text(text: str) -> str:
    """
    Format text into readable paragraphs for better presentation.
    :param text: The raw text output.
    :return: Formatted text with proper paragraph breaks.
    """
    paragraphs = text.split('\n')
    formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    return formatted_text

def blog_generation(topic: str) -> str:
    prompt = PromptTemplate.from_template('''Write a comprehensive blog post about {topic}. The post should be 1200-1500 words long and follow this structure:
Title: Create an engaging, SEO-friendly title
Introduction (150-200 words):

Open with a compelling hook
Identify the main problem or challenge
Explain what readers will learn
End with a transition to the main content

Main Body (800-1000 words):

Break content into 3-4 clear sections with subheadings
Include specific examples and case studies
Support claims with data and statistics
Provide practical, actionable advice
Address potential challenges and solutions

Conclusion (150-200 words):

Summarize key points
Provide clear next steps
End with a strong call-to-action

Requirements:

Use a professional but conversational tone
Include 2-3 relevant statistics
Add bullet points for better readability
Focus on practical, actionable insights
Optimize for SEO with natural keyword usage

Write the complete blog post now.''')
    
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    
    # Get the result and extract the text from the dictionary
    result = chain.invoke({"topic": topic})
    if isinstance(result, dict):
        # Extract text from the dictionary
        text = result.get('text', '')  # This handles the case where 'text' key exists
    else:
        # If result is already a string
        text = str(result)
    
    # Format and return the text
    return format_text(text)

# Gradio interface
def gradio_interface(topic):
    try:
        return blog_generation(topic)
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create the Gradio interface with a title and description
iface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Textbox(label="Enter Blog Topic", placeholder="e.g., Revolution in AI"),
    outputs=gr.Textbox(label="Generated Blog", lines=20, interactive=True),
    title="BLOG GENERATION TOOL",
    description="Generate professional blog posts on any topic using AI",
    theme=gr.themes.Soft(),  # Adding a clean theme
    css="footer {display: none !important;}"  # Hide the footer
)

# Launch the Gradio app
if __name__ == "__main__":
    iface.launch()