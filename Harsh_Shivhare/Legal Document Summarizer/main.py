import os
import io
import cv2
import numpy as np
import streamlit as st
import PyPDF2
from PIL import Image
import easyocr
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

class LegalDocumentSummarizer:
    """
    A comprehensive class for summarizing legal documents with multiple extraction methods.
    """
    def __init__(self, api_key=None):
        """
        Initialize the summarizer with Google Generative AI.
        
        :param api_key: Optional API key for Google Generative AI
        """
        # Load environment variables
        load_dotenv()
        
        # Use provided API key or fetch from environment
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        # Initialize OCR reader
        self.reader = easyocr.Reader(['en'])
        
        # Initialize Language Model
        self.llm = GoogleGenerativeAI(
            model='gemini-pro', 
            temperature=0.7, 
            api_key=self.api_key
        )

    def extract_text_from_pdf(self, pdf_file, lang=['en']):
        """
        Extract text from an uploaded PDF file, including text from images.
        
        :param pdf_file: Uploaded PDF file object
        :param lang: Languages for OCR (default English)
        :return: Extracted text from the PDF
        """
        text = ""
        
        # Read PDF file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Iterate through each page
        for page_num, page in enumerate(pdf_reader.pages, 1):
            # Extract text directly from the PDF
            text += f"--- Page {page_num} ---\n"
            text += page.extract_text() + "\n"
            
            # Process images in the page
            text += self._extract_images_from_page(page, page_num)
        
        return text

    def _extract_images_from_page(self, page, page_num):
        """
        Extract text from images on a PDF page.
        
        :param page: PDF page object
        :param page_num: Page number for error logging
        :return: Extracted text from images
        """
        image_text = ""
        
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].get_object()
            
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    try:
                        # Extract and process image
                        image = xObject[obj]
                        data = image.get_data()
                        
                        img = Image.open(io.BytesIO(data)).convert('RGB')
                        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        
                        # Perform OCR
                        result = self.reader.readtext(img_np)
                        
                        # Collect text from OCR
                        image_text += " ".join(detection[1] for detection in result) + "\n"
                    
                    except Exception as e:
                        image_text += f"Error processing image on page {page_num}: {str(e)}\n"
        
        return image_text

    def _create_summary_prompt(self, document_text):
        """
        Create a structured prompt for document summarization.
        
        :param document_text: Text to be summarized
        :return: Formatted prompt template
        """
        return PromptTemplate.from_template("""
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

        Provide a structured, concise summary addressing the above points.
        """)

    def summarize_document(self, document_text):
        """
        Generate a summary of the legal document.
        
        :param document_text: Text of the document to summarize
        :return: Formatted summary
        """
        # Create prompt template
        prompt = self._create_summary_prompt(document_text)
        
        # Create processing chain
        output_parser = StrOutputParser()
        chain = LLMChain(
            llm=self.llm, 
            prompt=prompt, 
            output_parser=output_parser, 
            verbose=False
        )

        # Generate summary
        try:
            summary = chain.invoke(input={"document_text": document_text})
            return self._format_summary(summary.get('text', ''))
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    @staticmethod
    def _format_summary(text: str) -> str:
        """
        Format text into readable paragraphs.
        
        :param text: Raw text output
        :return: Formatted text with proper paragraph breaks
        """
        paragraphs = text.split('\n')
        return "\n\n".join(paragraph.strip() for paragraph in paragraphs if paragraph.strip())

def main():
    """
    Streamlit application for legal document summarization.
    """
    st.title("Legal Document Summarizer")
    st.write("Upload a PDF or paste a legal document text, and get a concise summary!")

    # Initialize summarizer
    summarizer = LegalDocumentSummarizer()

    # Tabs for different input methods
    tab1, tab2 = st.tabs(["Upload PDF", "Paste Text"])

    with tab1:
        # PDF File Uploader
        uploaded_pdf = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_pdf is not None:
            with st.spinner("Extracting text from PDF..."):
                try:
                    # Extract text from uploaded PDF
                    extracted_text = summarizer.extract_text_from_pdf(uploaded_pdf)
                    
                    # Display extracted text (optional)
                    st.text_area("Extracted Text", value=extracted_text, height=200)
                    
                    # Summarization button
                    if st.button("Summarize PDF Document"):
                        with st.spinner("Summarizing..."):
                            try:
                                summary = summarizer.summarize_document(extracted_text)
                                st.success("Summary Generated Successfully!")
                                st.subheader("Summary:")
                                st.write(summary)
                            except Exception as e:
                                st.error(f"Error generating summary: {e}")
                
                except Exception as e:
                    st.error(f"Error extracting text from PDF: {e}")

    with tab2:
        # Text input for document
        document_text = st.text_area(
            "Enter Legal Document Text Here:", 
            height=300, 
            placeholder="Paste the text of the legal document here..."
        )

        # Summarization button for text input
        if st.button("Summarize Text Document"):
            if document_text.strip():
                with st.spinner("Summarizing..."):
                    try:
                        summary = summarizer.summarize_document(document_text)
                        st.success("Summary Generated Successfully!")
                        st.subheader("Summary:")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
            else:
                st.warning("Please enter the text of the legal document to summarize.")

if __name__ == "__main__":
    main()