import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import gradio as gr

# Load environment variables
load_dotenv()

# Set up API key
api_key = os.getenv('GOOGLE_API_KEY')

# Initialize the LLM instance
llm = GoogleGenerativeAI(model='gemini-pro', api_key=api_key)

def format_text(text: str) -> str:
    """Format text into readable paragraphs."""
    paragraphs = text.split('\n')
    formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    return formatted_text

def story_completion(story_line: str, theme: str, length: str, temperature: float) -> str:
    """Generate a story based on inputs."""
    # Adjust word count based on length selection
    word_counts = {
        "Short (250 words)": 250,
        "Medium (500 words)": 500,
        "Long (1000 words)": 1000
    }
    target_words = word_counts[length]
    
    prompt = PromptTemplate.from_template("""
    Please continue the story from the following line, creating a {length} story (approximately {word_count} words) 
    with a {theme} theme. Use vivid details, emotions, and engaging dialogue.
    
    Build upon the themes and atmosphere, develop the plot naturally, and include descriptive language 
    and sensory details to bring the scene to life.
    
    Starting line: {story_line}
    """)

    # Create a new LLM instance with the current temperature
    current_llm = GoogleGenerativeAI(
        model='gemini-pro',
        temperature=temperature,
        api_key=api_key
    )
    
    chain = LLMChain(
        llm=current_llm,
        prompt=prompt,
        output_parser=StrOutputParser(),
        verbose=True
    )

    extracted_text = chain.invoke(input={
        "story_line": story_line,
        "theme": theme,
        "length": length,
        "word_count": target_words
    })
    
    return format_text(extracted_text["text"])

def continue_story(current_story: str, temperature: float) -> str:
    """Continue an existing story."""
    prompt = PromptTemplate.from_template("""
    Continue the following story, maintaining the same style, tone, and themes. 
    Add approximately 250 more words to advance the plot naturally:

    {current_story}
    """)
    
    current_llm = GoogleGenerativeAI(
        model='gemini-pro',
        temperature=temperature,
        api_key=api_key
    )
    
    chain = LLMChain(
        llm=current_llm,
        prompt=prompt,
        output_parser=StrOutputParser(),
        verbose=True
    )

    continuation = chain.invoke(input={"current_story": current_story})
    return format_text(continuation["text"])

def gradio_ui():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # Interactive Story Completion Tool
        Create and shape your story with various themes and settings!
        """)

        with gr.Row():
            with gr.Column(scale=2):
                story_line_input = gr.Textbox(
                    label="Starting Line",
                    placeholder="Enter the starting line of your story here...",
                    lines=2,
                    value=""
                )
                
                with gr.Row():
                    theme_dropdown = gr.Dropdown(
                        choices=[
                            "Adventure", "Mystery", "Romance", "Science Fiction",
                            "Fantasy", "Horror", "Drama", "Comedy"
                        ],
                        label="Theme",
                        value=None
                    )
                    
                    length_dropdown = gr.Dropdown(
                        choices=[
                            "Short (250 words)",
                            "Medium (500 words)",
                            "Long (1000 words)"
                        ],
                        label="Story Length",
                        value=None
                    )
                
                temperature_slider = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="Creativity Level (Temperature)",
                    info="Higher values = more creative but less focused"
                )

            with gr.Column(scale=3):
                output = gr.Textbox(
                    label="Story Output",
                    placeholder="Your story will appear here...",
                    lines=12,
                    interactive=False,
                    value=""
                )

        with gr.Row():
            complete_button = gr.Button("Generate Story", variant="primary")
            regenerate_button = gr.Button("Regenerate")
            continue_button = gr.Button("Continue Story")
            clear_button = gr.Button("Clear")

        # Event handlers
        complete_button.click(
            fn=story_completion,
            inputs=[story_line_input, theme_dropdown, length_dropdown, temperature_slider],
            outputs=[output]
        )

        regenerate_button.click(
            fn=story_completion,
            inputs=[story_line_input, theme_dropdown, length_dropdown, temperature_slider],
            outputs=[output]
        )

        continue_button.click(
            fn=continue_story,
            inputs=[output, temperature_slider],
            outputs=[output]
        )

        clear_button.click(
            fn=lambda: (None, None),
            inputs=[],
            outputs=[story_line_input, output]
        )

    return demo

if __name__ == "__main__":
    app = gradio_ui()
    app.launch()