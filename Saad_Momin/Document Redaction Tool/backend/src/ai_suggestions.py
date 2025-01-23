# File: src/ai_suggestions.py
import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
import json

class AIRedactionSuggester:
    def __init__(self):
        """Initialize the AI suggester with API key from environment variables"""
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def get_redaction_suggestions(self, file_path: str, sensitivity: int = 50) -> List[Dict[str, Any]]:
        """Get AI-powered redaction suggestions for a document"""
        try:
            with open(file_path, 'r') as f:
                text = f.read()

            # Create prompt for the AI
            prompt = f"""Analyze the following text and identify sensitive information that should be redacted.
            Consider PII (Personal Identifiable Information), financial information, and credentials.
            Sensitivity level: {sensitivity}/100
            
            Text to analyze:
            {text}
            
            Provide the results in JSON format with the following structure:
            [
                {{
                    "text": "text to redact",
                    "type": "PII/FINANCIAL/CREDENTIALS",
                    "confidence": confidence_score,
                    "reason": "reason for redaction"
                }}
            ]"""

            response = self.model.generate_content(prompt)
            suggestions = json.loads(response.text)
            return suggestions
        except Exception as e:
            raise Exception(f"Error getting AI suggestions: {str(e)}")

    def analyze_contextual_meaning(self, document_text: str, text: str, type_: str) -> List[Dict[str, Any]]:
        """Analyze contextual meaning for custom redaction"""
        try:
            prompt = f"""Analyze the following document and find contextually similar information to "{text}" that should be redacted.
            Consider the type: {type_}
            
            Document text:
            {document_text}
            
            Provide the results in JSON format with the following structure:
            [
                {{
                    "text": "found text",
                    "confidence": confidence_score,
                    "reason": "reason for suggesting this match"
                }}
            ]"""

            response = self.model.generate_content(prompt)
            matches = json.loads(response.text)
            return matches
        except Exception as e:
            raise Exception(f"Error analyzing context: {str(e)}")
