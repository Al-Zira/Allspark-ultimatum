# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_API_KEY=""

# Set the working directory in the container
WORKDIR /app

# Copy application code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port (if the app is intended to be accessed via HTTP)
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]