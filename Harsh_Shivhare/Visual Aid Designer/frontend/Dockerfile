# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set up working directory
WORKDIR /app

# Install Gradio and requests
RUN pip install --no-cache-dir gradio==3.50.2 requests

# Copy the application
COPY . .

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
CMD ["python", "gradio_app.py"] 