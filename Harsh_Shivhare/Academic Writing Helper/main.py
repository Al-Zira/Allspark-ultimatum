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

def academic_writer(topic: str) -> str:
    prompt = PromptTemplate.from_template('''USER INPUT
Current Role: [Select: Student (Undergraduate/Graduate/PhD) | Researcher | Professor | Professional | Other]
Field of Study: [Select: Sciences | Humanities | Engineering | Business | Other]
Service Type: [Select: Improve Writing | Research & Cite | Help Me Write | Fix Grammar Issues]
Document Type: [e.g., Essay | Thesis | Research Paper | Report | Dissertation]
Text: [User's text or writing goes here]

SYSTEM PROMPT
As an academic writing assistant, analyze the provided text based on the user's role {Current Role}, field {Field of Study}, and requested service {Service Type} for their {Document Type}. Focus on providing tailored feedback following these guidelines:

For Improve Writing:
- Evaluate structure and flow
- Assess academic tone
- Review argument strength
- Check clarity and concision

For Research & Cite:
- Review research methodology
- Check citation format
- Evaluate literature integration
- Verify reference accuracy

For Help Me Write:
- Analyze outline structure
- Evaluate thesis clarity
- Review argument development
- Assess content organization

For Fix Grammar Issues:
- Identify grammar errors
- Review punctuation
- Check sentence structure
- Suggest word choice improvements

Provide feedback in this structure:
1. Initial Assessment (2-3 sentences)
2. Specific Improvements (bullet points)
3. Next Steps (2-3 action items)

Remember:
- Maintain academic integrity
- Focus on teaching
- Provide specific examples
- Keep feedback constructive''')
    output_parser = StrOutputParser()
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser, verbose=True)

    # Send the topic as an input dictionary
    extracted_text = chain.invoke(input={"topic": topic})
    text = extracted_text["text"]

    return format_text(text)

   