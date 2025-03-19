FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .



# Define entrypoint for running the script with arguments
ENTRYPOINT ["python", "main.py"]
#docker run -it -e GOOGLE_API_KEY=your_api_key ai-allergy-substitute-finder --allergy_items "nuts,sunflowerseeds" --situation "food"   
                   

