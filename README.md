# Syntaxis

Modern Greek sentence generator using grammatical templates.

## REST API

The Syntaxis REST API provides HTTP endpoints for generating Greek sentences from grammatical templates.

### Starting the Server

```bash
# Development mode with auto-reload
uv run uvicorn syntaxis.service.app:app --reload --port 8000

# Production mode
uv run uvicorn syntaxis.service.app:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once the server is running, view the auto-generated documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Usage

**Generate lexicals from a template:**

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{"template": "[article:nom:masc:sg] [noun:nom:masc:sg]"}'
```

**Response:**

```json
{
  "template": "[article:nom:masc:sg] [noun:nom:masc:sg]",
  "lexicals": [
    {
      "lemma": "¿",
      "word": ["¿"],
      "translations": ["the"],
      "features": {
        "case": "nom",
        "gender": "masc",
        "number": "sg"
      }
    },
    {
      "lemma": "¬½´Á±Â",
      "word": ["¬½´Á±Â"],
      "translations": ["man", "male"],
      "features": {
        "case": "nom",
        "gender": "masc",
        "number": "sg"
      }
    }
  ]
}
```

**Health check:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "syntaxis-api"
}
```
