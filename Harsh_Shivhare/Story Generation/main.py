import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from typing import Generator, Dict
import time
import sys
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Set up API key
api_key = os.getenv('GOOGLE_API_KEY')

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

class StoryGenerator:
    def __init__(self, model='gemini-pro', api_key=api_key, temperature=0.7):
        self.llm = GoogleGenerativeAI(model=model, temperature=temperature, api_key=api_key)
        self.temperature = temperature

    @staticmethod
    def format_text(text: str) -> str:
        """Format text into readable paragraphs."""
        paragraphs = text.split('\n')
        formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
        return formatted_text

    def stream_response(self, chain: LLMChain, inputs: Dict) -> Generator[str, None, None]:
        """Stream the response from the LLM chain"""
        response_tokens = []
        for chunk in chain.stream(inputs):
            if chunk.get('text'):
                response_tokens.append(chunk['text'])
                yield chunk['text']

    def story_completion(self, story_line: str, theme: str, length: str) -> Generator[str, None, None]:
        """Generate a story based on inputs."""
        # Adjust word count based on length selection
        word_counts = {
            "Short (250 words)": 250,
            "Medium (500 words)": 500,
            "Long (1000 words)": 1000
        }
        target_words = word_counts.get(length, 250)
        
        prompt = PromptTemplate.from_template("""
        Please continue the story from the following line, creating a {length} story (approximately {word_count} words) 
        with a {theme} theme. Use vivid details, emotions, and engaging dialogue.
        
        Build upon the themes and atmosphere, develop the plot naturally, and include descriptive language 
        and sensory details to bring the scene to life.
        
        Starting line: {story_line}
        """)
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=StrOutputParser()
        )
        
        yield from self.stream_response(chain, {
            "story_line": story_line,
            "theme": theme,
            "length": length,
            "word_count": target_words
        })

    def continue_story(self, current_story: str) -> Generator[str, None, None]:
        """Continue an existing story."""
        prompt = PromptTemplate.from_template("""
        Continue the following story, maintaining the same style, tone, and themes. 
        Add approximately 250 more words to advance the plot naturally:
        
        {current_story}
        """)
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=StrOutputParser()
        )
        
        yield from self.stream_response(chain, {"current_story": current_story})

# Example usage:
if __name__ == "__main__":
    generator = StoryGenerator()
    stream_printer = StreamPrinter(delay=0.02)
    
    # Generate a new story
    story_line = "In the heart of an ancient forest, the sun barely pierced through the thick canopy."
    theme = "Mystery"
    length = "Medium (500 words)"
    
    print("Generating story...\n")
    chunks = []
    for chunk in generator.story_completion(story_line, theme, length):
        chunks.append(chunk)
    generated_text = ''.join(chunks)
    formatted_story = generator.format_text(generated_text)
    stream_printer.print_stream(formatted_story)
    
    # Continue the existing story
    print("\nContinuing the story...\n")
    continuation_chunks = []
    for chunk in generator.continue_story(formatted_story):
        continuation_chunks.append(chunk)
    continued_text = ''.join(continuation_chunks)
    formatted_continuation = generator.format_text(continued_text)
    stream_printer.print_stream(formatted_continuation)