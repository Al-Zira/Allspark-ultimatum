FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /images
# Copy the entire application
COPY . .

# Set environment variables for API key


# Define entrypoint for running the script with arguments
ENTRYPOINT ["python", "main.py"]

#docker run -it -e GOOGLE_API_KEY=your_api_key ai-study-assistant text_summary --input "Your text here." --prompt "Summarize this text concisely." 
#docker run -it -e GOOGLE_API_KEY=your_api_key -v .:/app/images ai-study-assistant image_summary --prompt "Describe the images in detail."
#docker run -it -e GOOGLE_API_KEY=your_api_key ai-study-assistant generate_test_and_evaluate --input "Artificial Intelligence and its applications in healthcare."
#docker run -it -e GOOGLE_API_KEY=your_api_keyai-study-assistant find_resources --input "AI Agents"                    

