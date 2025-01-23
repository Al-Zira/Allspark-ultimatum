# File: src/file_handler.py
import os
import mimetypes
import pikepdf
import docx
from typing import List, Union
import tempfile
import pdfplumber

class FileHandler:
    MIME_TYPE_MAPPING = {
        'application/pdf': ('pdf', ['.pdf']),
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ('docx', ['.docx', '.doc']),
        'text/plain': ('txt', ['.txt', '.text']),
        'application/rtf': ('rtf', ['.rtf'])
    }

    def validate_file(self, file_path: str) -> bool:
        """
        Validate file type and size
        
        Args:
            file_path (str): Path to the file to validate
        
        Returns:
            bool: Whether file is valid
        """
        # Check file existence
        if not os.path.exists(file_path):
            raise FileNotFoundError("File does not exist")

        # File size check (100MB limit)
        if os.path.getsize(file_path) / (1024 * 1024) > 100:
            raise ValueError("File exceeds 100MB limit")

        # MIME type detection
        file_mime = mimetypes.guess_type(file_path)[0]
        if not file_mime or file_mime not in self.MIME_TYPE_MAPPING:
            # Fallback to extension-based detection
            ext = os.path.splitext(file_path)[1].lower()
            valid_extensions = [ext for mime_info in self.MIME_TYPE_MAPPING.values() for ext in mime_info[1]]
            if ext not in valid_extensions:
                raise ValueError(f"Unsupported file type: {ext}")

        return True

    def get_file_type(self, file_path: str) -> str:
        """
        Get the standardized file type
        
        Args:
            file_path (str): Path to the file
        
        Returns:
            str: Standardized file type
        """
        file_mime = mimetypes.guess_type(file_path)[0]
        if file_mime and file_mime in self.MIME_TYPE_MAPPING:
            return self.MIME_TYPE_MAPPING[file_mime][0]
        
        # Fallback to extension-based detection
        ext = os.path.splitext(file_path)[1].lower()
        for mime_type, (file_type, extensions) in self.MIME_TYPE_MAPPING.items():
            if ext in extensions:
                return file_type
        return None

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from supported file formats
        
        Args:
            file_path (str): Path to the file
        
        Returns:
            str: Extracted text content
        """
        file_type = self.get_file_type(file_path)
        
        extractors = {
            'pdf': self._extract_pdf_text,
            'docx': self._extract_docx_text,
            'txt': self._extract_plain_text,
            'rtf': self._extract_plain_text
        }
        
        extractor = extractors.get(file_type)
        if not extractor:
            raise ValueError(f"No text extractor available for file type: {file_type}")
            
        return extractor(file_path)

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            # First try with pdfplumber
            try:
                text = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text.append(extracted)
                if text:
                    return "\n".join(text)
            except Exception as e:
                print(f"pdfplumber extraction failed: {e}")

            # Fallback to pikepdf
            try:
                text = []
                pdf = pikepdf.Pdf.open(file_path)
                for page in pdf.pages:
                    if hasattr(page, 'Contents'):
                        text.append(str(page.Contents))
                if text:
                    return "\n".join(text)
            except Exception as e:
                print(f"pikepdf extraction failed: {e}")

            raise RuntimeError("Could not extract text from PDF with any available method")
        except Exception as e:
            raise RuntimeError(f"PDF text extraction failed: {str(e)}")

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise RuntimeError(f"DOCX text extraction failed: {e}")

    def _extract_plain_text(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Text file extraction failed: {e}")

    def save_temp_file(self, uploaded_file) -> str:
        """
        Save an uploaded file to a temporary location
        
        Args:
            uploaded_file: StreamlitUploadedFile object
        
        Returns:
            str: Path to the saved temporary file
        """
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name

            self.validate_file(temp_path)
            return temp_path
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise RuntimeError(f"Failed to save temporary file: {e}")
