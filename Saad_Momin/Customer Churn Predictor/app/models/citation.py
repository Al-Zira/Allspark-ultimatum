from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CitationStyle(str, Enum):
    BLUEBOOK_US = "Bluebook (US)"
    ALWD = "ALWD Guide to Legal Citation"
    CHICAGO_MANUAL_LEGAL = "Chicago Manual of Legal Citation"
    OSCOLA = "Oxford Standard Citation of Legal Authorities"
    CANADIAN_GUIDE = "Canadian Guide to Uniform Legal Citation (McGill Guide)"
    AGLC = "Australian Guide to Legal Citation"
    AUSTLII = "AustLII Citation Format"
    QUEENSLAND_STYLE = "Queensland Courts Citation Style"
    FEDERAL_COURT_AU = "Federal Court of Australia Citation Style"
    HIGH_COURT_AU = "High Court of Australia Citation Style"
    INDIAN_LEGAL = "Indian Law Institute Citation Style"
    INDIAN_LAW_COMMISSION = "Indian Law Commission Citation Style"
    ECHR = "European Court of Human Rights Citation Style"
    ECJ = "European Court of Justice Citation Style"
    INTERNATIONAL_COURT_JUSTICE = "International Court of Justice Citation Style"
    INTERNATIONAL_CRIMINAL_COURT = "International Criminal Court Citation Style"
    UNCITRAL = "UNCITRAL Citation Style"

class CitationRequest(BaseModel):
    citation: str = Field(..., description="The legal citation to validate")
    style: CitationStyle = Field(..., description="The citation style to validate against")
    jurisdiction_type: Optional[str] = Field(None, description="The jurisdiction type (e.g., US_SUPREME_COURT)")

class CitationResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the citation is valid")
    error_details: Optional[List[str]] = Field(None, description="List of validation errors if any")
    suggested_correction: Optional[str] = Field(None, description="Suggested correction for invalid citations")
    source_type: Optional[str] = Field(None, description="Type of legal source (case, statute, etc.)")
    jurisdiction: Optional[str] = Field(None, description="Detected jurisdiction of the citation")

class HyperlinkRequest(BaseModel):
    citation: str = Field(..., description="The legal citation to generate a hyperlink for")
    style: CitationStyle = Field(..., description="The citation style")

class HyperlinkResponse(BaseModel):
    hyperlink: str = Field(..., description="Generated hyperlink for the citation") 