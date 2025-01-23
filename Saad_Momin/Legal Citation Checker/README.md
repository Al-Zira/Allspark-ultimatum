# Legal Citation Checker

A powerful API for validating, reformatting, and generating hyperlinks for legal citations across multiple jurisdictions and citation styles.

## Project Structure

```
Legal Citation Checker/
├── backend/
│   ├── __init__.py
│   ├── api.py
│   ├── main.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── .env.example        # Template for environment variables
│   └── .env                # Your actual environment variables (not in git)
├── frontend/
│   └── streamlit_app.py
├── docker-compose.yml
└── requirements.txt
```

## Setup Instructions

### Using Docker (Recommended)

1. Clone the repository
2. Set up environment variables:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your Google API key
   ```
3. Build and start the backend:
   ```bash
   docker-compose up --build
   ```
4. The API will be available at `http://localhost:8000`

### Docker Commands

#### Building and Running

1. Build the Docker image:

   ```bash
   # Build only
   docker-compose build

   # Build and see detailed output
   docker-compose build --progress=plain
   ```

2. Run the container:

   ```bash
   # Run in foreground (see logs)
   docker-compose up

   # Run in background
   docker-compose up -d
   ```

3. Build and run in one command:
   ```bash
   docker-compose up --build
   ```

#### Managing Containers

1. View running containers:

   ```bash
   docker-compose ps
   ```

2. Stop containers:

   ```bash
   # Stop while keeping containers
   docker-compose stop

   # Stop and remove containers
   docker-compose down
   ```

## API Documentation

### Available Endpoints

#### 1. Citation Validation

Validates a legal citation against a specific style guide.

```bash
POST /validate
Content-Type: application/json

{
    "citation": "410 U.S. 113",
    "style": "BLUEBOOK_US"
}
```

Example response:

```json
{
  "is_valid": false,
  "error_details": [
    "Missing parallel citation to a regional reporter.",
    "Page number should ideally include a pinpoint cite if referencing a specific part of the opinion."
  ],
  "suggested_correction": "410 U.S. 113, 93 S.Ct. 790 (1973)",
  "source_type": "case",
  "jurisdiction": "United States"
}
```

#### 2. Hyperlink Generation

Generates hyperlinks to legal resources for a given citation.

```bash
POST /hyperlink
Content-Type: application/json

{
    "citation": "410 U.S. 113",
    "jurisdiction": "US_SUPREME_COURT",
    "style": "BLUEBOOK_US"
}
```

Example response:

```json
{
  "hyperlinks": [
    "https://supreme.justia.com/cases/federal/us/410/113/",
    "https://scholar.google.com/scholar_case?case=&volume=410&page=113",
    "https://caselaw.findlaw.com/us-supreme-court/410/113.html"
  ],
  "primary_link": "https://supreme.justia.com/cases/federal/us/410/113/",
  "alternate_links": [
    "https://scholar.google.com/scholar_case?case=&volume=410&page=113",
    "https://caselaw.findlaw.com/us-supreme-court/410/113.html"
  ]
}
```

#### 3. Citation Reformatting

Reformats a citation from one style to another.

```bash
POST /reformat
Content-Type: application/json

{
    "citation": "Roe v. Wade, 410 U.S. 113 (1973)",
    "source_style": "BLUEBOOK_US",
    "target_style": "CHICAGO_MANUAL_LEGAL"
}
```

Example response:

```json
{
  "reformatted_citation": "*Roe v. Wade*, 410 U.S. 113 (1973)."
}
```

#### 4. Available Styles

Get a list of all supported citation styles.

```bash
GET /styles
```

Example response:

```json
{
  "BLUEBOOK_US": "Bluebook (US)",
  "ALWD": "ALWD Guide to Legal Citation",
  "CHICAGO_MANUAL_LEGAL": "Chicago Manual of Legal Citation"
  // ... more styles
}
```

#### 5. Available Jurisdictions

Get a list of all supported jurisdictions.

```bash
GET /jurisdictions
```

Example response:

```json
{
  "US_SUPREME_COURT": 1,
  "US_FEDERAL": "us_federal",
  "UK_SUPREME_COURT": 7
  // ... more jurisdictions
}
```

## Supported Citation Styles

- Bluebook (US)
- ALWD Guide to Legal Citation
- Chicago Manual of Legal Citation
- Oxford Standard Citation of Legal Authorities (OSCOLA)
- Canadian Guide to Uniform Legal Citation (McGill Guide)
- Australian Guide to Legal Citation (AGLC)
- And many more...

## Supported Jurisdictions

- United States (Supreme Court, Federal, State courts)
- United Kingdom (Supreme Court, High Court, etc.)
- India (Supreme Court, High Courts)
- European Union (Court of Justice, General Court)
- Australia (High Court, Federal Court)
- International Courts (ICJ, ICC)
