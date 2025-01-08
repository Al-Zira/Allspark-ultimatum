import os
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

@dataclass
class WritingRequest:
    """Data class to hold writing request parameters"""
    role: str
    field: str
    service_type: str
    document_type: str
    text: str

class AcademicWritingConfig:
    """Configuration class for Academic Writing Assistant"""
    ROLES = [
        "Student (Undergraduate)", 
        "Student (Graduate)", 
        "Student (PhD)", 
        "Researcher", 
        "Professor", 
        "Professional", 
        "Other"
    ]
    
    FIELDS = [
        "Sciences", 
        "Humanities", 
        "Engineering", 
        "Business", 
        "Other"
    ]
    
    SERVICE_TYPES = [
        "Improve Writing", 
        "Research & Cite", 
        "Help Me Write", 
        "Fix Grammar Issues"
    ]
    
    DOCUMENT_TYPES = [
        "Essay", 
        "Thesis", 
        "Research Paper", 
        "Report", 
        "Dissertation", 
        "Other"
    ]

    @staticmethod
    def get_prompt_template() -> str:
        """Returns the prompt template for the LLM"""
        return '''
        USER INPUT
        Current Role: {role}
        Field of Study: {field}
        Service Type: {service_type}
        Document Type: {document_type}
        Text: {text}

        SYSTEM PROMPT
        As an academic writing assistant, analyze the provided text based on the user's role {role}, field {field}, and requested service {service_type} for their {document_type}. Focus on providing tailored feedback following these guidelines:

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
        - Keep feedback constructive
        '''

class TextFormatter:
    """Class for handling text formatting operations"""
    
    @staticmethod
    def format_paragraphs(text: str) -> str:
        """Format text into readable paragraphs"""
        paragraphs = text.split('\n')
        formatted_text = "\n\n".join(
            paragraph.strip() 
            for paragraph in paragraphs 
            if paragraph.strip()
        )
        return formatted_text

class InputValidator:
    """Class for handling input validation"""
    
    @staticmethod
    def validate_request(request: WritingRequest) -> Tuple[bool, str]:
        """Validate all inputs before processing"""
        if not all([
            request.role, 
            request.field, 
            request.service_type, 
            request.document_type, 
            request.text
        ]):
            return False, "All fields are required. Please fill in missing information."
        return True, ""

class AcademicWritingAssistant:
    """Main class for handling academic writing assistance"""
    
    def __init__(self):
        """Initialize the Academic Writing Assistant"""
        load_dotenv()
        # self.api_key = os.getenv('GOOGLE_API_KEY')
        self.api_key="AIzaSyDYvfMX-qZgtTZC6VXYECu21fnqfQ5HuiY"
        self.llm = GoogleGenerativeAI(
            model='gemini-pro',
            temperature=0.9,
            api_key=self.api_key
        )
        self.formatter = TextFormatter()
        self.validator = InputValidator()
        self._setup_chain()

    def _setup_chain(self):
        """Set up the LangChain processing chain"""
        prompt = PromptTemplate.from_template(
            AcademicWritingConfig.get_prompt_template()
        )
        output_parser = StrOutputParser()
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=output_parser,
            verbose=True
        )

    def process_request(self, request: WritingRequest) -> str:
        """Process academic writing request with user inputs"""
        # Validate inputs
        is_valid, error_message = self.validator.validate_request(request)
        if not is_valid:
            return error_message

        # Process the request
        result = self.chain.invoke({
            "role": request.role,
            "field": request.field,
            "service_type": request.service_type,
            "document_type": request.document_type,
            "text": request.text
        })

        # Format and return the result
        return self.formatter.format_paragraphs(result["text"])

def main():
    """Example usage of the Academic Writing Assistant"""
    # Initialize the assistant
    assistant = AcademicWritingAssistant()

    # Create a sample request
    request = WritingRequest(
        role="Student (Undergraduate)",
        field="Sciences",
        service_type="Improve Writing",
        document_type="Essay",
        text="""Title: The Role of Artificial Intelligence in Transforming Healthcare Systems

Abstract:
Artificial Intelligence (AI) is increasingly reshaping the healthcare landscape by enhancing diagnostic accuracy, optimizing treatment plans, and improving patient outcomes. This paper explores the applications of AI in medical imaging, drug discovery, and personalized medicine. By analyzing current advancements and potential challenges, we highlight AI's capacity to revolutionize healthcare delivery while addressing ethical considerations and the need for transparent AI models.

1. Introduction
The integration of AI into healthcare systems has gained significant traction over the past decade. As healthcare data continues to grow exponentially, traditional analytical methods struggle to process and interpret this information efficiently. AI offers powerful solutions by leveraging machine learning (ML) and deep learning (DL) algorithms to uncover patterns within vast datasets, aiding clinicians in decision-making processes.

2. AI Applications in Healthcare
One of the most prominent applications of AI in healthcare is medical imaging. Convolutional Neural Networks (CNNs) have demonstrated remarkable accuracy in detecting anomalies in radiographic images, surpassing human radiologists in some cases. Similarly, AI-driven drug discovery accelerates the identification of potential compounds by simulating molecular interactions, significantly reducing research and development timelines.

3. Challenges and Ethical Considerations
Despite its potential, the adoption of AI in healthcare is not without challenges. Issues surrounding data privacy, algorithmic bias, and the interpretability of AI models raise concerns among practitioners and policymakers. Ensuring equitable access to AI technologies and fostering collaborative efforts between AI developers and healthcare professionals is essential for sustainable implementation.

4. Conclusion
AI has the potential to transform healthcare delivery by enhancing efficiency, reducing costs, and improving patient care. However, careful consideration of ethical implications and continuous refinement of AI systems are crucial to maximizing their benefits. Future research should focus on developing transparent, unbiased models that align with clinical needs.

Keywords: Artificial Intelligence, Healthcare, Machine Learning, Medical Imaging, Drug Discovery, Ethical AI"""
    )

    # Process the request
    result = assistant.process_request(request)
    print(result)

if __name__ == "__main__":
    main()