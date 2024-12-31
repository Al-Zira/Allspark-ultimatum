# Use the official Python image as the base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and the script into the container
COPY requirements.txt ./
COPY product_description.py ./
COPY .dockerignore ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file into the container
COPY .env .env

# Expose the port if needed (optional, depends on whether it's a web service)
EXPOSE 8000

# Command to run your script
CMD ["python", "product_description.py"]