# Research Topic Generator

## Overview
This project is an AI-powered Research Topic Generator that helps users generate short research topics, detailed descriptions, and relevant academic references. It supports multiple languages and ensures safety by detecting harmful content in generated references.

## Features
- Generate five unique research topics based on a keyword.
- Provide detailed descriptions for each topic.
- Fetch three academic references for each topic with clickable links.
- Multi-language support using the `translate` library.
- Detect harmful content in references.
- Stream results in a letter-by-letter format for a dynamic experience.

## Technologies Used
- Python
- Google Generative AI (`gemini-1.0-pro` model)
- `translate` library for language support
- `dotenv` for environment variable management
- `time` for streaming output

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/research-topic-generator.git
   cd research-topic-generator
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file with your Gemini API key:
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

## Usage
Run the script and follow the prompts:
```bash
python research_class.py
```
- Enter a keyword for generating research topics.
- Provide optional details for better results.
- Choose the output language from available options.

## Docker Deployment

### Prerequisites
Ensure you have Docker installed. If not, download and install it from [Docker's official website](https://www.docker.com/).

### Build the Docker Image
```bash
docker build -t research-topic-generator .
```

### Run the Container
```bash
docker run --rm -it --env GEMINI_API_KEY=your_api_key_here research-topic-generator
```
Alternatively, you can use a `.env` file:
```bash
docker run --rm -it --env-file .env research-topic-generator
```

### Stopping the Container
To stop the container, press `CTRL + C` or use:
```bash
docker ps  # Get the container ID
docker stop <container_id>
```

## License
This project is licensed under the MIT License.

## Author
[Your Name]

