# REST API Service Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add FastAPI REST API service that accepts Greek grammar templates and returns JSON representations of generated lexicals.

**Architecture:** Clean architecture with dependency injection. Service layer (syntaxis/service/) wraps existing Syntaxis class. API layer handles HTTP, schemas handle validation, core handles business logic.

**Tech Stack:** FastAPI, Pydantic, uvicorn, httpx (testing)

---

## Task 1: Add Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add FastAPI dependencies to pyproject.toml**

Add to the `dependencies` array in `pyproject.toml`:

```toml
dependencies = [
    "modern-greek-inflexion",
    "prettytable>=3.16.0",
    "typer>=0.12.3",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
]
```

Add to the `dev` dependency group:

```toml
dev = [
    "pudb>=2025.1.3",
    "autoflake>=2.0.0",
    "black>=25.9.0",
    "ipython>=8.37.0",
    "isort>=7.0.0",
    "pytest>=8.4.2",
    "httpx>=0.27.0",
]
```

**Step 2: Sync dependencies**

Run: `uv sync`
Expected: Dependencies resolved and installed successfully

**Step 3: Commit dependency changes**

```bash
git add pyproject.toml uv.lock
git commit -m "build: add FastAPI dependencies for REST API service

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Create Project Structure

**Files:**
- Create: `syntaxis/service/__init__.py`
- Create: `syntaxis/service/api/__init__.py`
- Create: `syntaxis/service/core/__init__.py`
- Create: `syntaxis/service/schemas/__init__.py`

**Step 1: Create service directory structure**

Run:
```bash
mkdir -p syntaxis/service/api
mkdir -p syntaxis/service/core
mkdir -p syntaxis/service/schemas
```

**Step 2: Create __init__.py files**

Create empty `syntaxis/service/__init__.py`:
```python
"""FastAPI REST API service for Syntaxis."""
```

Create empty `syntaxis/service/api/__init__.py`:
```python
"""API routes and HTTP handlers."""
```

Create empty `syntaxis/service/core/__init__.py`:
```python
"""Business logic layer."""
```

Create empty `syntaxis/service/schemas/__init__.py`:
```python
"""Pydantic models for request/response validation."""
```

**Step 3: Verify structure**

Run: `find syntaxis/service -type f -name "*.py"`
Expected: Lists all 4 __init__.py files

**Step 4: Commit structure**

```bash
git add syntaxis/service/
git commit -m "feat: create service layer directory structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Implement Request Schema

**Files:**
- Create: `syntaxis/service/schemas/requests.py`
- Create: `tests/service/schemas/test_requests.py`

**Step 1: Write failing test for request schema**

Create `tests/service/schemas/test_requests.py`:

```python
import pytest
from pydantic import ValidationError

from syntaxis.service.schemas.requests import GenerateRequest


def test_generate_request_valid_template():
    """Valid template string creates request successfully."""
    request = GenerateRequest(template="[noun:nom:masc:sg]")
    assert request.template == "[noun:nom:masc:sg]"


def test_generate_request_requires_template():
    """Request requires template field."""
    with pytest.raises(ValidationError) as exc_info:
        GenerateRequest()

    assert "template" in str(exc_info.value)


def test_generate_request_rejects_empty_template():
    """Request rejects empty template string."""
    with pytest.raises(ValidationError) as exc_info:
        GenerateRequest(template="")

    assert "template" in str(exc_info.value)


def test_generate_request_accepts_complex_template():
    """Request accepts complex multi-token templates."""
    template = "[article:nom:masc:sg] [noun:nom:masc:sg] [verb:present:active:ter:sg]"
    request = GenerateRequest(template=template)
    assert request.template == template
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/service/schemas/test_requests.py -v`
Expected: FAIL with "No module named 'syntaxis.service.schemas.requests'"

**Step 3: Create service schemas directory**

Run: `mkdir -p tests/service/schemas`

Create `tests/service/__init__.py`:
```python
"""Tests for service layer."""
```

Create `tests/service/schemas/__init__.py`:
```python
"""Tests for request/response schemas."""
```

**Step 4: Write minimal implementation**

Create `syntaxis/service/schemas/requests.py`:

```python
"""Request schemas for API endpoints."""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request body for generating lexicals from a template.

    Attributes:
        template: Greek grammar template string (e.g., "[noun:nom:masc:sg]")
    """

    template: str = Field(
        ...,
        min_length=1,
        description="Greek grammar template with tokens like [noun:nom:masc:sg]",
        examples=["[article:nom:masc:sg] [noun:nom:masc:sg]"],
    )
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/service/schemas/test_requests.py -v`
Expected: 4 passed

**Step 6: Commit**

```bash
git add syntaxis/service/schemas/requests.py tests/service/
git commit -m "feat: add GenerateRequest schema with validation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Implement Response Schemas

**Files:**
- Create: `syntaxis/service/schemas/responses.py`
- Create: `tests/service/schemas/test_responses.py`

**Step 1: Write failing test for response schemas**

Create `tests/service/schemas/test_responses.py`:

```python
from syntaxis.service.schemas.responses import GenerateResponse, LexicalResponse


def test_lexical_response_minimal():
    """LexicalResponse with minimal fields."""
    lexical = LexicalResponse(
        lemma="άνδρας",
        word={"άνδρας"},
        translations={"man", "male"},
        features={"case": "nom", "gender": "masc", "number": "sg"},
    )
    assert lexical.lemma == "άνδρας"
    assert lexical.word == {"άνδρας"}
    assert lexical.features["case"] == "nom"


def test_lexical_response_allows_none_word():
    """LexicalResponse allows None for word field."""
    lexical = LexicalResponse(
        lemma="test",
        word=None,
        translations={"test"},
        features={},
    )
    assert lexical.word is None


def test_lexical_response_allows_none_translations():
    """LexicalResponse allows None for translations field."""
    lexical = LexicalResponse(
        lemma="test",
        word={"test"},
        translations=None,
        features={},
    )
    assert lexical.translations is None


def test_generate_response_with_lexicals():
    """GenerateResponse contains template and lexicals."""
    lexicals = [
        LexicalResponse(
            lemma="ο",
            word={"ο"},
            translations={"the"},
            features={"case": "nom", "gender": "masc", "number": "sg"},
        ),
        LexicalResponse(
            lemma="άνδρας",
            word={"άνδρας"},
            translations={"man"},
            features={"case": "nom", "gender": "masc", "number": "sg"},
        ),
    ]

    response = GenerateResponse(
        template="[article:nom:masc:sg] [noun:nom:masc:sg]",
        lexicals=lexicals,
    )

    assert response.template == "[article:nom:masc:sg] [noun:nom:masc:sg]"
    assert len(response.lexicals) == 2
    assert response.lexicals[0].lemma == "ο"


def test_generate_response_empty_lexicals():
    """GenerateResponse allows empty lexicals list."""
    response = GenerateResponse(template="test", lexicals=[])
    assert response.lexicals == []
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/service/schemas/test_responses.py -v`
Expected: FAIL with "No module named 'syntaxis.service.schemas.responses'"

**Step 3: Write minimal implementation**

Create `syntaxis/service/schemas/responses.py`:

```python
"""Response schemas for API endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class LexicalResponse(BaseModel):
    """Response model for a single lexical item.

    Attributes:
        lemma: Dictionary form of the word
        word: Set of inflected forms (None if not yet inflected)
        translations: Set of English translations
        features: Dictionary of grammatical features
    """

    lemma: str = Field(
        ...,
        description="Dictionary form of the Greek word",
        examples=["άνδρας"],
    )
    word: Optional[set[str]] = Field(
        None,
        description="Inflected word form(s)",
        examples=[{"άνδρας"}],
    )
    translations: Optional[set[str]] = Field(
        None,
        description="English translations",
        examples=[{"man", "male"}],
    )
    features: dict[str, str] = Field(
        ...,
        description="Grammatical features (case, gender, number, etc.)",
        examples=[{"case": "nom", "gender": "masc", "number": "sg"}],
    )


class GenerateResponse(BaseModel):
    """Response model for generate endpoint.

    Attributes:
        template: The original template string that was processed
        lexicals: List of generated lexical items with their features
    """

    template: str = Field(
        ...,
        description="Original template string",
        examples=["[article:nom:masc:sg] [noun:nom:masc:sg]"],
    )
    lexicals: list[LexicalResponse] = Field(
        ...,
        description="Generated lexicals matching the template",
    )
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/service/schemas/test_responses.py -v`
Expected: 5 passed

**Step 5: Commit**

```bash
git add syntaxis/service/schemas/responses.py tests/service/schemas/test_responses.py
git commit -m "feat: add response schemas for API endpoints

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Implement Service Layer

**Files:**
- Create: `syntaxis/service/core/service.py`
- Create: `tests/service/core/test_service.py`

**Step 1: Write failing test for service layer**

Create `tests/service/core/__init__.py`:
```python
"""Tests for core business logic."""
```

Create `tests/service/core/test_service.py`:

```python
from unittest.mock import Mock

import pytest

from syntaxis.api import Syntaxis
from syntaxis.models.lexical import Noun
from syntaxis.service.core.service import SyntaxisService


@pytest.fixture
def mock_syntaxis():
    """Mock Syntaxis instance for testing."""
    return Mock(spec=Syntaxis)


@pytest.fixture
def service(mock_syntaxis):
    """SyntaxisService instance with mocked dependencies."""
    return SyntaxisService(syntaxis=mock_syntaxis)


def test_service_initializes_with_syntaxis(mock_syntaxis):
    """Service stores Syntaxis instance."""
    service = SyntaxisService(syntaxis=mock_syntaxis)
    assert service.syntaxis is mock_syntaxis


def test_generate_from_template_calls_syntaxis(service, mock_syntaxis):
    """Service delegates to Syntaxis.generate_sentence."""
    template = "[noun:nom:masc:sg]"

    # Create a mock noun with to_json method
    mock_noun = Mock(spec=Noun)
    mock_noun.to_json.return_value = {
        "lemma": "άνδρας",
        "word": {"άνδρας"},
        "translations": {"man"},
        "features": {"case": "nom", "gender": "masc", "number": "sg"},
    }

    mock_syntaxis.generate_sentence.return_value = [mock_noun]

    result = service.generate_from_template(template)

    mock_syntaxis.generate_sentence.assert_called_once_with(template)
    assert len(result) == 1
    assert result[0]["lemma"] == "άνδρας"


def test_generate_from_template_converts_to_json(service, mock_syntaxis):
    """Service calls to_json on each lexical."""
    template = "[noun:nom:masc:sg] [verb:present:active:ter:sg]"

    mock_noun = Mock()
    mock_noun.to_json.return_value = {"lemma": "άνδρας", "features": {}}

    mock_verb = Mock()
    mock_verb.to_json.return_value = {"lemma": "βλέπω", "features": {}}

    mock_syntaxis.generate_sentence.return_value = [mock_noun, mock_verb]

    result = service.generate_from_template(template)

    assert len(result) == 2
    mock_noun.to_json.assert_called_once()
    mock_verb.to_json.assert_called_once()


def test_generate_from_template_empty_result(service, mock_syntaxis):
    """Service handles empty lexical list."""
    mock_syntaxis.generate_sentence.return_value = []

    result = service.generate_from_template("[noun:nom:masc:sg]")

    assert result == []
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/service/core/test_service.py -v`
Expected: FAIL with "No module named 'syntaxis.service.core.service'"

**Step 3: Write minimal implementation**

Create `syntaxis/service/core/service.py`:

```python
"""Business logic layer for Syntaxis API service."""

from syntaxis.api import Syntaxis


class SyntaxisService:
    """Service layer that wraps Syntaxis core functionality.

    Provides business logic for generating Greek sentences from templates
    and converting lexicals to JSON format for API responses.

    Attributes:
        syntaxis: Syntaxis instance for sentence generation
    """

    def __init__(self, syntaxis: Syntaxis):
        """Initialize service with Syntaxis instance.

        Args:
            syntaxis: Syntaxis instance for generating sentences
        """
        self.syntaxis = syntaxis

    def generate_from_template(self, template: str) -> list[dict]:
        """Generate lexicals from template and convert to JSON.

        Args:
            template: Greek grammar template string

        Returns:
            List of dictionaries representing lexical objects

        Raises:
            TemplateParseError: If template syntax is invalid
            ValueError: If no words match the template features
        """
        lexicals = self.syntaxis.generate_sentence(template)
        return [lexical.to_json() for lexical in lexicals]
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/service/core/test_service.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add syntaxis/service/core/service.py tests/service/core/
git commit -m "feat: add SyntaxisService business logic layer

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Implement Dependency Injection

**Files:**
- Create: `syntaxis/service/dependencies.py`
- Create: `tests/service/test_dependencies.py`

**Step 1: Write failing test for dependencies**

Create `tests/service/test_dependencies.py`:

```python
from syntaxis.api import Syntaxis
from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.dependencies import get_service, get_syntaxis


def test_get_syntaxis_returns_instance():
    """get_syntaxis returns Syntaxis instance."""
    syntaxis = get_syntaxis()
    assert isinstance(syntaxis, Syntaxis)
    assert syntaxis.database is not None
    assert syntaxis.template is not None


def test_get_syntaxis_uses_default_db_path():
    """get_syntaxis uses ./syntaxis.db by default."""
    syntaxis = get_syntaxis()
    assert syntaxis.database.db_path == "./syntaxis.db"


def test_get_service_returns_instance():
    """get_service returns SyntaxisService instance."""
    syntaxis = get_syntaxis()
    service = get_service(syntaxis)
    assert isinstance(service, SyntaxisService)
    assert service.syntaxis is syntaxis


def test_get_service_with_custom_syntaxis():
    """get_service accepts custom Syntaxis instance."""
    custom_syntaxis = Syntaxis(db_path="./test.db")
    service = get_service(custom_syntaxis)
    assert service.syntaxis is custom_syntaxis
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/service/test_dependencies.py -v`
Expected: FAIL with "No module named 'syntaxis.service.dependencies'"

**Step 3: Write minimal implementation**

Create `syntaxis/service/dependencies.py`:

```python
"""Dependency injection for FastAPI service."""

from syntaxis.api import Syntaxis
from syntaxis.service.core.service import SyntaxisService


def get_syntaxis() -> Syntaxis:
    """Get Syntaxis instance with default configuration.

    Returns:
        Syntaxis instance connected to ./syntaxis.db
    """
    return Syntaxis(db_path="./syntaxis.db")


def get_service(syntaxis: Syntaxis) -> SyntaxisService:
    """Get SyntaxisService instance.

    This is a factory function used by FastAPI's dependency injection.
    In routes, use: service: SyntaxisService = Depends(get_service)

    Args:
        syntaxis: Syntaxis instance (injected by FastAPI)

    Returns:
        SyntaxisService instance
    """
    return SyntaxisService(syntaxis=syntaxis)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/service/test_dependencies.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add syntaxis/service/dependencies.py tests/service/test_dependencies.py
git commit -m "feat: add dependency injection for service layer

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Implement API Routes

**Files:**
- Create: `syntaxis/service/api/routes.py`
- Create: `tests/service/api/test_routes.py`

**Step 1: Write failing test for routes**

Create `tests/service/api/__init__.py`:
```python
"""Tests for API routes."""
```

Create `tests/service/api/test_routes.py`:

```python
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from syntaxis.service.api.routes import generate
from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.schemas.requests import GenerateRequest


@pytest.fixture
def mock_service():
    """Mock SyntaxisService for testing."""
    return Mock(spec=SyntaxisService)


@pytest.mark.asyncio
async def test_generate_endpoint_success(mock_service):
    """Generate endpoint returns lexicals on success."""
    request = GenerateRequest(template="[noun:nom:masc:sg]")

    mock_service.generate_from_template.return_value = [
        {
            "lemma": "άνδρας",
            "word": {"άνδρας"},
            "translations": {"man"},
            "features": {"case": "nom", "gender": "masc", "number": "sg"},
        }
    ]

    response = await generate(request=request, service=mock_service)

    assert response.template == "[noun:nom:masc:sg]"
    assert len(response.lexicals) == 1
    assert response.lexicals[0].lemma == "άνδρας"
    mock_service.generate_from_template.assert_called_once_with("[noun:nom:masc:sg]")


@pytest.mark.asyncio
async def test_generate_endpoint_template_parse_error(mock_service):
    """Generate endpoint returns 400 on template parse error."""
    request = GenerateRequest(template="[invalid")

    # Simulate template parse error
    mock_service.generate_from_template.side_effect = ValueError("Invalid template syntax")

    with pytest.raises(HTTPException) as exc_info:
        await generate(request=request, service=mock_service)

    assert exc_info.value.status_code == 400
    assert "Invalid template" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_endpoint_no_matching_words(mock_service):
    """Generate endpoint returns 500 when no words match."""
    request = GenerateRequest(template="[noun:nom:masc:sg]")

    # Simulate no matching words
    mock_service.generate_from_template.side_effect = ValueError("No words found")

    with pytest.raises(HTTPException) as exc_info:
        await generate(request=request, service=mock_service)

    assert exc_info.value.status_code == 500
    assert "No words found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_endpoint_multiple_lexicals(mock_service):
    """Generate endpoint handles multiple lexicals."""
    request = GenerateRequest(template="[article:nom:masc:sg] [noun:nom:masc:sg]")

    mock_service.generate_from_template.return_value = [
        {
            "lemma": "ο",
            "word": {"ο"},
            "translations": {"the"},
            "features": {"case": "nom", "gender": "masc", "number": "sg"},
        },
        {
            "lemma": "άνδρας",
            "word": {"άνδρας"},
            "translations": {"man"},
            "features": {"case": "nom", "gender": "masc", "number": "sg"},
        },
    ]

    response = await generate(request=request, service=mock_service)

    assert len(response.lexicals) == 2
    assert response.lexicals[0].lemma == "ο"
    assert response.lexicals[1].lemma == "άνδρας"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/service/api/test_routes.py -v`
Expected: FAIL with "No module named 'syntaxis.service.api.routes'"

**Step 3: Write minimal implementation**

Create `syntaxis/service/api/routes.py`:

```python
"""API route handlers."""

from fastapi import APIRouter, Depends, HTTPException

from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.dependencies import get_service, get_syntaxis
from syntaxis.service.schemas.requests import GenerateRequest
from syntaxis.service.schemas.responses import GenerateResponse, LexicalResponse

router = APIRouter(prefix="/api/v1", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: SyntaxisService = Depends(lambda: get_service(get_syntaxis())),
) -> GenerateResponse:
    """Generate Greek lexicals from a grammatical template.

    Args:
        request: Request containing the template string
        service: Injected SyntaxisService instance

    Returns:
        Response containing the template and generated lexicals

    Raises:
        HTTPException: 400 if template is invalid, 500 if generation fails
    """
    try:
        lexicals_json = service.generate_from_template(request.template)

        # Convert to Pydantic models
        lexicals = [LexicalResponse(**lex) for lex in lexicals_json]

        return GenerateResponse(template=request.template, lexicals=lexicals)

    except ValueError as e:
        error_msg = str(e)

        # Template parse errors return 400
        if "template" in error_msg.lower() or "invalid" in error_msg.lower():
            raise HTTPException(status_code=400, detail=f"Invalid template: {error_msg}")

        # No matching words returns 500
        raise HTTPException(status_code=500, detail=error_msg)

    except Exception as e:
        # Unexpected errors return 500
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/service/api/test_routes.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add syntaxis/service/api/routes.py tests/service/api/
git commit -m "feat: add API route handler for generate endpoint

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Implement FastAPI Application

**Files:**
- Create: `syntaxis/service/app.py`

**Step 1: Write implementation for FastAPI app**

Create `syntaxis/service/app.py`:

```python
"""FastAPI application setup and configuration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from syntaxis.service.api.routes import router

# Create FastAPI application
app = FastAPI(
    title="Syntaxis API",
    description="REST API for generating Greek sentences from grammatical templates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors.

    Args:
        request: The request that caused the exception
        exc: The exception that was raised

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Register routers
app.include_router(router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint.

    Returns:
        Status indicating the service is running
    """
    return {"status": "healthy", "service": "syntaxis-api"}
```

**Step 2: Test app can be imported**

Run: `uv run python -c "from syntaxis.service.app import app; print('App imported successfully')"`
Expected: "App imported successfully"

**Step 3: Commit**

```bash
git add syntaxis/service/app.py
git commit -m "feat: add FastAPI application with health check

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Add Integration Tests

**Files:**
- Create: `tests/integration/test_api_integration.py`

**Step 1: Write integration tests**

Create `tests/integration/__init__.py`:
```python
"""Integration tests for the full API."""
```

Create `tests/integration/test_api_integration.py`:

```python
"""Integration tests for REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from syntaxis.service.app import app

client = TestClient(app)


def test_health_check():
    """Health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "syntaxis-api"}


def test_generate_endpoint_valid_template():
    """Generate endpoint returns lexicals for valid template."""
    response = client.post(
        "/api/v1/generate",
        json={"template": "[noun:nom:masc:sg]"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "template" in data
    assert "lexicals" in data
    assert data["template"] == "[noun:nom:masc:sg]"
    assert len(data["lexicals"]) == 1

    lexical = data["lexicals"][0]
    assert "lemma" in lexical
    assert "word" in lexical
    assert "translations" in lexical
    assert "features" in lexical
    assert lexical["features"]["case"] == "nom"
    assert lexical["features"]["gender"] == "masc"
    assert lexical["features"]["number"] == "sg"


def test_generate_endpoint_complex_template():
    """Generate endpoint handles complex multi-token template."""
    response = client.post(
        "/api/v1/generate",
        json={"template": "[article:nom:masc:sg] [noun:nom:masc:sg] [verb:present:active:ter:sg]"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["lexicals"]) == 3
    assert data["lexicals"][0]["features"]["case"] == "nom"
    assert data["lexicals"][1]["features"]["case"] == "nom"
    assert data["lexicals"][2]["tense"] == "present" or "features" in data["lexicals"][2]


def test_generate_endpoint_invalid_template():
    """Generate endpoint returns 400 for invalid template."""
    response = client.post(
        "/api/v1/generate",
        json={"template": "[invalid:syntax"},
    )

    assert response.status_code == 400
    assert "detail" in response.json()


def test_generate_endpoint_missing_template():
    """Generate endpoint returns 422 for missing template."""
    response = client.post(
        "/api/v1/generate",
        json={},
    )

    assert response.status_code == 422


def test_generate_endpoint_empty_template():
    """Generate endpoint returns 422 for empty template."""
    response = client.post(
        "/api/v1/generate",
        json={"template": ""},
    )

    assert response.status_code == 422


def test_openapi_docs_available():
    """OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available():
    """ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200
```

**Step 2: Run integration tests**

Run: `uv run pytest tests/integration/test_api_integration.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add tests/integration/
git commit -m "test: add integration tests for REST API

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Run Full Test Suite

**Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass (147 existing + new service tests)

**Step 2: Check test coverage**

Run: `uv run pytest tests/service/ tests/integration/ -v --tb=short`
Expected: All service and integration tests pass

**Step 3: Verify app can start**

Run: `uv run uvicorn syntaxis.service.app:app --reload --port 8000` (background)
Expected: Server starts on http://127.0.0.1:8000

Then test manually:
```bash
curl http://127.0.0.1:8000/health
```
Expected: `{"status":"healthy","service":"syntaxis-api"}`

Stop the server with Ctrl+C.

**Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete REST API service implementation

Added FastAPI REST API with:
- POST /api/v1/generate endpoint
- Request/response schemas with Pydantic
- Service layer with dependency injection
- Comprehensive unit and integration tests
- Health check endpoint
- OpenAPI documentation at /docs

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 11: Update Documentation

**Files:**
- Modify: `README.md`

**Step 1: Add REST API section to README**

Add the following section to `README.md` after the existing content:

```markdown
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
```

**Step 2: Verify README renders correctly**

Run: `cat README.md | grep -A 5 "REST API"`
Expected: Shows the new REST API section

**Step 3: Commit documentation**

```bash
git add README.md
git commit -m "docs: add REST API usage to README

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Verification Steps

After completing all tasks, verify the implementation:

1. **All tests pass:**
   ```bash
   uv run pytest -v
   ```

2. **Server starts successfully:**
   ```bash
   uv run uvicorn syntaxis.service.app:app --reload --port 8000
   ```

3. **Health check works:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Generate endpoint works:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/generate" \
     -H "Content-Type: application/json" \
     -d '{"template": "[noun:nom:masc:sg]"}'
   ```

5. **Documentation loads:**
   - Visit http://localhost:8000/docs in browser
   - Verify Swagger UI shows generate endpoint
   - Test endpoint through Swagger UI

---

## Notes

- All tests follow TDD: write failing test → verify failure → implement → verify pass
- Commits use conventional commits format with co-author attribution
- Service layer uses dependency injection for testability
- Error handling distinguishes between client errors (400) and server errors (500)
- Integration tests verify full request/response cycle
- OpenAPI docs are auto-generated by FastAPI
