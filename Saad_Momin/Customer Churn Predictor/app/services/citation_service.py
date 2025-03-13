from typing import Optional, Dict, Any
import google.generativeai as genai
from app.core.config import get_settings
from app.models.citation import CitationStyle
import re
import json

settings = get_settings()

class CitationService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def validate_citation(
        self,
        citation: str,
        style: CitationStyle,
        jurisdiction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a legal citation using the Gemini model.
        """
        try:
            # Build the prompt
            jurisdiction_context = f"\nJurisdiction: {jurisdiction_type}" if jurisdiction_type else ""
            
            prompt = f"""
            Analyze this legal citation according to {style.value} rules:
            Citation: {citation}{jurisdiction_context}
            
            Validation requirements:
            1. Check citation format
            2. Verify all required components
            3. Check jurisdiction-specific rules
            4. Identify any formatting errors
            
            Return a JSON object with:
            {{
                "is_valid": boolean,
                "error_details": [list of specific errors],
                "suggested_correction": "corrected citation if needed",
                "source_type": "case/statute/regulation/treaty",
                "jurisdiction": "detected jurisdiction"
            }}
            """
            
            # Get response from model
            response = self.model.generate_content(prompt)
            result = self._parse_validation_response(response.text, citation)
            
            # Validate jurisdiction if specified
            if jurisdiction_type and result.get("jurisdiction") != jurisdiction_type:
                result["is_valid"] = False
                result["error_details"] = result.get("error_details", []) + [
                    f"Citation jurisdiction '{result.get('jurisdiction')}' does not match specified jurisdiction: {jurisdiction_type}"
                ]
            
            return result
            
        except Exception as e:
            return {
                "is_valid": False,
                "error_details": [f"Validation error: {str(e)}"],
                "source_type": None,
                "jurisdiction": None
            }
    
    async def generate_hyperlink(self, citation: str, style: CitationStyle) -> str:
        """
        Generate a hyperlink for a legal citation.
        """
        try:
            prompt = f"""
            For this legal citation: '{citation}'
            Generate a direct public hyperlink based on jurisdiction:
            - US Supreme Court/Federal: Use Google Scholar
            - UK cases: Use BAILII
            - EU cases: Use EUR-Lex
            - International: Use official court databases
            
            Return only the URL, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            urls = re.findall(r'https?://\S+', response.text)
            
            return urls[0] if urls else "No hyperlink available"
            
        except Exception as e:
            return f"Error generating hyperlink: {str(e)}"
    
    def _parse_validation_response(self, text: str, original_citation: str) -> Dict[str, Any]:
        """Parse and clean the model's response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            # Clean and parse JSON
            json_text = json_match.group(0)
            json_text = re.sub(r':\s*([^{}\[\],"]+)\s*([,}])', r': "\1"\2', json_text)
            json_text = json_text.replace('\n', '').replace('\r', '')
            
            # Parse JSON
            result = json.loads(json_text)
            
            # Ensure required fields
            return {
                "is_valid": bool(result.get("is_valid", False)),
                "error_details": result.get("error_details", []),
                "suggested_correction": result.get("suggested_correction", original_citation),
                "source_type": result.get("source_type"),
                "jurisdiction": result.get("jurisdiction")
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error_details": [f"Response parsing error: {str(e)}"],
                "suggested_correction": original_citation,
                "source_type": None,
                "jurisdiction": None
            } 