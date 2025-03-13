# Legal Citation API

A FastAPI-based REST API for validating and processing legal citations across multiple jurisdictions and citation styles.

## Features

- Citation validation across multiple jurisdictions
- Hyperlink generation for legal citations
- Support for multiple citation styles (Bluebook, OSCOLA, AGLC, etc.)
- Comprehensive jurisdiction coverage (US, UK, EU, Australia, India, etc.)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the API

Start the API server:

```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /validate

Validate a legal citation according to specified style and jurisdiction.

Example request for US Supreme Court citation:

```json
{
  "citation": "Brown v. Board of Education, 347 U.S. 483 (1954)",
  "style": "Bluebook (US)",
  "jurisdiction_type": "US_SUPREME_COURT"
}
```

Example request for US Federal citation:

```json
{
  "citation": "Smith v. Jones, 123 F.3d 456 (9th Cir. 2000)",
  "style": "Bluebook (US)",
  "jurisdiction_type": "US_FEDERAL"
}
```

### POST /hyperlink

Generate a hyperlink for a legal citation.

Example request:

```json
{
  "citation": "Brown v. Board of Education, 347 U.S. 483 (1954)",
  "style": "Bluebook (US)"
}
```

### GET /styles

Get a list of all supported citation styles. Use the values (not the keys) from this endpoint in your requests.

Example response:

```json
{
  "BLUEBOOK_US": "Bluebook (US)",
  "OSCOLA": "Oxford Standard Citation of Legal Authorities",
  ...
}
```

### GET /jurisdictions

Get a list of all supported jurisdictions. Use the exact jurisdiction names in your requests.

Example response:

```json
[
  "US_FEDERAL",
  "US_STATE",
  "US_SUPREME_COURT",
  "UK_SUPREME_COURT",
  ...
]
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Successful operation
- 400: Bad request (invalid input)
- 422: Validation error (invalid jurisdiction name)
- 500: Server error

Errors include detailed messages to help with debugging.

## Making Requests

Important: When making requests, use the exact jurisdiction names from the `/jurisdictions` endpoint.

✅ Correct for US Supreme Court:

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "citation": "Brown v. Board of Education, 347 U.S. 483 (1954)",
    "style": "Bluebook (US)",
    "jurisdiction_type": "US_SUPREME_COURT"
  }'
```

✅ Correct for US Federal:

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "citation": "Smith v. Jones, 123 F.3d 456 (9th Cir. 2000)",
    "style": "Bluebook (US)",
    "jurisdiction_type": "US_FEDERAL"
  }'
```
