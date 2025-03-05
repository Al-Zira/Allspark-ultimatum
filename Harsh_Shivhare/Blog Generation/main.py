import os
from typing import Dict, Optional
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import asyncio

class BlogGenerator:
    """A class to generate various types of blog posts using Google's Generative AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the BlogGenerator with API key and templates.
        
        Args:
            api_key (str, optional): Google API key. If not provided, will try to load from environment.
        """
        self.api_key = api_key or self._load_api_key()
        self.llm = self._initialize_llm()
        self.templates = self._initialize_templates()
        
    def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
    
    def _initialize_llm(self) -> GoogleGenerativeAI:
        """Initialize the language model."""
        return GoogleGenerativeAI(
            model='gemini-2.0-flash',
            temperature=0.9,
            google_api_key=self.api_key
        )
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize blog templates for different types of content."""
        return {
            "technical": '''Write a technical blog post about {topic}. The post should be 1200-1500 words long and follow this structure:
                Title: Create a clear, technical SEO-friendly title
                
                
                
                Use technical terminology appropriately and include code snippets or technical specifications where relevant.
                ''',
            
            "lifestyle": '''Write a lifestyle blog post about {topic}. The post should be 1200-1500 words long and follow this structure:
                Title: Create an engaging, relatable title
                
    
                
                Use a conversational, friendly tone and include personal experiences.
                ''',
            
            "business": '''Write a business-focused blog post about {topic}. The post should be 1200-1500 words long and follow this structure:
                Title: Create a professional, business-oriented title
                
                
                '''
        }
    
    def _format_text(self, text: str) -> str:
        """
        Format text into readable paragraphs.
        
        Args:
            text (str): Raw text to format
            
        Returns:
            str: Formatted text with proper paragraph breaks
        """
        paragraphs = text.split('\n')
        return "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())
    
    def _get_template(self, blog_type: str) -> str:
        """
        Get the template for the specified blog type.
        
        Args:
            blog_type (str): Type of blog to generate
            
        Returns:
            str: Template string for the specified blog type
        """
        return self.templates.get(blog_type.lower(), self.templates["lifestyle"])
    
    async def generate_blog(self, topic: str, blog_type: str = "lifestyle"):
        """
        Asynchronously generate a blog post based on the topic and type, yielding text chunks.
        
        Args:
            topic (str): The topic of the blog post
            blog_type (str): Type of blog (technical, lifestyle, or business)
            
        Yields:
            str: Chunks of the generated blog post
        """
        try:
            template = self._get_template(blog_type)
            prompt = PromptTemplate.from_template(template)
            formatted_prompt = prompt.format(topic=topic)
            
            chunks = []
            async for chunk in self.llm.astream(formatted_prompt):
                yield chunk
                
            # text = ''.join(chunks)
            # formatted_text = self._format_text(text)
            
            # chunk_size = 100  # Define chunk size for streaming output
            # for i in range(0, len(formatted_text), chunk_size):
            #     yield formatted_text[i:i+chunk_size]
                
        except Exception as e:
            raise Exception(f"Blog generation failed: {str(e)}")
    
    @property
    def available_blog_types(self) -> list:
        """Get list of available blog types."""
        return list(self.templates.keys())

async def main():
    """Asynchronous main function to run the blog generator from command line."""
    try:
        # Initialize the blog generator
        generator = BlogGenerator()
        
        # Get user input
        topic = input("Enter blog topic: ")
        print(f"\nAvailable blog types: {', '.join(generator.available_blog_types)}")
        blog_type = input("Enter blog type (default: lifestyle): ").strip() or "lifestyle"
        
        # Generate and print the blog with streaming
        print("\nGenerating blog...\n")
        async for chunk in generator.generate_blog(topic, blog_type):
            print(chunk, end="", flush=True)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())