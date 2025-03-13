FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create documents directory for PDF files
RUN mkdir -p /app/documents

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .

# Set the documents directory as a volume
VOLUME /app/documents

CMD ["python", "main.py"]

# Build Command:
# -----------------------------
# docker build -t rahulagowda04/text_summarizer .
#
# Run Command:
# -----------------------------
# For Windows PowerShell:
# docker run -it -v "${PWD}/documents:/app/documents" -e GOOGLE_API_KEY="AIzaSyDoWshQ37GNlfgMLjKwJ40Yxpa8Ntbg8Y8" -e FILE_PATH="/app/documents/deepseek.pdf" rahulagowda04/text_summarizer