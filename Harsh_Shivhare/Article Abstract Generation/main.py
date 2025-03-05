import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import warnings
# import absl.logging

# Suppress GRPC warnings
# os.environ["GRPC_VERBOSITY"] = "ERROR"
# os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

# # Suppress Abseil logs
# absl.logging.set_verbosity("error")

# Suppress general warnings (optional)
warnings.filterwarnings("ignore")


class AbstractGenerator:
    """
    A class to handle the generation of article abstracts using Google Generative AI.
    """

    def __init__(self, model: str, temperature: float, api_key: str):
        """
        Initialize the AbstractGenerator with the necessary LLM settings.

        :param model: The LLM model to use.
        :param temperature: The temperature for text generation.
        :param api_key: The API key for accessing the model.
        """
        self.llm = GoogleGenerativeAI(model=model, temperature=temperature, api_key=api_key)

    @staticmethod
    def format_text(text: str) -> str:
        """
        Format text into readable paragraphs for better presentation.

        :param text: The text to format.
        :return: Formatted text.
        """
        paragraphs = text.split('\n')
        formatted_text = "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
        return formatted_text

    async def generate_abstract(self, article: str, target_ratio: float):
        """
        Generate an abstract for the given article with streaming output.

        :param article: The article text to summarize.
        :param target_ratio: The target compression ratio (percentage).
        :yield: Streamed abstract text.
        """
        # Calculate target word count based on compression ratio
        current_words = len(article.split())
        target_words = int(current_words * (target_ratio / 100))

        prompt = PromptTemplate.from_template(
            """
            Take the following article and summarize it into a concise abstract, capturing its main points, key findings, and purpose. 
            The abstract should be approximately {target_words} words long, providing an accurate and clear overview that highlights 
            the most important aspects of the article while maintaining readability and coherence.

            Here is the article text: {article}
            """
        )

        formatted_prompt = prompt.format(article=article, target_words=target_words)

        try:
            # Stream the response directly from the LLM
            async for chunk in self.llm.astream(formatted_prompt):
                yield chunk
        except Exception as e:
            yield f"Error during processing: {str(e)}"


class ArticleProcessor:
    """
    A class to process articles and manage statistics for abstracts.
    """

    def __init__(self, abstract_generator: AbstractGenerator):
        """
        Initialize the ArticleProcessor.

        :param abstract_generator: An instance of AbstractGenerator.
        """
        self.abstract_generator = abstract_generator

    async def process_article(self, article_text: str, compression_ratio: float, include_stats: bool = False):
        """
        Process the article and return the abstract with optional statistics using streaming.

        :param article_text: The text of the article.
        :param compression_ratio: The desired compression ratio (percentage).
        :param include_stats: Whether to include statistics in the output.
        :yield: Streamed abstract (with optional statistics).
        """
        if not article_text.strip():
            yield "Please enter an article to generate an abstract."
            return

        # Validate compression ratio
        if compression_ratio < 5 or compression_ratio > 50:
            yield "Please enter a compression ratio between 5% and 50%."
            return

        abstract_stream = self.abstract_generator.generate_abstract(article_text, compression_ratio)

        abstract = ""
        async for chunk in abstract_stream:
            abstract += chunk
            yield chunk

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

            yield stats


# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Initialize components
abstract_generator = AbstractGenerator(model='gemini-2.0-flash', temperature=0.9, api_key=api_key)
article_processor = ArticleProcessor(abstract_generator=abstract_generator)

# Example usage
import asyncio

if __name__ == "__main__":
    example_article = input("Enter the article text: ")
    compression_ratio = float(input("Enter the target compression ratio (5-50%): "))
    include_stats = input("Include statistics in the output? (yes/no): ").strip().lower() == "yes"

    print("\nGenerating abstract...\n")

    async def main():
        async for output in article_processor.process_article(example_article, compression_ratio, include_stats):
            print(output, end="", flush=True)

    asyncio.run(main())


    
