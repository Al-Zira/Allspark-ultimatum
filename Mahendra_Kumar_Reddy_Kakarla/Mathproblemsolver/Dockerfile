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

#docker run -it -e GOOGLE_API_KEY=your_api_key -v .:/app/images ai-math-problem-solver get_answer_from_image              
#docker run -it --rm -e GOOGLE_API_KEY=your_api_key ai-math-problem-solver --question="x^2+y^2+2xy=?  x=5" get_answer_for_text      

