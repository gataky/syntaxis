# REST API Service Design

**Date:** 2025-11-10
**Status:** Approved

## Overview

Add a REST API service to the Syntaxis project using FastAPI. The API will accept Greek grammar templates and return JSON representations of the generated lexicals using their existing `to_json()` methods.

## Requirements

- **Framework:** FastAPI with uvicorn ASGI server
- **Architecture:** Clean architecture with dependency injection
- **Endpoint:** Single POST endpoint that accepts template, returns lexicals as JSON
- **Features:**
  - Basic error handling (400 for bad requests, 500 for server errors)
  - Auto-generated API documentation (OpenAPI/Swagger)
  - Type safety with Pydantic models

## Project Structure

```
syntaxis/
  service/
    __init__.py
    app.py              # FastAPI app initialization, middleware, exception handlers
    dependencies.py     # Dependency injection setup
    api/
      __init__.py
      routes.py         # Route handlers (thin controllers)
    core/
      __init__.py
      service.py        # SyntaxisService - business logic layer
    schemas/
      __init__.py
      requests.py       # Pydantic request models
      responses.py      # Pydantic response models
```

### Architecture Layers

1. **api/**: HTTP layer - handles requests/responses, no business logic
2. **core/**: Business logic - wraps existing Syntaxis class, handles generation and conversion to JSON
3. **schemas/**: Data validation - Pydantic models for type safety
4. **dependencies.py**: DI factory functions (database path, Syntaxis instance)

The existing `syntaxis/api.py` (Syntaxis class) remains unchanged and is imported by the service layer.

## API Design

### Endpoint

```
POST /api/v1/generate
```

### Request

```json
{
  "template": "[article:nom:masc:sg] [noun:nom:masc:sg]"
}
```

### Response (200 OK)

```json
{
  "template": "[article:nom:masc:sg] [noun:nom:masc:sg]",
  "lexicals": [
    {
      "lemma": "ο",
      "word": ["ο"],
      "translations": ["the"],
      "features": {
        "case": "nom",
        "gender": "masc",
        "number": "sg"
      }
    },
    {
      "lemma": "άνδρας",
      "word": ["άνδρας"],
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

### Error Response (400 Bad Request)

```json
{
  "detail": "Invalid template format: missing closing bracket"
}
```

### Error Response (500 Internal Server Error)

```json
{
  "detail": "No words found matching features for token: [noun:nom:masc:sg]"
}
```

### Documentation

- Swagger UI available at `/docs`
- ReDoc available at `/redoc`

## Implementation Components

### Request Flow

```
HTTP POST → routes.py → SyntaxisService → Syntaxis class → Lexical.to_json()
                ↓
         Pydantic validation
```

### 1. Request Schema (schemas/requests.py)

```python
class GenerateRequest(BaseModel):
    template: str
    # Future: add optional seed for reproducible random selection
```

### 2. Response Schema (schemas/responses.py)

```python
class LexicalResponse(BaseModel):
    lemma: str
    word: set[str] | None
    translations: set[str] | None
    features: dict[str, str]

class GenerateResponse(BaseModel):
    template: str
    lexicals: list[LexicalResponse]
```

### 3. Service Layer (core/service.py)

```python
class SyntaxisService:
    def __init__(self, syntaxis: Syntaxis):
        self.syntaxis = syntaxis

    def generate_from_template(self, template: str) -> list[dict]:
        lexicals = self.syntaxis.generate_sentence(template)
        return [lex.to_json() for lex in lexicals]
```

### 4. Dependency Injection (dependencies.py)

```python
def get_syntaxis() -> Syntaxis:
    return Syntaxis(db_path="./syntaxis.db")

def get_service(syntaxis: Syntaxis = Depends(get_syntaxis)) -> SyntaxisService:
    return SyntaxisService(syntaxis)
```

### 5. Routes (api/routes.py)

```python
@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: SyntaxisService = Depends(get_service)
):
    # Thin controller - delegates to service
```

### 6. Application Setup (app.py)

- FastAPI app initialization
- CORS middleware (disabled by default, can enable later)
- Exception handlers for custom errors
- Router registration with `/api/v1` prefix

## Error Handling

### Error Types

1. **Template Parse Errors** (400 Bad Request)
   - Invalid template syntax
   - Missing features for lexical type
   - Caught from Template.parse() exceptions

2. **Database Errors** (500 Internal Server Error)
   - No matching words found
   - Database connection issues
   - Caught from Database.get_random_word() exceptions

3. **Global Exception Handler**
   - Catches unexpected exceptions
   - Returns 500 with generic error message
   - Logs full traceback for debugging

## Testing Strategy

### Unit Tests (tests/service/)

- `test_service.py`: SyntaxisService logic
- `test_schemas.py`: Pydantic model validation
- Mock Syntaxis class to isolate service layer

### Integration Tests (tests/integration/)

- `test_api.py`: Full API endpoint tests
- Use TestClient from FastAPI
- Test with real database or test fixtures
- Verify JSON serialization of Lexical.to_json()

### Test Coverage

- Happy path: valid template returns lexicals
- Invalid template format
- Template with invalid features
- No words match criteria
- Database connection failure

## Dependencies

Add to `pyproject.toml`:

- `fastapi` - web framework
- `uvicorn[standard]` - ASGI server for running the API
- `pydantic` - data validation (comes with FastAPI)
- `httpx` - for testing (TestClient dependency)

## Running the Service

```bash
# Development
uvicorn syntaxis.service.app:app --reload --port 8000

# Production
uvicorn syntaxis.service.app:app --host 0.0.0.0 --port 8000
```

## Future Enhancements

- Request seed parameter for reproducible random word selection
- CORS middleware configuration
- Rate limiting
- Authentication/API keys
- Batch template processing
- Caching layer for database queries
