from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tempfile import NamedTemporaryFile
from PIL import Image
import os
import time

class MermaidRenderer:
    def get_html_template(self, mermaid_code):
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@9.3.0/dist/mermaid.min.js"></script>
    <script>
        window.onload = function() {{
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                themeVariables: {{
                    primaryColor: '#ffffff',
                    primaryTextColor: '#000000',
                    primaryBorderColor: '#000000',
                    lineColor: '#000000',
                    secondaryColor: '#e0e0e0',
                    tertiaryColor: '#f5f5f5'
                }},
                flowchart: {{ 
                    curve: 'basis',
                    padding: 20,
                    htmlLabels: true
                }},
                sequence: {{ 
                    useMaxWidth: false,
                    width: 1200,
                    height: 800
                }}
            }});
        }}
    </script>
    <style>
        body {{ 
            margin: 0; 
            padding: 20px; 
            background: white; 
        }}
        #diagram {{
            background: white;
            padding: 20px;
            min-width: 800px;
            max-width: 4000px;
        }}
    </style>
</head>
<body>
    <div id="diagram">
        <pre class="mermaid">
{mermaid_code}
        </pre>
    </div>
</body>
</html>"""

    def setup_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use system-installed ChromeDriver
        service = Service('/usr/bin/chromedriver')
        return webdriver.Chrome(service=service, options=chrome_options)

    def render_diagram(self, mermaid_code, output_path):
        driver = None
        temp_file_path = None

        try:
            # Clean up the mermaid code
            mermaid_code = mermaid_code.strip()
            
            # Create HTML file with the template
            html_content = self.get_html_template(mermaid_code)
            
            with NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name

            # Setup and start Chrome
            driver = self.setup_chrome_driver()
            driver.get(f"file://{temp_file_path}")

            # Wait for rendering
            time.sleep(2)  # Give time for JavaScript to execute
            
            try:
                # Wait for SVG to be present
                wait = WebDriverWait(driver, 10)
                svg = wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))
                
                if not svg:
                    raise Exception("No SVG element found - diagram may have failed to render")

                # Get dimensions
                width = max(svg.size['width'], 800)
                height = max(svg.size['height'], 400)

                # Set window size to match content
                driver.set_window_size(width + 100, height + 100)
                
                # Take screenshot
                driver.save_screenshot(output_path)

                # Process the image
                img = Image.open(output_path)
                img = img.crop((20, 20, width + 60, height + 60))  # Crop with padding
                img.save(output_path, quality=95, optimize=True)

                return True
            
            except Exception as e:
                print(f"SVG Error: {str(e)}")
                # Take a screenshot of the error state for debugging
                driver.save_screenshot(output_path)
                return False

        except Exception as e:
            print(f"Rendering Error: {str(e)}")
            return False

        finally:
            if driver:
                driver.quit()
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)