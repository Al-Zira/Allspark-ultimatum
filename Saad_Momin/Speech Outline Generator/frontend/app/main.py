import streamlit as st
import requests
import base64

# API endpoint
API_URL = "http://localhost:8080"  # FastAPI backend URL

def get_download_link(content, filename):
    """Generate a download link for the text file"""
    text_bytes = content.encode('utf-8')
    b64 = base64.b64encode(text_bytes).decode()
    return f'<a href="data:text/plain;charset=utf-8;base64,{b64}" download="{filename}">Download Text File</a>'

def main():
    st.set_page_config(page_title="AI Speech Outline Generator", page_icon="🎤", layout="wide")
    
    st.title("🎤 AI Speech Outline Generator")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Basic Parameters
        topic = st.text_input("What is the topic of your speech?", 
                            placeholder="Enter your speech topic")
        
        topic_details = st.text_area("Additional Topic Details (Optional)", 
                                    placeholder="Enter any specific details, context, or focus areas for your topic")
        
        language = st.selectbox("Select Language", 
                                ["English", "Spanish", "French", "German", "Mandarin", 
                                 "Japanese", "Korean", "Italian", "Portuguese", "Russian",
                                 "Arabic", "Hindi", "Turkish"])
        
        tone = st.selectbox("Select Tone", 
                            ["Formal", "Conversational", "Inspirational", 
                             "Academic", "Persuasive", "Technical", "Humorous",
                             "Professional", "Motivational"])
    
    with col2:
        # Enhanced Parameters
        duration = st.slider("Speech Duration (minutes)", 
                           min_value=5, max_value=60, value=15, step=5)
        
        audience_type = st.selectbox("Target Audience",
                                   ["General Public", "Professional", "Academic",
                                    "Technical", "Students", "Executives",
                                    "Mixed Audience", "Industry Specific"])
        
        presentation_style = st.selectbox("Presentation Style",
                                        ["Traditional", "Interactive",
                                         "Story-based", "Data-driven",
                                         "Workshop Style", "Q&A Format"])
        
        purpose = st.selectbox("Speech Purpose",
                             ["Inform", "Persuade", "Motivate",
                              "Educate", "Entertain", "Call to Action"])
    
    # Advanced Options Expander
    with st.expander("Advanced Options"):
        col3, col4 = st.columns(2)
        
        with col3:
            sections = st.slider("Number of Sections", 
                               min_value=3, max_value=10, value=5)
            
            template = st.selectbox("Template Style",
                                  ["Standard", "Problem-Solution",
                                   "Chronological", "Compare-Contrast",
                                   "Cause-Effect", "Process Analysis"])
        
        with col4:
            word_limit = st.select_slider("Word Limit",
                                        options=[500, 750, 1000, 1500, 2000, 2500, 3000],
                                        value=1500)
            
            formatting_style = st.selectbox("Formatting Style",
                                          ["Standard", "Bullet Points",
                                           "Numbered Lists", "Hierarchical",
                                           "Mind Map Style"])
    
    # Generate Button
    if st.button("Generate Outline", type="primary"):
        if topic:
            with st.spinner("Generating your speech outline..."):
                try:
                    # Prepare the request payload
                    payload = {
                        "topic": topic,
                        "language": language,
                        "tone": tone,
                        "sections": sections,
                        "duration": duration,
                        "audience_type": audience_type,
                        "presentation_style": presentation_style,
                        "purpose": purpose,
                        "template": template,
                        "word_limit": word_limit,
                        "formatting_style": formatting_style,
                        "topic_details": topic_details
                    }
                    
                    # Make API request
                    response = requests.post(f"{API_URL}/generate-outline", json=payload)
                    response.raise_for_status()  # Raise exception for bad status codes
                    
                    data = response.json()
                    outline = data["outline"]
                    
                    st.write("### 📝 Generated Speech Outline")
                    st.markdown(outline)
                    
                    # Create download options
                    st.markdown("### 📥 Download Options")
                    filename = f"speech_outline_{topic.lower().replace(' ', '_')}.txt"
                    st.markdown(get_download_link(outline, filename), unsafe_allow_html=True)
                    
                    # Display speech statistics
                    st.markdown("### 📊 Speech Statistics")
                    st.info(f"""
                    - Estimated Word Count: {data['word_count']}
                    - Estimated Speaking Time: {data['duration']} minutes
                    - Number of Sections: {data['sections']}
                    """)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the backend service: {str(e)}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a topic for your speech.")

if __name__ == "__main__":
    main() 