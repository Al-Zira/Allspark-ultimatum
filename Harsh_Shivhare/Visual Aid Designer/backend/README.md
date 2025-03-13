# Visual Aid Designer Backend

A FastAPI-based service that generates visual diagrams using Mermaid.js. The service provides endpoints to generate various types of diagrams including flowcharts, sequence diagrams, class diagrams, and more.

## Prerequisites

- Docker installed on your system
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows/Mac
  - [Docker Engine](https://docs.docker.com/engine/install/) for Linux
- Port 8000 available on your machine

## Platform Compatibility

The containerized backend works on:

- macOS (both Intel and Apple Silicon)
- Linux (x86_64 and ARM64)
- Windows (via Docker Desktop with WSL2)

## Building and Running

### Build the Docker Image

```bash
# On all platforms
docker build -t visual-aid-backend .
```

### Run the Container

```bash
# On all platforms
docker run -p 8000:8000 -d visual-aid-backend
```

This will start the server on:

- Linux/macOS: `http://localhost:8000`
- Windows: `http://localhost:8000` or `http://host.docker.internal:8000`

### Platform-Specific Notes

#### Windows

- Ensure WSL2 is installed and enabled for Docker Desktop
- Use PowerShell or Command Prompt for the commands
- For stopping containers:

```powershell
docker ps -q -f ancestor=visual-aid-backend | ForEach-Object { docker stop $_ }
```

#### macOS

- Works on both Intel and Apple Silicon Macs
- Terminal commands work as shown in examples

#### Linux

- Might need to run Docker commands with `sudo` depending on your setup
- To avoid using sudo, add your user to the docker group:

```bash
sudo usermod -aG docker $USER
```

## API Endpoints

### 1. Get Available Diagram Types

**Endpoint:** `GET /diagram-types`

**Example:**

```bash
# Linux/macOS
curl http://localhost:8000/diagram-types

# Windows (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/diagram-types" -Method Get
```

**Response:**

```json
[
  "flowchart-diagram",
  "sequence-diagram",
  "class-diagram",
  "state-diagram",
  "entity-relationship-diagram",
  "gantt-diagram",
  "pie-chart",
  "quadrant-chart",
  "reqirement-diagram",
  "timeline-diagram",
  "git-diagram",
  "mind-map-diagram"
]
```

### 2. Generate Diagram

**Endpoint:** `POST /generate-diagram`

**Request Body:**

```json
{
  "prompt": "string",
  "diagram_type": "string"
}
```

**Example:**

```bash
# Linux/macOS
curl -X POST http://localhost:8000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple flowchart showing login process",
    "diagram_type": "flowchart-diagram"
  }'

# Windows (PowerShell)
$body = @{
    prompt = "Create a simple flowchart showing login process"
    diagram_type = "flowchart-diagram"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/generate-diagram" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

**Response:**

```json
{
  "mermaid_code": "string",
  "image_path": "string",
  "preview": "string"
}
```

## Example Usage

1. Generate a flowchart:

```bash
curl -X POST http://localhost:8000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a simple flowchart showing login process",
    "diagram_type": "flowchart-diagram"
  }'
```

2. Generate a sequence diagram:

```bash
curl -X POST http://localhost:8000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a sequence diagram for user registration",
    "diagram_type": "sequence-diagram"
  }'
```

## Troubleshooting

1. If the container fails to start, check if port 8000 is already in use:

```bash
# Linux/macOS
lsof -i :8000

# Windows (PowerShell)
netstat -ano | findstr :8000
```

2. To view container logs:

```bash
# Linux/macOS
docker logs $(docker ps -q -f ancestor=visual-aid-backend)

# Windows (PowerShell)
docker ps -q -f ancestor=visual-aid-backend | ForEach-Object { docker logs $_ }
```

3. To stop the container:

```bash
# Linux/macOS
docker stop $(docker ps -q -f ancestor=visual-aid-backend)

# Windows (PowerShell)
docker ps -q -f ancestor=visual-aid-backend | ForEach-Object { docker stop $_ }
```

4. Common Issues:

- **Windows**: If you can't connect to the server, try using `host.docker.internal` instead of `localhost`
- **Linux**: If you get permission errors, make sure your user is in the docker group
- **macOS**: On Apple Silicon Macs, the first build might take longer due to platform emulation

## Development

The backend uses:

- FastAPI for the web framework
- Selenium with Chromium for rendering Mermaid diagrams
- Pillow for image processing

For local development without Docker:

- **Linux**: Install chromium-browser and chromium-driver
- **macOS**: Install Chrome/Chromium via Homebrew: `brew install --cask chromium`
- **Windows**: Install Chrome and ChromeDriver manually


