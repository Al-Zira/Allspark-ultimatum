FROM python:3.11-slim

# Install system dependencies and Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pillow

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/bin/chromium
ENV CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage"
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Create a non-root user and set up permissions
RUN useradd -m myuser \
    && chown -R myuser:myuser /app \
    && mkdir -p /home/myuser/.wdm/drivers \
    && chown -R myuser:myuser /home/myuser/.wdm

USER myuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 