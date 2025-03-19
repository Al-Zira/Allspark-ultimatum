    # Use an official Python runtime as a parent image
    FROM python:3.12-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the entire project first (including requirements.txt)
    COPY . .

    # Install dependencies from requirements.txt
    COPY requirements.txt .
    RUN python -m pip install -r requirements.txt  

    # Ensure the /contracts folder exists (useful for mounting)
    RUN mkdir -p /contracts


    # Define the command to run the script
    ENTRYPOINT ["python", "main.py"]

    #docker run -it --rm -e GOOGLE_API_KEY=your_api_key -v "%CD%\AI-zira Contract.pdf:/contracts/AI-zira Contract.pdf" ai_contract_reviewer "AI-zira Contract.pdf" 
