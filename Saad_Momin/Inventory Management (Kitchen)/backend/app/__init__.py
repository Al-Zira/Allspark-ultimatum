from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) 