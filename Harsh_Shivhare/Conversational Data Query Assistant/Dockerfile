# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Create the local model directory and set permissions
RUN mkdir -p /local_model && chown -R 1000:1000 /local_model

# Download the model during the build process and save it locally
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
model.save('/local_model')"

# Set environment variable to the local model path
ENV TRANSFORMERS_CACHE=/local_model

# Switch to a non-root user
RUN useradd -u 1000 -m appuser
USER appuser

# Set the entry point
CMD ["python", "main.py"]
