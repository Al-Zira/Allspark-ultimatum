import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')

# Create an instance of the LLM, using the 'gemini-pro' model with a specified creativity level
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

def format_text(text: str) -> str:
    """
    Format text into readable paragraphs for better presentation.
    :param te
    xt: The raw text output.
    :return: Formatted text with proper paragraph breaks.
    """
    paragraphs = text.split('\n')  # Split based on newline for initial formatting if exists
    formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    return formatted_text

def content_generation(topic: str) -> str:
    prompt = PromptTemplate.from_template('''You are a social media content expert. Create a social media post based on these parameters:
INPUT_PARAMETERS:

TOPIC: [topic]
PLATFORM: [platform]
TONE: [professional/casual/humorous/inspiring]
EMOJI_DENSITY: [none/low/medium/high]
HASHTAG_COUNT: [number]
MAX_LENGTH: [number] characters

RULES:

Match specified tone consistently
Use emojis strategically based on density level
Include relevant hashtags at the specified count
Stay within character limit
Include a hook and call-to-action

EXAMPLE OUTPUT STRUCTURE:
[Hook with emoji]
[Main message]
[Call-to-action]
[Hashtags]
Generate the post now.''')
    output_parser = StrOutputParser()
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser, verbose=True)

    # Send the topic as an input dictionary
    extracted_text = chain.invoke(input={"topic": topic})
    text = extracted_text["text"]

    return format_text(text)

   