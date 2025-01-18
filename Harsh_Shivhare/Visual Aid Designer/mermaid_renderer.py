from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tempfile import NamedTemporaryFile
from PIL import Image
import os

class MermaidRenderer:
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            mermaid.initialize({{
                startOnLoad: true,
                theme: "default",
                themeVariables: {{
                    primaryColor: "#ffffff",
                    primaryTextColor: "#000000",
                    primaryBorderColor: "#000000",
                    lineColor: "#000000",
                    secondaryColor: "#e0e0e0",
                    tertiaryColor: "#f5f5f5",
                    noteBkgColor: "#ffffff",
                    noteTextColor: "#000000"
                }},
                flowchart: {{ curve: "basis", padding: 20 }}
            }});
        }});
    </script>
    <style>
        body {{ margin: 0; padding: 0; background: white; }}
        .mermaid {{ background: white; padding: 20px; display: inline-block; max-width: 4000px; }}
    </style>
</head>
<body>
    <div class="mermaid">
        {code}
    </div>
</body>
</html>
"""

    def setup_chrome_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--force-device-scale-factor=2")
        chrome_options.add_argument("--disable-gpu")
        return webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)

    def render_diagram(self, mermaid_code, output_path):
        driver = None
        temp_file_path = None

        try:
            with NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
                temp_file.write(self.HTML_TEMPLATE.format(code=mermaid_code))
                temp_file_path = temp_file.name

            driver = self.setup_chrome_driver()
            driver.get(f"file://{temp_file_path}")

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mermaid")))

            # Get the size of the mermaid div
            diagram_element = driver.find_element(By.CLASS_NAME, "mermaid")
            width = diagram_element.size['width']
            height = diagram_element.size['height']

            # Set window size to double the size for high resolution
            driver.set_window_size(width * 2, height * 2)

            # Take screenshot
            driver.save_screenshot(output_path)

            # Resize the image to original size using Pillow
            img = Image.open(output_path)
            img = img.resize((width, height), Image.LANCZOS)
            img.save(output_path)

            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

        finally:
            if driver:
                driver.quit()
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)