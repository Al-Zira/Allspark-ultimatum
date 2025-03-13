FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY init_db.py .

# Run the application
CMD ["python", "main.py"]

# Build Command:
# -----------------------------
# docker build -t rahulagowda04/personal_medical_assistant .
#
# Run Command:
# -----------------------------
# For Windows PowerShell:
#docker run -it -e NEO4J_URI="neo4j+s://49d065ce.databases.neo4j.io" -e NEO4J_USERNAME="neo4j" -e NEO4J_PASSWORD="ggMNF_WiDovTk3yvPpaKIyn5No03udCCbqhRDSP7MYw" -e GOOGLE_API_KEY="AIzaSyDoWshQ37GNlfgMLjKwJ40Yxpa8Ntbg8Y8" rahulagowda04/personal_medical_assistant