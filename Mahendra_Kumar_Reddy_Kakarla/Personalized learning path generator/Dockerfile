# Use an official Python runtime as a parent image
FROM python:3.12-slim
# Set the working directory in the container
WORKDIR /app
# Copy the entire project first (including requirements.txt)
COPY . .
# Install dependencies from requirements.txt
COPY requirements.txt .
RUN python -m pip install -r requirements.txt  



# Define the command to run the script
ENTRYPOINT ["python", "main.py"]
#docker run -it --rm -e GOOGLE_API_KEY=your_api_key ai-personalized-learning-path --skill_set"skills" --interests "interests" --goals "goal"