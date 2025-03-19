# Use an official Python runtime as a parent image
FROM python:3.12-slim
# Set the working directory in the container
WORKDIR /app
# Copy the entire project first (including requirements.txt)
COPY . .
# Install dependencies from requirements.txt
COPY requirements.txt .
RUN python -m pip install -r requirements.txt  


# Set environment variables (optional but useful)
ENV CONFIG_PATH=/app/credentials.yaml
# Define the command to run the script
ENTRYPOINT ["python", "main.py"]

#docker run -it --rm -e GOOGLE_API_KEY=your_api_key ai-stress-relief-system --task suggest_music --mood "mood"
#docker run -it --rm -e GOOGLE_API_KEY=your_api_key ai-stress-relief-system --task get_jokes --mood "mood"
#docker run -it --rm -e GOOGLE_API_KEY=your_api_key ai-stress-relief-system --task get_medications_and_relief_methods --mood "mood"