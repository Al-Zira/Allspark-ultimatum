from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import re
import requests
from main import CitationStyle, JurisdictionType, LegalCitationProcessor, CitationValidationResult
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LegalCite API",
    description="API for legal citation validation and processing",
    version="1.0.0"
)

# Initialize the citation processor
citation_processor = LegalCitationProcessor(api_key=os.getenv('GOOGLE_API_KEY'))

# Citation source mapping
CITATION_SOURCES = {
    "US_SUPREME_COURT": [
        "https://supreme.justia.com/cases/federal/us/{volume}/{page}/",
        "https://scholar.google.com/scholar_case?case={case_name}&volume={volume}&page={page}",
        "https://caselaw.findlaw.com/us-supreme-court/{volume}/{page}.html"
    ],
    "US_FEDERAL": [
        "https://law.justia.com/cases/federal/{court}/{year}/{case_number}/",
        "https://caselaw.findlaw.com/court/{court}/{year}/{case_number}.html"
    ],
    "INDIAN_SUPREME": [
        "https://indiankanoon.org/doc/{doc_id}/",
        "https://www.scconline.com/citations/{year}/{volume}/{page}",
        "https://main.sci.gov.in/judgments/{year}/{case_number}"
    ],
    "UK_SUPREME_COURT": [
        "https://www.bailii.org/uk/cases/UKSC/{year}/{case_number}.html",
        "https://www.supremecourt.uk/cases/{year}/{case_number}"
    ],
    "AU_HIGH_COURT": [
        "http://www.austlii.edu.au/au/cases/cth/HCA/{year}/{case_number}.html",
        "https://jade.io/citation/{year}HCA{case_number}"
    ],
    "EU_COURT_OF_JUSTICE": [
        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex_number}",
        "https://curia.europa.eu/juris/liste.jsf?num={case_number}&year={year}"
    ]
}

def extract_citation_components(citation: str) -> Dict[str, str]:
    """Extract components from citation text"""
    components = {}
    
    # US Supreme Court pattern (simplified)
    us_supreme = re.match(r'(\d+)\s+U\.?S\.?\s+(\d+)', citation)
    if us_supreme:
        components.update({
            'volume': us_supreme.group(1),
            'page': us_supreme.group(2)
        })
        print(f"Extracted US Supreme Court components: {components}")  # Debug log
        return components
    
    # Indian Supreme Court pattern
    indian = re.match(r'(?:AIR|SCC)\s+(\d{4})\s+SC\s+(\d+)', citation)
    if indian:
        components.update({
            'year': indian.group(1),
            'page': indian.group(2)
        })
    
    # UK Supreme Court pattern
    uk = re.match(r'\[(\d{4})\]\s+UKSC\s+(\d+)', citation)
    if uk:
        components.update({
            'year': uk.group(1),
            'case_number': uk.group(2)
        })
    
    # Australian High Court pattern
    au = re.match(r'(?:\[(\d{4})\])?\s*(\d+)?\s*(?:CLR|ALR)\s*(\d+)', citation)
    if au:
        components.update({
            'year': au.group(1) if au.group(1) else '',
            'volume': au.group(2) if au.group(2) else '',
            'page': au.group(3)
        })
    
    # EU Court of Justice pattern
    eu = re.match(r'Case\s+(?:C-)?(\d+)/(\d+)', citation)
    if eu:
        components.update({
            'case_number': eu.group(1),
            'year': eu.group(2)
        })
    
    return components

def validate_url(url: str) -> bool:
    """Check if URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_citation_links(citation: str, jurisdiction: str) -> List[str]:
    """Generate possible citation links based on jurisdiction"""
    components = extract_citation_components(citation)
    valid_links = []
    
    print(f"Generating links for jurisdiction: {jurisdiction}")  # Debug log
    print(f"Citation components: {components}")  # Debug log
    
    if jurisdiction in CITATION_SOURCES:
        for url_template in CITATION_SOURCES[jurisdiction]:
            try:
                # For incomplete templates, add placeholder values
                if 'case_name' not in components:
                    components['case_name'] = ''
                if 'year' not in components:
                    components['year'] = ''
                
                url = url_template.format(**components)
                print(f"Generated URL: {url}")  # Debug log
                
                # Skip validation for now to see all generated URLs
                valid_links.append(url)
            except Exception as e:
                print(f"Error generating URL: {str(e)}")  # Debug log
                continue
    
    if not valid_links:
        # Fallback to a basic Justia link for US Supreme Court cases
        if jurisdiction == "US_SUPREME_COURT" and 'volume' in components and 'page' in components:
            fallback_url = f"https://supreme.justia.com/cases/federal/us/{components['volume']}/{components['page']}/"
            valid_links.append(fallback_url)
    
    return valid_links

class CitationRequest(BaseModel):
    citation: str
    style: str
    jurisdiction: Optional[str] = None

class ReformatRequest(BaseModel):
    citation: str
    source_style: str
    target_style: str

@app.get("/")
async def root():
    return {"message": "Welcome to LegalCite API"}

@app.get("/styles")
async def get_citation_styles():
    """Get all available citation styles"""
    return {style.name: style.value for style in CitationStyle}

@app.get("/jurisdictions")
async def get_jurisdictions():
    """Get all available jurisdictions"""
    return {j.name: j.value for j in JurisdictionType}

@app.post("/validate")
async def validate_citation(request: CitationRequest):
    """Validate a legal citation"""
    try:
        style = CitationStyle[request.style]
        result = citation_processor.validate_citation(request.citation, style)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/hyperlink")
async def get_hyperlink(request: CitationRequest):
    """Generate hyperlink for a citation with multiple fallback sources"""
    try:
        # Get all possible valid links
        links = generate_citation_links(request.citation, request.jurisdiction)
        
        if not links:
            # Fallback to Google Scholar search if no direct links found
            case_name = extract_citation_components(request.citation).get('case_name', '')
            if case_name:
                scholar_link = f"https://scholar.google.com/scholar?q={case_name.replace(' ', '+')}"
                links.append(scholar_link)
        
        return {
            "hyperlinks": links,
            "primary_link": links[0] if links else None,
            "alternate_links": links[1:] if len(links) > 1 else []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reformat")
async def reformat_citation(request: ReformatRequest):
    """Reformat a citation from one style to another"""
    try:
        source_style = CitationStyle[request.source_style]
        target_style = CitationStyle[request.target_style]
        reformatted = citation_processor.reformat_citation(
            request.citation,
            source_style,
            target_style
        )
        return {"reformatted_citation": reformatted}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 