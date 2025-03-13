import requests
import base64

def get_download_link(content, filename):
    """Generate a download link for the text file"""
    text_bytes = content.encode('utf-8')
    b64 = base64.b64encode(text_bytes).decode()
    return f'<a href="data:text/plain;charset=utf-8;base64,{b64}" download="{filename}">Download Text File</a>'

# First, let's get the outline from the API
response = requests.post(
    "http://localhost:8000/generate-outline",
    json={
        "topic": "Test Download",
        "language": "English",
        "tone": "Professional",
        "sections": 3,
        "duration": 10,
        "audience_type": "General Public",
        "presentation_style": "Traditional",
        "purpose": "Inform",
        "template": "Standard",
        "word_limit": 500,
        "formatting_style": "Bullet Points",
        "topic_details": "Testing download functionality"
    }
)

if response.status_code == 200:
    data = response.json()
    outline = data["outline"]
    
    # Generate download link
    filename = "test_outline.txt"
    download_link = get_download_link(outline, filename)
    
    # Save the outline to a file directly
    with open(filename, "w", encoding="utf-8") as f:
        f.write(outline)
    
    print(f"1. API Response received successfully")
    print(f"2. Word count: {data['word_count']}")
    print(f"3. File saved as: {filename}")
    print(f"4. Download link generated: {len(download_link)} characters")
else:
    print(f"Error: {response.status_code}")
    print(response.text) 