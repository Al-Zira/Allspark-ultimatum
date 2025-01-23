import streamlit as st
import requests
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LegalCitationApp:
    def __init__(self):
        """Initialize the Streamlit Legal Citation Application"""
        # Configure Streamlit page
        st.set_page_config(
            page_title="LegalCite: AI Citation Assistant",
            page_icon="⚖️",
            layout="wide"
        )
        
        # API Configuration
        self.api_base_url = os.getenv('API_URL', 'http://localhost:8000')
        
        # Cache citation styles and jurisdictions
        self.style_options = self._fetch_citation_styles()
        self.jurisdiction_options = self._fetch_jurisdictions()
        
        # Citation style to jurisdiction mapping
        self.style_jurisdiction_map = {
            'BLUEBOOK_US': ['US_FEDERAL', 'US_STATE', 'US_SUPREME_COURT', 'US_FEDERAL_CIRCUIT', 
                           'US_DISTRICT_COURT', 'US_STATE_SUPREME', 'US_STATE_APPELLATE', 'US_BANKRUPTCY'],
            'ALWD': ['US_FEDERAL', 'US_STATE'],
            'CHICAGO_MANUAL_LEGAL': ['US_FEDERAL', 'US_STATE'],
            'OSCOLA': ['UK_SUPREME_COURT', 'UK_HIGH_COURT', 'UK_COURT_OF_APPEAL', 'UK_CROWN_COURT'],
            'CANADIAN_GUIDE': ['UK_SUPREME_COURT'],
            'INDIAN_LEGAL': ['INDIAN_SUPREME', 'INDIAN_HIGH_COURT', 'INDIAN_DISTRICT_COURT', 'INDIAN_STATE'],
            'INDIAN_LAW_COMMISSION': ['INDIAN_SUPREME', 'INDIAN_HIGH_COURT', 'INDIAN_STATE'],
            'ECHR': ['EUROPEAN_COURT_HUMAN_RIGHTS'],
            'ECJ': ['EU_COURT_OF_JUSTICE', 'EU_GENERAL_COURT'],
            'INTERNATIONAL_COURT_JUSTICE': ['INTERNATIONAL_COURT_JUSTICE'],
            'INTERNATIONAL_CRIMINAL_COURT': ['INTERNATIONAL_CRIMINAL_COURT'],
            'UNCITRAL': ['PERMANENT_COURT_ARBITRATION'],
            'AGLC': ['AU_HIGH_COURT', 'AU_FEDERAL_COURT', 'AU_FAMILY_COURT', 'AU_STATE_SUPREME', 
                     'AU_DISTRICT_COURT', 'AU_MAGISTRATES', 'AU_TRIBUNALS', 'AU_STATE'],
            'AUSTLII': ['AU_HIGH_COURT', 'AU_FEDERAL_COURT', 'AU_STATE'],
            'QUEENSLAND_STYLE': ['AU_HIGH_COURT', 'AU_FEDERAL_COURT', 'AU_STATE'],
            'FEDERAL_COURT_AU': ['AU_HIGH_COURT', 'AU_FEDERAL_COURT'],
            'HIGH_COURT_AU': ['AU_HIGH_COURT']
        }

    def _fetch_citation_styles(self) -> Dict[str, str]:
        """Fetch available citation styles from API"""
        try:
            response = requests.get(f"{self.api_base_url}/styles")
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch citation styles: {str(e)}")
            return {}

    def _fetch_jurisdictions(self) -> Dict[str, str]:
        """Fetch available jurisdictions from API"""
        try:
            response = requests.get(f"{self.api_base_url}/jurisdictions")
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch jurisdictions: {str(e)}")
            return {}

    def _get_filtered_jurisdictions(self, style_name: str) -> Dict[str, str]:
        """Get jurisdictions relevant to the selected citation style"""
        if not style_name:
            return self.jurisdiction_options
            
        allowed_jurisdictions = self.style_jurisdiction_map.get(style_name, [])
        return {k: v for k, v in self.jurisdiction_options.items() 
                if any(allowed_j in k for allowed_j in allowed_jurisdictions)}

    def render_page(self):
        """Main Streamlit page rendering method"""
        # Page Title and Introduction
        st.title("🏛️ LegalCite: AI-Powered Citation Assistant")
        st.markdown("""
        An intelligent tool for validating, reformatting, and analyzing 
        legal citations across major legal systems.
        """)
        
        # Sidebar Configuration
        self._render_sidebar()
        
        # Main Content Tabs
        tab1, tab2 = st.tabs([
            "Citation Validation", 
            "Citation Reformatting"
        ])
        
        with tab1:
            self._render_validation_tab()
        
        with tab2:
            self._render_reformatting_tab()

    def _render_sidebar(self):
        """Render configuration sidebar with dynamic jurisdiction filtering"""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # Citation Style Selection
            self.selected_style = st.selectbox(
                "Preferred Citation Style", 
                list(self.style_options.keys())
            )
            
            # Get filtered jurisdictions based on selected style
            filtered_jurisdictions = self._get_filtered_jurisdictions(self.selected_style)
            
            # Jurisdiction Selection with filtered options
            jurisdiction_options = list(filtered_jurisdictions.keys())
            self.selected_jurisdiction = st.selectbox(
                "Jurisdiction",
                jurisdiction_options,
                index=0 if jurisdiction_options else None
            )
            
            # Additional Sidebar Information
            st.info("""
            💡 Pro Tips:
            - Use full, precise citations
            - Check formatting carefully
            - Different jurisdictions have unique rules
            """)

    def _render_validation_tab(self):
        """Render the citation validation interface"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Input Citation")
            input_citation = st.text_area(
                "Paste your legal citation", 
                height=200,
                placeholder="Example (US): Marbury v. Madison, 5 U.S. (1 Cranch) 137 (1803)"
            )
        
        with col2:
            st.subheader("🔍 Citation Analysis")
            if st.button("Analyze Citation"):
                if input_citation:
                    try:
                        # Call validation API
                        response = requests.post(
                            f"{self.api_base_url}/validate",
                            json={
                                "citation": input_citation,
                                "style": self.selected_style,
                                "jurisdiction": self.selected_jurisdiction
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Display Validation Results
                            st.write("### Validation Results")
                            
                            # Validity Indicator
                            if result.get("is_valid"):
                                st.success("✅ Citation is Valid")
                            else:
                                st.error("❌ Citation has issues")
                            
                            # Display detailed results
                            st.json(result)
                            
                            # Get hyperlink if citation is valid
                            if result.get("is_valid"):
                                hyperlink_response = requests.post(
                                    f"{self.api_base_url}/hyperlink",
                                    json={
                                        "citation": input_citation,
                                        "style": self.selected_style,
                                        "jurisdiction": self.selected_jurisdiction
                                    }
                                )
                                
                                if hyperlink_response.status_code == 200:
                                    hyperlink_data = hyperlink_response.json()
                                    
                                    if hyperlink_data.get("primary_link"):
                                        st.markdown("### 🔗 Available Links")
                                        
                                        # Primary Link
                                        st.markdown("#### Primary Source:")
                                        st.markdown(f"[Access Full Text]({hyperlink_data['primary_link']})")
                                        
                                        # Alternate Links
                                        if hyperlink_data.get("alternate_links"):
                                            st.markdown("#### Alternative Sources:")
                                            for idx, link in enumerate(hyperlink_data["alternate_links"], 1):
                                                st.markdown(f"{idx}. [Alternative Source {idx}]({link})")
                                    else:
                                        st.warning("No direct links found for this citation.")
                        else:
                            st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Error processing citation: {str(e)}")

    def _render_reformatting_tab(self):
        """Render the citation reformatting interface"""
        st.subheader("🔄 Citation Reformatting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source_style = st.selectbox(
                "Source Citation Style", 
                list(self.style_options.keys())
            )
        
        with col2:
            target_style = st.selectbox(
                "Target Citation Style", 
                list(self.style_options.keys())
            )
        
        input_citation = st.text_area(
            "Citation to Reformat",
            placeholder="Enter full legal citation here"
        )
        
        if st.button("Reformat Citation"):
            try:
                response = requests.post(
                    f"{self.api_base_url}/reformat",
                    json={
                        "citation": input_citation,
                        "source_style": source_style,
                        "target_style": target_style
                    }
                )
                
                if response.status_code == 200:
                    reformatted = response.json()["reformatted_citation"]
                    st.success("Reformatted Citation:")
                    st.code(reformatted)
                else:
                    st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Reformatting error: {str(e)}")

def main():
    """Main application entry point"""
    app = LegalCitationApp()
    app.render_page()

if __name__ == "__main__":
    main() 