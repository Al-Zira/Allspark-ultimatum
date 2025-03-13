FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Create directories
RUN mkdir -p /app/saved_model /app/documents

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the saved model files first
COPY saved_model /app/saved_model/

# Copy application files
COPY main.py .

# Set the documents directory as a volume
VOLUME /app/documents

# Run the application
CMD ["python", "main.py"]

# Build Command:
# -----------------------------
# docker build -t rahulagowda04/medical_report_summarizer .
#
# Run Commands:
# -----------------------------
# For Windows PowerShell:
#docker run -it -v "${PWD}/documents:/app/documents" -e GOOGLE_API_KEY="AIzaSyDoWshQ37GNlfgMLjKwJ40Yxpa8Ntbg8Y8" -e FILE_PATH="/app/documents/report.pdf" rahulagowda04/medical_report_summarizer:v2