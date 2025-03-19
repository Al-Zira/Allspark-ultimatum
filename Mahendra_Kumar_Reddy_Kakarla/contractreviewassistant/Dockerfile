FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /contracts
# Copy the entire application
COPY . .

# Define entrypoint for running the script with arguments
ENTRYPOINT ["python", "main.py"]

#docker run -it -e GOOGLE_API_KEY=AIzaSyDB1dmte18jUEJDnF_wqUy9Yze5_2iLz7Q -v .:/app/contracts ai-contract-assistant
