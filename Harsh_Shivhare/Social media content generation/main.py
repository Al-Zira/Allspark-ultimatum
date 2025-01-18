import os
import time
import sys
from typing import Dict, Generator
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.9, api_key=api_key)

class SocialMediaContentGenerator:
    def __init__(self, llm):
        self.llm = llm

    def stream_response(self, chain: LLMChain, inputs: Dict) -> Generator[str, None, None]:
        """Stream the response from the LLM chain."""
        response_tokens = []
        for chunk in chain.stream(inputs):
            if chunk.get('text'):
                response_tokens.append(chunk['text'])
                yield chunk['text']

    def format_text(self, text: str) -> str:
        """Format text into readable paragraphs."""
        paragraphs = text.split('\n')
        formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
        return formatted_text

    def generate_content(
        self,
        topic: str,
        platform: str,
        tone: str,
        emoji_density: str,
        hashtag_count: int,
        max_length: int
    ) -> str:
        """Generate social media content based on input parameters."""
        prompt = PromptTemplate.from_template('''
        You are a social media content expert. Create a social media post based on these parameters:

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

        Generate the post now.
        ''')
        
        output_parser = StrOutputParser()
        chain = LLMChain(llm=self.llm, prompt=prompt, output_parser=output_parser)
        
        full_text = ""
        for chunk in self.stream_response(chain, {
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "emoji_density": emoji_density,
            "hashtag_count": hashtag_count,
            "max_length": max_length
        }):
            full_text += chunk
        
        formatted_text = self.format_text(full_text)
        return formatted_text

class StreamPrinter:
    """Handles streaming output with typewriter effect"""
    def __init__(self, delay: float = 0.02):
        self.delay = delay

    def print_stream(self, text: str):
        """Print text with a typewriter effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(self.delay)

def main():
    # Get user inputs
    topic = input("Enter the topic: ")
    platform = input("Enter the platform (e.g., Instagram, Twitter): ")
    tone = input("Enter the tone (e.g., professional, casual): ")
    emoji_density = input("Enter emoji density (e.g., none, low, medium, high): ")
    hashtag_count = int(input("Enter the number of hashtags: "))
    max_length = int(input("Enter the maximum length in characters: "))

    # Create an instance of the generator
    generator = SocialMediaContentGenerator(llm)

    try:
        # Generate content
        content = generator.generate_content(
            topic=topic,
            platform=platform,
            tone=tone,
            emoji_density=emoji_density,
            hashtag_count=hashtag_count,
            max_length=max_length
        )

        # Use StreamPrinter to print the content with typewriter effect
        printer = StreamPrinter()
        printer.print_stream(content)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()