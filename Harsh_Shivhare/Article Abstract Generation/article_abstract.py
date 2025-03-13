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

# Initialize LLM
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

def format_text(text: str) -> str:
    """
    Format text into readable paragraphs for better presentation.
    """
    paragraphs = text.split('\n')
    formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    return formatted_text

def article_abstract(article: str, target_ratio: float) -> str:
    """
    Generate an abstract from the given article text with a target compression ratio.
    """
    # Calculate target word count based on compression ratio
    current_words = len(article.split())
    target_words = int(current_words * (target_ratio / 100))
    
    prompt = PromptTemplate.from_template("""
    Take the following article and summarize it into a concise abstract, capturing its main points, key findings, and purpose. 
    The abstract should be approximately {target_words} words long, providing an accurate and clear overview that highlights 
    the most important aspects of the article while maintaining readability and coherence.
    
    Here is the article text: {article}
    """)

    output_parser = StrOutputParser()
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser, verbose=True)
    
    # Generate abstract
    extracted_text = chain.invoke(input={"article": article, "target_words": target_words})
    text = extracted_text["text"]
    
    return format_text(text)

def process_article(article_text: str, compression_ratio: float, include_stats: bool = False) -> str:
    """
    Process the article and return the abstract with optional statistics.
    """
    if not article_text.strip():
        return "Please enter an article to generate an abstract."
    
    # Validate compression ratio
    if compression_ratio < 5 or compression_ratio > 50:
        return "Please enter a compression ratio between 5% and 50%."
    
    abstract = article_abstract(article_text, compression_ratio)
    
    if include_stats:
        # Calculate actual statistics
        word_count = len(article_text.split())
        abstract_word_count = len(abstract.split())
        actual_ratio = round((abstract_word_count / word_count) * 100, 1)
        
        stats = f"\n\nArticle Statistics:\n" \
               f"Original word count: {word_count}\n" \
               f"Abstract word count: {abstract_word_count}\n" \
               f"Target compression ratio: {compression_ratio}%\n" \
               f"Actual compression ratio: {actual_ratio}%"
        
        return abstract + stats
    
    return abstract

# Create Gradio interface
with gr.Blocks(title="Article Abstract Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Article Abstract Generator")
    gr.Markdown("Enter your article text and desired compression ratio to generate a concise abstract.")
    
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(
                label="Article Text",
                placeholder="Paste your article here...",
                lines=10
            )
            with gr.Row():
                compression_slider = gr.Slider(
                    minimum=5,
                    maximum=50,
                    value=25,
                    step=1,
                    label="Target Compression Ratio (%)",
                    info="Select the desired length of the abstract as a percentage of the original text"
                )
        with gr.Column(scale=2):
            output_text = gr.Textbox(
                label="Generated Abstract",
                lines=6,
                interactive=False
            )
    
    with gr.Row():
        include_stats = gr.Checkbox(label="Include Statistics", value=True)
        submit_btn = gr.Button("Generate Abstract", variant="primary")
        clear_btn = gr.Button("Clear", variant="secondary")
    
    # Handle button clicks
    submit_btn.click(
        fn=process_article,
        inputs=[input_text, compression_slider, include_stats],
        outputs=output_text
    )
    
    clear_btn.click(
        fn=lambda: (None, None),
        inputs=None,
        outputs=[input_text, output_text]
    )
    
    # Add example
    gr.Examples(
        examples=[
            ["Education is the process by which a person either acquires or delivers some knowledge to another person. It is also where someone develops essential skills to learn social norms. However, the main goal of education is to help individuals live life and contribute to society when they become older. There are multiple types of education but traditional schooling plays a key role in measuring the success of a person. Besides this, education also helps to eliminate poverty and provides people the chance to live better lives. Let you guys know that this is one of the most important reasons why parents strive to make their kids educate as long as possible. Education is important for everyone as it helps people in living a better life with multiple facilities. It helps individuals to improve their communication skills by learning how to read, write, speak, and listen. It helps people meet basic job requirements and secure better jobs with less effort. The educated population also plays a vital role in building the economy of a nation. Countries with the highest literacy rates are likely to make positive progress in human and economical development. Therefore, it is important for everyone to get the education to live healthy and peaceful life."]
        ],
        inputs=input_text
    )

if __name__ == "__main__":
    demo.launch(share=True)