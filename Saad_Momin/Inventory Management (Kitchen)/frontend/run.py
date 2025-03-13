import streamlit.web.cli as stcli
import sys
import os

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", "app/main.py"]
    sys.exit(stcli.main()) 