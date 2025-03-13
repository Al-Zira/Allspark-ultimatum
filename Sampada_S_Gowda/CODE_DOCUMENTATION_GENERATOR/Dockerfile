# Use Python 3.9 Slim image
FROM python:3.9-slim

# Set environment variables to improve Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements.txt file initially
COPY app/requirements.txt /app/

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the entire 'app' directory into the container
COPY app /app/

# Create a non-root user and grant ownership of the /app directory
RUN adduser --uid 5678 --disabled-password --gecos "" appuser && chown -R appuser /app

# Set the default user to the non-root user
USER appuser

# Ensure the upload directory exists and is writable by the app user
RUN mkdir -p /app/uploads && chown -R appuser /app/uploads

# Set the directory for file uploads in your application
ENV UPLOAD_FOLDER=/app/uploads

# Specify the default command to run your application
CMD ["python", "/app/code_class.py"]
