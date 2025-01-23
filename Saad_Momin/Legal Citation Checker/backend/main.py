import os
import re
import json
from typing import Dict, Any, Optional
import google.generativeai as genai
from dataclasses import dataclass, asdict
from enum import Enum, auto

class CitationStyle(Enum):
    # US Citation Styles
    BLUEBOOK_US = "Bluebook (US)"
    ALWD = "ALWD Guide to Legal Citation"
    CHICAGO_MANUAL_LEGAL = "Chicago Manual of Legal Citation"
    
    # UK Citation Styles
    OSCOLA = "Oxford Standard Citation of Legal Authorities"
    
    # Canadian Citation Styles
    CANADIAN_GUIDE = "Canadian Guide to Uniform Legal Citation (McGill Guide)"
    
    # Australian Citation Styles
    AGLC = "Australian Guide to Legal Citation"
    AUSTLII = "AustLII Citation Format"
    QUEENSLAND_STYLE = "Queensland Courts Citation Style"
    FEDERAL_COURT_AU = "Federal Court of Australia Citation Style"
    HIGH_COURT_AU = "High Court of Australia Citation Style"
    
    # Indian Citation Styles
    INDIAN_LEGAL = "Indian Law Institute Citation Style"
    INDIAN_LAW_COMMISSION = "Indian Law Commission Citation Style"
    
    # European Citation Styles
    ECHR = "European Court of Human Rights Citation Style"
    ECJ = "European Court of Justice Citation Style"
    
    # International Citation Styles
    INTERNATIONAL_COURT_JUSTICE = "International Court of Justice Citation Style"
    INTERNATIONAL_CRIMINAL_COURT = "International Criminal Court Citation Style"
    UNCITRAL = "UNCITRAL Citation Style"

class JurisdictionType(Enum):
    # US Jurisdictions
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    US_SUPREME_COURT = auto()
    US_FEDERAL_CIRCUIT = auto()
    US_DISTRICT_COURT = auto()
    US_STATE_SUPREME = auto()
    US_STATE_APPELLATE = auto()
    US_BANKRUPTCY = auto()
    
    # UK Jurisdictions
    UK_SUPREME_COURT = auto()
    UK_HIGH_COURT = auto()
    UK_COURT_OF_APPEAL = auto()
    UK_CROWN_COURT = auto()
    
    # Indian Jurisdictions
    INDIAN_SUPREME = auto()
    INDIAN_HIGH_COURT = auto()
    INDIAN_DISTRICT_COURT = auto()
    INDIAN_STATE = "indian_state"
    
    # European Jurisdictions
    EU_COURT_OF_JUSTICE = auto()
    EU_GENERAL_COURT = auto()
    EUROPEAN_COURT_HUMAN_RIGHTS = auto()
    
    # International Jurisdictions
    INTERNATIONAL_COURT_JUSTICE = auto()
    INTERNATIONAL_CRIMINAL_COURT = auto()
    WTO_DISPUTE_PANEL = auto()
    PERMANENT_COURT_ARBITRATION = auto()
    
    # Australian Jurisdictions
    AU_HIGH_COURT = auto()
    AU_FEDERAL_COURT = auto()
    AU_FAMILY_COURT = auto()
    AU_STATE_SUPREME = auto()
    AU_DISTRICT_COURT = auto()
    AU_MAGISTRATES = auto()
    AU_TRIBUNALS = auto()
    AU_STATE = "au_state"

@dataclass
class CitationValidationResult:
    """Structured result for citation validation"""
    is_valid: bool
    error_details: list[str] = None
    suggested_correction: Optional[str] = None
    source_type: Optional[str] = None
    jurisdiction: Optional[JurisdictionType] = None

    def to_dict(self):
        """Convert dataclass to dictionary, handling optional fields"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class LegalCitationProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Legal Citation Processor"""
        if not api_key:
            api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("No API key provided. Set GOOGLE_API_KEY environment variable.")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {e}")

    def validate_citation(self, citation: str, style: CitationStyle) -> CitationValidationResult:
        """Validate legal citations"""
        try:
            prompt = f"""
            Strictly Analyze the legal citation '{citation}' according to {style.value} rules.
            
            VALIDATION REQUIREMENTS:
            1. Check citation format
            2. Verify all required components are present
            3. Identify any formatting errors
            4. Consider jurisdiction-specific rules
            
            Output JSON format:
            {{
                "is_valid": boolean,
                "error_details": [list of specific errors],
                "suggested_correction": "corrected citation if needed",
                "source_type": "case/statute/regulation/treaty",
                "jurisdiction": "specific jurisdiction from the citation"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result = self._extract_validation_result(response.text, citation)
            return CitationValidationResult(**result)
        
        except Exception as e:
            return CitationValidationResult(
                is_valid=False, 
                error_details=[f"Validation error: {str(e)}"]
            )

    def hyperlink_citation(self, citation: str) -> str:
        """Generate hyperlink for citation"""
        try:
            prompt = f"""
            For citation '{citation}':
            1. Identify jurisdiction and court level
            2. Generate direct public hyperlink
            3. Return only the URL
            """
            
            response = self.model.generate_content(prompt)
            urls = re.findall(r'https?://\S+', response.text)
            return urls[0] if urls else 'No reliable hyperlink found'
        
        except Exception as e:
            return f"Hyperlink generation error: {str(e)}"

    def reformat_citation(self, citation: str, source_style: CitationStyle, target_style: CitationStyle) -> str:
        """Reformat citation between styles"""
        try:
            prompt = f"""
            Reformat citation '{citation}' from {source_style.value} to {target_style.value}:
            - Preserve source integrity
            - Apply {target_style.value} formatting rules
            - Maintain all critical case information
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            return f"Citation reformatting error: {str(e)}"

    def _extract_validation_result(self, text: str, original_citation: str) -> dict:
        """Extract validation result from AI response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL | re.MULTILINE)
            if json_match:
                json_text = json_match.group(0)
                json_text = re.sub(r':\s*([^{}\[\],"]+)\s*([,}])', r': "\1"\2', json_text)
                json_text = json_text.replace('\n', '').replace('\r', '')
                json_text = json_text.replace('"is_valid": "false"', '"is_valid": false')
                json_text = json_text.replace('"is_valid": "true"', '"is_valid": true')
                
                return json.loads(json_text)
            
            # Fallback parsing if JSON not found
            return {
                "is_valid": "error" not in text.lower(),
                "error_details": re.findall(r'error:\s*(.*)', text, re.IGNORECASE),
                "suggested_correction": original_citation
            }
            
        except Exception:
            return {
                "is_valid": False,
                "error_details": ["Failed to parse validation result"],
                "suggested_correction": original_citation
            }