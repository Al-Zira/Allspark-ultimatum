from setuptools import setup, find_packages

setup(
    name="kitchen-inventory-frontend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.24.0",
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0"
    ],
) 