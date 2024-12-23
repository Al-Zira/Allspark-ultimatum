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

def writing_assistant(topic: str) -> str:
    prompt = PromptTemplate.from_template('''You are a Writing Assistant AI helping with a {ASSIGNMENT_TYPE} in {SUBJECT} at {ACADEMIC_LEVEL} level.

Length requirement: {WORD_COUNT}
Special requirements: {REQUIREMENTS}

Please help by providing:
1. Clear structure and organization suggestions
2. Content improvement recommendations
3. Grammar and style feedback
4. Specific examples to illustrate points

Guidelines:
- Guide rather than write the content
- Explain your suggestions
- Maintain academic integrity
- Keep the student's original voice

Student's current work:
[Student's text goes here]

What specific aspects would you like feedback on?''')
    output_parser = StrOutputParser()
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser, verbose=True)

    # Send the topic as an input dictionary
    extracted_text = chain.invoke(input={"topic": topic})
    text = extracted_text["text"]

    return format_text(text)

   