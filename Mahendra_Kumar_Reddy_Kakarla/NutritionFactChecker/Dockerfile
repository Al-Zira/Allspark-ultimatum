FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /images
# Copy the entire application
COPY . .



# Define entrypoint for running the script with arguments
ENTRYPOINT ["python", "main.py"]
#docker run -it --rm -e GOOGLE_API_KEY=your_api_key  -v .:/app/images ai-nutrition-fact-checker get_nf_from_image      
#docker run -it --rm -e GOOGLE_API_KEY=your_api_key  ai-nutrition-fact-checker get_nf_from_product_info --product_Name "Oats" --company_name "Quaker" --description "Whole grain oats with no added sugar"                   

