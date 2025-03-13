# DIY Project Planner

## Overview
The DIY Project Planner is a terminal-based application that helps users generate personalized DIY project plans based on their skill level, budget, and interests. The project utilizes the **Gemini AI API** to suggest project ideas and provides a system to save, view, and download project details.

## Features
- Generate DIY project ideas based on skill level, budget, and interests.
- Convert currency between **USD and INR**.
- Save generated project plans.
- View a list of saved projects.
- Display project details for review.
- Download project details as a text file.
- Interactive terminal-based interface.

## Tech Stack
- **Python 3.9**
- **Google Gemini AI API**
- **Docker** (for containerization)
- **dotenv** (for environment variables management)

## Installation
### Prerequisites
- **Python 3.9+** installed on your machine
- **Docker** installed (optional for containerized deployment)

### Clone the Repository
```sh
git clone https://github.com/your-repo/diy-project-planner.git
cd diy-project-planner
```

### Setup Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Set Up API Key
Create a `.env` file in the project root and add:
```sh
GEMINI_API_KEY=your_api_key_here
```

## Usage
Run the application with:
```sh
python app/main.py
```
Follow the on-screen prompts to interact with the DIY Project Planner.

## Docker Setup
### Build and Run the Docker Container
```sh
docker build -t diy-project-planner .
docker run -it --rm -v "$(pwd)/uploads:/app/uploads" diy-project-planner
```

## Environment Variables
| Variable          | Description                   |
|------------------|------------------------------|
| GEMINI_API_KEY   | API key for Google Gemini AI |

## Project Structure
```
📂 diy-project-planner
│-- 📂 app
│   │-- main.py
│   │-- requirements.txt
│   │-- .env (not included in repo)
│-- Dockerfile
│-- README.md
```



