FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create credentials directory
RUN mkdir -p /app/credentials

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .

# Set the credentials directory as a volume
VOLUME /app/credentials

CMD ["python", "main.py"]

# Build Command:
# -----------------------------
# docker build -t rahulagowda04/email_writer .
#
# Run Command:
# -----------------------------
# For Windows PowerShell:
#docker run -it -v "${PWD}/credentials:/app/credentials" -e GOOGLE_API_KEY="AIzaSyDoWshQ37GNlfgMLjKwJ40Yxpa8Ntbg8Y8" -e TOKEN="/app/credentials/token.json" -e CLIENT_SECRET_FILE_PATH="/app/credentials/credentials.json" rahulagowda04/email_writer