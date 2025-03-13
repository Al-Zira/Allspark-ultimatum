# Redaction API Documentation

A powerful API for detecting and redacting sensitive information from documents. Supports PDF, DOCX, and TXT files.

## Features

- 📄 Multi-format document support (PDF, DOCX, TXT)
- 🔍 Intelligent PII detection
- 🤖 AI-powered context analysis
- ⚡ Async processing for large files
- 🔒 Secure file handling
- 🚀 Rate limiting and optimization

## API Endpoints

### Health Check Endpoints

#### GET /

Check if the API is running.

```bash
curl http://localhost:8000/
```

Response:

```json
{
  "message": "API is running"
}
```

#### GET /test

Test the API functionality.

```bash
curl http://localhost:8000/test
```

Response:

```json
{
  "message": "API is working"
}
```

### Document Processing Endpoints

#### POST /upload

Upload a document for processing.

```bash
curl -X POST -F "file=@path/to/your/document.pdf" http://localhost:8000/upload
```

Response:

```json
{
  "message": "Successfully received file: document.pdf",
  "size": 1234,
  "file_path": "/tmp/upload_hash_document.pdf",
  "text": "Extracted text content..."
}
```

Supported file types:

- PDF (.pdf)
- Microsoft Word (.docx)
- Text files (.txt)

File size limit: 50MB

#### POST /ai-suggestions

Get AI-powered suggestions for potential sensitive information in a document.

```bash
curl -X POST "http://localhost:8000/ai-suggestions?file_path=/tmp/upload_hash_document.pdf"
```

Response:

```json
{
  "suggestions": [
    {
      "text": "detected text",
      "type": "PII",
      "confidence": 0.95,
      "reason": "Contains EMAIL/PHONE/SSN/etc"
    }
  ]
}
```

#### POST /apply-redactions

Apply redactions to a document.

```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "redactions": [
        {
            "text": "text to redact",
            "type": "PII",
            "confidence": 0.95,
            "reason": "Contains sensitive info"
        }
    ],
    "file_path": "/tmp/upload_hash_document.pdf"
}' http://localhost:8000/apply-redactions
```

Response:

```json
{
    "redacted_file_path": "/tmp/redacted_hash_document.pdf",
    "report": {
        "original_file": "/tmp/upload_hash_document.pdf",
        "redacted_file": "/tmp/redacted_hash_document.pdf",
        "num_redactions": 1,
        "redactions": [...]
    }
}
```

#### POST /analyze-context

Analyze text for contextual sensitive information.

```bash
curl -X POST "http://localhost:8000/analyze-context?document_text=text to analyze&text=pattern to find&type=PII"
```

Response:

```json
{
  "matches": [
    {
      "text": "matched text",
      "type": "PII",
      "confidence": 95.0,
      "reason": "Explanation of match",
      "context": "... text surrounding the match ..."
    }
  ]
}
```

## Rate Limiting

- Maximum 120 requests per minute per IP address
- Requests exceeding this limit will receive a 429 (Too Many Requests) response

## Error Responses

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid parameters or file type)
- 404: Not Found (file not found)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

Error response format:

```json
{
  "detail": "Error message description"
}
```

## Security Features

- File type validation
- File size limits
- Automatic temporary file cleanup
- Security headers
- CORS protection
- Trusted host middleware

## Development Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:

```
GOOGLE_API_KEY=your_api_key_here
```

4. Run the server:

```bash
uvicorn main:app --reload --port 8000
```

## Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t redaction-backend .

# Run the container
docker run -p 8000:8000 --env-file .env redaction-backend
```

## Performance Considerations

- Large files are processed in chunks (1MB)
- Async processing for better performance
- LRU caching for repeated operations
- Thread pool for CPU-intensive tasks
- Optimized regex patterns

```

```
