# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (ffmpeg is needed for audio processing)
RUN apt-get update && apt-get install -y ffmpeg

# Copy application code
COPY . /app

# Copy the locally saved Whisper model
COPY local_model /app/local_model

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the necessary directories exist
RUN mkdir -p /app/videos /app/audios && chown -R 1000:1000 /app/videos /app/audios

# Switch to a non-root user for security
RUN useradd -u 1000 -m appuser
USER appuser

# Set the entry point
CMD ["python", "main.py"]
# docker -run -it --rm -e GOOGLE_API_KEY=your_api_key -v $(pwd)/videos:/app/videos ai-video-summarizer
# docker -run -it --rm -e GOOGLE_API_KEY=your_api_key --youtube_link "your_youtube_link" ai-video-summarizer