# Use Python 3.9 Slim
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire "app" folder into the container's "/app"
COPY app /app

# Install dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt

# Create a non-root user and set permissions
RUN adduser --uid 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Run the application
CMD ["python", "/app/nutrition_class.py"]
