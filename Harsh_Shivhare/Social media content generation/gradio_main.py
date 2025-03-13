import os
import gradio as gr
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

def format_text(text: str) -> str:
    """Format text into readable paragraphs."""
    paragraphs = text.split('\n')
    formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    return formatted_text

def generate_content(
    topic: str,
    platform: str,
    tone: str,
    emoji_density: str,
    hashtag_count: int,
    max_length: int
) -> str:
    """Generate social media content based on input parameters."""
    prompt = PromptTemplate.from_template('''You are a social media content expert. Create a social media post based on these parameters:

INPUT_PARAMETERS:
TOPIC: {topic}
PLATFORM: {platform}
TONE: {tone}
EMOJI_DENSITY: {emoji_density}
HASHTAG_COUNT: {hashtag_count}
MAX_LENGTH: {max_length} characters

RULES:
1. Match specified tone consistently
2. Use emojis strategically based on density level
3. Include exactly {hashtag_count} relevant hashtags
4. Stay within {max_length} characters
5. Include a hook and call-to-action

Generate the post now.''')
    
    output_parser = StrOutputParser()
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser, verbose=True)
    
    result = chain.invoke({
        "topic": topic,
        "platform": platform,
        "tone": tone,
        "emoji_density": emoji_density,
        "hashtag_count": hashtag_count,
        "max_length": max_length
    })
    
    return format_text(result["text"])

# Create Gradio interface
with gr.Blocks(title="Social Media Content Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📱 Social Media Content Generator")
    
    with gr.Row():
        with gr.Column():
            topic_input = gr.Textbox(
                label="Topic",
                placeholder="Enter your content topic"
            )
            platform_input = gr.Dropdown(
                choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                label="Platform",
                value="Instagram"
            )
            tone_input = gr.Radio(
                choices=["professional", "casual", "humorous", "inspiring"],
                label="Tone",
                value="casual"
            )
            emoji_density = gr.Radio(
                choices=["none", "low", "medium", "high"],
                label="Emoji Density",
                value="medium"
            )
            hashtag_count = gr.Slider(
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                label="Number of Hashtags"
            )
            max_length = gr.Slider(
                minimum=100,
                maximum=2200,
                value=280,
                step=10,
                label="Maximum Length (characters)"
            )
            generate_button = gr.Button("Generate Content", variant="primary")

        with gr.Column():
            output_text = gr.Textbox(
                label="Generated Content",
                lines=10,
                show_copy_button=True
            )

    generate_button.click(
        fn=generate_content,
        inputs=[
            topic_input,
            platform_input,
            tone_input,
            emoji_density,
            hashtag_count,
            max_length
        ],
        outputs=output_text
    )

    gr.Markdown("""
    ### Instructions
    1. Enter your content topic
    2. Select the target platform
    3. Choose your preferred tone
    4. Set emoji density
    5. Adjust hashtag count
    6. Set maximum character length
    7. Click 'Generate Content'
    """)

if __name__ == "__main__":
    demo.launch()