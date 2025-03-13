FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create data directory for CSV files
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY __init__.py .
COPY data_analyzer.py .
COPY main.py .

# Set the data directory as a volume
VOLUME /app/data

RUN printf 'GOOGLE_API_KEY=None\CSV_PATH=None\n' > .env

CMD ["python", "main.py"]

# Build Command:
# -----------------------------
# docker build -t rahulagowda04/data_report_generator .
#
# Run Command:
# -----------------------------
# For Windows PowerShell:
# docker run -it -v "${PWD}/data:/app/data" -e GOOGLE_API_KEY=AIzaSyDoWshQ37GNlfgMLjKwJ40Yxpa8Ntbg8Y8 -e CSV_PATH="/app/data/carbo.csv" rahulagowda04/data_report_generator