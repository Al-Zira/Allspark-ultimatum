from fastapi import APIRouter, HTTPException, Depends
from app.models.citation import (
    CitationRequest,
    CitationResponse,
    HyperlinkRequest,
    HyperlinkResponse,
    CitationStyle
)
from app.services.citation_service import CitationService
from typing import List

router = APIRouter()
citation_service = CitationService()

@router.post("/validate", response_model=CitationResponse)
async def validate_citation(request: CitationRequest):
    """
    Validate a legal citation according to specified style and jurisdiction.
    """
    try:
        result = await citation_service.validate_citation(
            citation=request.citation,
            style=request.style,
            jurisdiction_type=request.jurisdiction_type
        )
        return CitationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hyperlink", response_model=HyperlinkResponse)
async def generate_hyperlink(request: HyperlinkRequest):
    """
    Generate a hyperlink for a legal citation.
    """
    try:
        hyperlink = await citation_service.generate_hyperlink(
            citation=request.citation,
            style=request.style
        )
        if hyperlink.startswith("Error"):
            raise HTTPException(status_code=500, detail=hyperlink)
        return HyperlinkResponse(hyperlink=hyperlink)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/styles", response_model=List[str])
async def get_citation_styles():
    """
    Get a list of all supported citation styles.
    """
    return [style.value for style in CitationStyle]

@router.get("/jurisdictions", response_model=List[str])
async def get_jurisdictions():
    """
    Get a list of all supported jurisdictions.
    """
    return [
        "US_SUPREME_COURT",
        "US_FEDERAL",
        "US_STATE",
        "UK_SUPREME_COURT",
        "UK_HIGH_COURT",
        "INDIAN_SUPREME",
        "INDIAN_HIGH_COURT",
        "EU_COURT_OF_JUSTICE",
        "INTERNATIONAL_COURT_JUSTICE"
    ] 