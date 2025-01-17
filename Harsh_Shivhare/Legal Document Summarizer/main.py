import os
import io
import cv2
import numpy as np
import PyPDF2
from PIL import Image
import easyocr
from dotenv import load_dotenv
from typing import Generator, Dict
import sys
import time

from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import warnings
warnings.filterwarnings("ignore")

class LegalDocumentSummarizer:
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.reader = easyocr.Reader(['en'])
        self.llm = GoogleGenerativeAI(
            model='gemini-pro',
            temperature=0.7,
            api_key=self.api_key
        )

    def extract_text_from_pdf(self, pdf_file, lang=['en']):
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text += f"--- Page {page_num} ---\n"
            text += page.extract_text() + "\n"
            text += self._extract_images_from_page(page, page_num)
        return text

    def _extract_images_from_page(self, page, page_num):
        image_text = ""
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    try:
                        image = xObject[obj]
                        data = image.get_data()
                        img = Image.open(io.BytesIO(data)).convert('RGB')
                        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        result = self.reader.readtext(img_np)
                        image_text += " ".join(detection[1] for detection in result) + "\n"
                    except Exception as e:
                        image_text += f"Error processing image on page {page_num}: {str(e)}\n"
        return image_text

    def _create_summary_prompt(self, document_text, summary_detail="concise"):
        detail_instruction = f"Provide a {summary_detail} summary addressing the above points."
        return PromptTemplate.from_template(f"""
        You are an expert legal document analyzer tasked with providing a comprehensive summary.

        Document Analysis Instructions:

        1. DOCUMENT OVERVIEW:
        - Precise document type
        - Identification of all parties
        - Key jurisdictional information
        - Critical dates and timelines

        2. CRITICAL LEGAL PROVISIONS:
        - Enumerate primary legal clauses
        - Highlight significant rights and obligations
        - Identify unique or non-standard terms

        3. FINANCIAL IMPLICATIONS:
        - Monetary provisions and financial terms
        - Payment structures
        - Monetary obligations and constraints

        4. LEGAL RISK ASSESSMENT:
        - Potential legal vulnerabilities
        - Ambiguous or complex clauses
        - Probable areas of future dispute

        5. TERMINATION AND COMPLIANCE:
        - Contract termination conditions
        - Breach of contract consequences
        - Compliance requirements and penalties

        6. STRATEGIC INSIGHTS:
        - Practical implications of key provisions
        - Potential strategic considerations
        - Noteworthy legal nuances

        Input Document:
        {document_text}

        {detail_instruction}
        """)

    def summarize_document(self, document_text, summary_detail="concise"):
        prompt = self._create_summary_prompt(document_text, summary_detail)
        output_parser = StrOutputParser()
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=output_parser,
            verbose=False
        )
        return self.stream_response(chain, {"document_text": document_text})

    def stream_response(self, chain: LLMChain, inputs: Dict) -> Generator[str, None, None]:
        """Stream the response from the LLM chain"""
        response_tokens = []
        for chunk in chain.stream(inputs):
            if chunk.get('text'):
                response_tokens.append(chunk['text'])
                yield chunk['text']

    @staticmethod
    def _format_summary(text: str) -> str:
        paragraphs = text.split('\n')
        return "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())

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
    summarizer = LegalDocumentSummarizer()
    pdf_file_path = os.path.normpath(input("Please enter the full path to the PDF file (e.g., C:/path/to/file.pdf): "))
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            extracted_text = summarizer.extract_text_from_pdf(pdf_file)
            print("\nGenerating summary...\n")
            stream_printer = StreamPrinter(delay=0.01)
            summary = ""
            for chunk in summarizer.summarize_document(extracted_text, summary_detail="concise"):
                summary += chunk
                stream_printer.print_stream(chunk)
            print("\nSummary generated successfully!\n")
    except FileNotFoundError:
        print(f"The file at {pdf_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()