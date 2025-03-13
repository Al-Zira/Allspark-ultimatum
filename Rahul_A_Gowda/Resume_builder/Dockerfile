FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN printf 'GOOGLE_API_KEY=None\n' > .env

CMD ["python", "main.py"]

# docker build -t rahulagowda04/resume_builder .
# docker run -it -e GOOGLE_API_KEY=AIzaSyDoWshQ37GNlfgMLjKwJ40Yxpa8Ntbg8Y8 rahulagowda04/resume_builder