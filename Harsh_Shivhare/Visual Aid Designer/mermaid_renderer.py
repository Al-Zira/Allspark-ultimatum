import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tempfile import NamedTemporaryFile
from pathlib import Path

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
        .mermaid {{ background: white; padding: 20px; display: inline-block; max-width: 4d00px; }}
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
        chrome_options.add_argument("--disable-gpu")
        return webdriver.Chrome(options=chrome_options)

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

            width = driver.execute_script("return document.querySelector('.mermaid').offsetWidth")
            height = driver.execute_script("return document.querySelector('.mermaid').offsetHeight")
            driver.set_window_size(width + 40, height + 200)

            driver.save_screenshot(output_path)
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

        finally:
            if driver:
                driver.quit()
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == "__main__":
    mermaid_code = """
    classDiagram
    class Bank {
        +String name
        +String address
        +List branches
        +addBranch(Branch branch)
        +removeBranch(Branch branch)
    }

    class Branch {
        +String branchId
        +String location
        +Bank bank
        +List employees
        +List accounts
        +addEmployee(Employee employee)
        +removeEmployee(Employee employee)
        +addAccount(Account account)
        +removeAccount(Account account)
    }

    class Employee {
        +String employeeId
        +String name
        +String position
        +Branch branch
        +assignToBranch(Branch branch)
    }

    class Customer {
        +String customerId
        +String name
        +String address
        +List accounts
        +addAccount(Account account)
        +removeAccount(Account account)
    }

    class Account {
        +String accountNumber
        +double balance
        +Customer owner
        +Transaction[] transactions
        +deposit(double amount)
        +withdraw(double amount)
    }

    class Transaction {
        +String transactionId
        +Date date
        +double amount
        +String type
        +Account account
    }
    
    class Loan {
        +String loanId
        +double amount
        +double interestRate
        +Branch branch
        +Customer borrower
    }

    Bank "1" o-- "many" Branch : has
    Branch "1" *-- "many" Account : contains
    Branch "1" o-- "many" Employee : employs
    Customer "1" *-- "many" Account : owns
    Account "1" -- "many" Transaction : contains
    Branch "1" *-- "many" Loan : processes
    Customer "1" *-- "many" Loan : borrows

    """

    renderer = MermaidRenderer()
    output_path = "mermaid_diagram.png"
    success = renderer.render_diagram(mermaid_code, output_path)

    if success:
        print(f"Diagram successfully generated at: {output_path}")
    else:
        print("Failed to generate diagram")
