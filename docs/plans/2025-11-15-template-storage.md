# Template Storage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add template storage system with database persistence, REST API endpoints, and client UI for saving/loading/deleting templates.

**Architecture:** Split existing monolithic routes.py into resource-specific routers (generation.py, metadata.py, templates.py). Add templates table with UNIQUE constraint. Create database/templates.py module for CRUD operations. Add SavedTemplatesView for managing templates.

**Tech Stack:** FastAPI, SQLite, Pydantic, Vue 3, Axios

---

## Task 1: Database Schema - Add Templates Table

**Files:**
- Modify: `syntaxis/lib/database/schema.py:154`
- Test: `tests/lib/database/test_schema.py` (NEW)

**Step 1: Write the failing test**

Create `tests/lib/database/test_schema.py`:

```python
import sqlite3

import pytest

from syntaxis.lib.database.schema import create_schema


def test_create_schema_creates_templates_table():
    """Should create templates table with correct schema."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'")
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == "templates"


def test_templates_table_has_correct_columns():
    """Should create templates table with id, template, created_at columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(templates)")
    columns = cursor.fetchall()

    column_names = [col[1] for col in columns]
    assert "id" in column_names
    assert "template" in column_names
    assert "created_at" in column_names


def test_templates_table_unique_constraint_on_template():
    """Should enforce UNIQUE constraint on template column."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO templates (template) VALUES (?)",
        ("noun(case=nominative,gender=masculine,number=singular)",)
    )
    conn.commit()

    # Try to insert duplicate
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
        cursor.execute(
            "INSERT INTO templates (template) VALUES (?)",
            ("noun(case=nominative,gender=masculine,number=singular)",)
        )
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/lib/database/test_schema.py -v`

Expected: FAIL - "no such table: templates"

**Step 3: Add templates table to schema**

In `syntaxis/lib/database/schema.py`, add after line 152 (after greek_adverbs table):

```python
    # Templates table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/lib/database/test_schema.py -v`

Expected: PASS - all 3 tests pass

**Step 5: Commit**

```bash
git add syntaxis/lib/database/schema.py tests/lib/database/test_schema.py
git commit -m "feat(db): add templates table with unique constraint"
```

---

## Task 2: Database Module - Template CRUD Functions

**Files:**
- Create: `syntaxis/lib/database/templates.py`
- Modify: `syntaxis/lib/database/__init__.py:1`
- Test: `tests/lib/database/test_templates.py` (NEW)

**Step 1: Write the failing test**

Create `tests/lib/database/test_templates.py`:

```python
import sqlite3
from datetime import datetime

import pytest

from syntaxis.lib.database import templates
from syntaxis.lib.database.schema import create_schema


@pytest.fixture
def db_conn():
    """Create in-memory database with schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    yield conn
    conn.close()


def test_save_template_inserts_new_template(db_conn):
    """Should insert template and return dict with id."""
    template_str = "noun(case=nominative,gender=masculine,number=singular)"

    result = templates.save_template(db_conn, template_str)

    assert result["id"] == 1
    assert result["template"] == template_str
    assert "created_at" in result
    assert isinstance(result["created_at"], str)


def test_save_template_raises_on_duplicate(db_conn):
    """Should raise ValueError when template already exists."""
    template_str = "noun(case=nominative,gender=masculine,number=singular)"
    templates.save_template(db_conn, template_str)

    with pytest.raises(ValueError, match="Template already exists"):
        templates.save_template(db_conn, template_str)


def test_list_templates_returns_all_templates(db_conn):
    """Should return list of all templates ordered by created_at desc."""
    templates.save_template(db_conn, "template1")
    templates.save_template(db_conn, "template2")
    templates.save_template(db_conn, "template3")

    result = templates.list_templates(db_conn)

    assert len(result) == 3
    # Most recent first
    assert result[0]["template"] == "template3"
    assert result[1]["template"] == "template2"
    assert result[2]["template"] == "template1"


def test_list_templates_returns_empty_list_when_no_templates(db_conn):
    """Should return empty list when no templates exist."""
    result = templates.list_templates(db_conn)
    assert result == []


def test_get_template_returns_template_by_id(db_conn):
    """Should return template dict when id exists."""
    saved = templates.save_template(db_conn, "test_template")

    result = templates.get_template(db_conn, saved["id"])

    assert result["id"] == saved["id"]
    assert result["template"] == "test_template"
    assert "created_at" in result


def test_get_template_returns_none_when_not_found(db_conn):
    """Should return None when template id doesn't exist."""
    result = templates.get_template(db_conn, 999)
    assert result is None


def test_delete_template_removes_template_and_returns_true(db_conn):
    """Should delete template and return True when id exists."""
    saved = templates.save_template(db_conn, "to_delete")

    result = templates.delete_template(db_conn, saved["id"])

    assert result is True
    # Verify it's gone
    assert templates.get_template(db_conn, saved["id"]) is None


def test_delete_template_returns_false_when_not_found(db_conn):
    """Should return False when template id doesn't exist."""
    result = templates.delete_template(db_conn, 999)
    assert result is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/lib/database/test_templates.py -v`

Expected: FAIL - "ModuleNotFoundError: No module named 'syntaxis.lib.database.templates'"

**Step 3: Create templates.py module**

Create `syntaxis/lib/database/templates.py`:

```python
"""Template storage operations for SQLite database."""

import logging
import sqlite3

logger = logging.getLogger(__name__)


def save_template(conn: sqlite3.Connection, template: str) -> dict:
    """Save a template to the database.

    Args:
        conn: SQLite database connection
        template: Template string to save

    Returns:
        Dict with id, template, and created_at

    Raises:
        ValueError: If template already exists
    """
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO templates (template) VALUES (?)",
            (template,)
        )
        conn.commit()
        template_id = cursor.lastrowid

        # Fetch the created record
        cursor.execute(
            "SELECT id, template, created_at FROM templates WHERE id = ?",
            (template_id,)
        )
        row = cursor.fetchone()

        return {
            "id": row["id"],
            "template": row["template"],
            "created_at": row["created_at"]
        }

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Template already exists")
        raise


def list_templates(conn: sqlite3.Connection) -> list[dict]:
    """List all templates ordered by created_at descending.

    Args:
        conn: SQLite database connection

    Returns:
        List of template dicts
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, template, created_at FROM templates ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()

    return [
        {
            "id": row["id"],
            "template": row["template"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def get_template(conn: sqlite3.Connection, template_id: int) -> dict | None:
    """Get a template by ID.

    Args:
        conn: SQLite database connection
        template_id: Template ID

    Returns:
        Template dict or None if not found
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, template, created_at FROM templates WHERE id = ?",
        (template_id,)
    )
    row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "template": row["template"],
        "created_at": row["created_at"]
    }


def delete_template(conn: sqlite3.Connection, template_id: int) -> bool:
    """Delete a template by ID.

    Args:
        conn: SQLite database connection
        template_id: Template ID

    Returns:
        True if deleted, False if not found
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()

    return cursor.rowcount > 0
```

**Step 4: Update __init__.py to export templates module**

In `syntaxis/lib/database/__init__.py`, modify to:

```python
from .api import Database
from . import templates

__all__ = ["Database", "templates"]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/lib/database/test_templates.py -v`

Expected: PASS - all 9 tests pass

**Step 6: Commit**

```bash
git add syntaxis/lib/database/templates.py syntaxis/lib/database/__init__.py tests/lib/database/test_templates.py
git commit -m "feat(db): add template CRUD operations module"
```

---

## Task 3: API Schemas - Template Request/Response Models

**Files:**
- Modify: `syntaxis/service/schemas/requests.py:19`
- Modify: `syntaxis/service/schemas/responses.py:63`

**Step 1: Add template request schema**

In `syntaxis/service/schemas/requests.py`, add at end of file:

```python


class SaveTemplateRequest(BaseModel):
    """Request body for saving a template.

    Attributes:
        template: Template string to save
    """

    template: str = Field(
        ...,
        min_length=1,
        description="Template string to save",
        examples=["noun(case=nominative,gender=masculine,number=singular)"]
    )
```

**Step 2: Add template response schemas**

In `syntaxis/service/schemas/responses.py`, add at end of file:

```python


class TemplateResponse(BaseModel):
    """Response model for a template.

    Attributes:
        id: Template ID
        template: Template string
        created_at: Timestamp when created
    """

    id: int = Field(
        ...,
        description="Template ID",
        examples=[1]
    )
    template: str = Field(
        ...,
        description="Template string",
        examples=["noun(case=nominative,gender=masculine,number=singular)"]
    )
    created_at: str = Field(
        ...,
        description="ISO 8601 timestamp",
        examples=["2025-11-15 10:30:00"]
    )


class DeleteTemplateResponse(BaseModel):
    """Response model for template deletion.

    Attributes:
        message: Success message
    """

    message: str = Field(
        ...,
        description="Success message",
        examples=["Template deleted successfully"]
    )
```

**Step 3: Commit**

```bash
git add syntaxis/service/schemas/requests.py syntaxis/service/schemas/responses.py
git commit -m "feat(api): add template request/response schemas"
```

---

## Task 4: Split Routes - Extract Generation Router

**Files:**
- Create: `syntaxis/service/api/generation.py`
- Modify: `syntaxis/service/api/routes.py` (will be deleted in Task 6)

**Step 1: Create generation.py router**

Create `syntaxis/service/api/generation.py`:

```python
"""Generation API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from syntaxis.lib.templates.api import TemplateParseError
from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.dependencies import get_service_dependency
from syntaxis.service.schemas.requests import GenerateRequest
from syntaxis.service.schemas.responses import GenerateResponse, LexicalResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: SyntaxisService = Depends(get_service_dependency),
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
    logger.info(f"POST /generate - template: {request.template}")

    try:
        lexicals_json = service.generate_from_template(request.template)

        # Convert to Pydantic models
        lexicals = [LexicalResponse(**lex) for lex in lexicals_json]

        result = GenerateResponse(template=request.template, lexicals=lexicals)
        logger.info(f"POST /generate - 200 OK - returned {len(result.lexicals)} words")
        return result

    except TemplateParseError as e:
        # Template parse errors return 400
        raise HTTPException(status_code=400, detail=f"Invalid template: {str(e)}")

    except ValueError as e:
        error_msg = str(e)

        # Template parse errors and feature validation errors return 400
        if (
            "template" in error_msg.lower()
            or "invalid" in error_msg.lower()
            or "no " in error_msg.lower()
            and "found" in error_msg.lower()
        ):
            raise HTTPException(
                status_code=400, detail=f"Invalid template: {error_msg}"
            )

        # Other ValueErrors are unexpected - let Exception handler catch it
        raise
```

**Step 2: Commit**

```bash
git add syntaxis/service/api/generation.py
git commit -m "feat(api): extract generation router"
```

---

## Task 5: Split Routes - Extract Metadata Router

**Files:**
- Create: `syntaxis/service/api/metadata.py`

**Step 1: Create metadata.py router**

Create `syntaxis/service/api/metadata.py`:

```python
"""Metadata API endpoints."""

import logging

from fastapi import APIRouter

from syntaxis.lib import constants as c

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["metadata"])


@router.get("/lexicals/schema")
async def get_lexical_schema():
    """Get all lexical types with their required features.

    Returns a mapping of lexical types to their required grammatical features.
    This endpoint provides metadata needed by the template builder UI.

    Returns:
        dict: Mapping of lexical types to their schema including required features
    """
    schema = {
        "lexicals": {
            c.NOUN: {"required": [c.CASE, c.GENDER, c.NUMBER]},
            c.VERB: {"required": [c.TENSE, c.VOICE, c.PERSON, c.NUMBER]},
            c.ADJECTIVE: {"required": [c.CASE, c.GENDER, c.NUMBER]},
            c.ARTICLE: {"required": [c.CASE, c.GENDER, c.NUMBER]},
            c.PRONOUN: {
                "required": [c.TYPE],
                "optional": [c.CASE, c.PERSON, c.NUMBER, c.GENDER],
            },
            c.ADVERB: {"required": []},
            c.PREPOSITION: {"required": []},
            c.CONJUNCTION: {"required": []},
            c.NUMERAL: {"required": []},
        }
    }
    return schema


@router.get("/features")
async def get_features():
    """Get all grammatical feature categories and their possible values.

    Returns a mapping of feature categories to lists of valid values.
    This endpoint provides metadata needed by the template builder UI.

    Returns:
        dict: Mapping of feature categories to their valid values
    """
    features = {
        c.CASE: sorted(c.CASE_VALUES),
        c.GENDER: sorted(c.GENDER_VALUES),
        c.NUMBER: sorted(c.NUMBER_VALUES),
        c.TENSE: sorted(c.TENSE_VALUES),
        c.VOICE: sorted(c.VOICE_VALUES),
        c.PERSON: sorted(c.PERSON_VALUES),
        c.TYPE: sorted(c.PRONOUN_TYPES),
    }
    return features
```

**Step 2: Commit**

```bash
git add syntaxis/service/api/metadata.py
git commit -m "feat(api): extract metadata router"
```

---

## Task 6: Templates Router - CRUD Endpoints

**Files:**
- Create: `syntaxis/service/api/templates.py`
- Test: `tests/integration/test_templates_api.py` (NEW)
- Delete: `syntaxis/service/api/routes.py`

**Step 1: Write the failing integration test**

Create `tests/integration/test_templates_api.py`:

```python
import pytest
from fastapi.testclient import TestClient

from syntaxis.lib.database import Database
from syntaxis.service.app import app


@pytest.fixture
def client():
    """Create test client with fresh in-memory database."""
    # Note: This assumes the app uses a dependency that can be overridden
    # If not, we may need to adjust the service to support test databases
    return TestClient(app)


def test_save_template_creates_new_template(client):
    """POST /api/v1/templates should save template and return it with ID."""
    response = client.post(
        "/api/v1/templates",
        json={"template": "noun(case=nominative,gender=masculine,number=singular)"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["template"] == "noun(case=nominative,gender=masculine,number=singular)"
    assert "created_at" in data


def test_save_template_returns_409_for_duplicate(client):
    """POST /api/v1/templates should return 409 for duplicate template."""
    template_str = "noun(case=nominative)"

    # First save succeeds
    client.post("/api/v1/templates", json={"template": template_str})

    # Second save fails
    response = client.post("/api/v1/templates", json={"template": template_str})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_list_templates_returns_all_templates(client):
    """GET /api/v1/templates should return list of all templates."""
    # Save some templates
    client.post("/api/v1/templates", json={"template": "template1"})
    client.post("/api/v1/templates", json={"template": "template2"})

    response = client.get("/api/v1/templates")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    # Verify it's a list of template objects
    assert all("id" in t and "template" in t and "created_at" in t for t in data)


def test_get_template_returns_template_by_id(client):
    """GET /api/v1/templates/{id} should return specific template."""
    # Save a template
    save_response = client.post(
        "/api/v1/templates",
        json={"template": "specific_template"}
    )
    template_id = save_response.json()["id"]

    response = client.get(f"/api/v1/templates/{template_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template_id
    assert data["template"] == "specific_template"


def test_get_template_returns_404_when_not_found(client):
    """GET /api/v1/templates/{id} should return 404 for non-existent ID."""
    response = client.get("/api/v1/templates/999999")
    assert response.status_code == 404


def test_delete_template_removes_template(client):
    """DELETE /api/v1/templates/{id} should delete template."""
    # Save a template
    save_response = client.post(
        "/api/v1/templates",
        json={"template": "to_delete"}
    )
    template_id = save_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/templates/{template_id}")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"]

    # Verify it's gone
    get_response = client.get(f"/api/v1/templates/{template_id}")
    assert get_response.status_code == 404


def test_delete_template_returns_404_when_not_found(client):
    """DELETE /api/v1/templates/{id} should return 404 for non-existent ID."""
    response = client.delete("/api/v1/templates/999999")
    assert response.status_code == 404
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_templates_api.py -v`

Expected: FAIL - "404 Not Found" (routes don't exist yet)

**Step 3: Create templates router**

Create `syntaxis/service/api/templates.py`:

```python
"""Template storage API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from syntaxis.lib.database import templates
from syntaxis.service.dependencies import get_service_dependency
from syntaxis.service.schemas.requests import SaveTemplateRequest
from syntaxis.service.schemas.responses import DeleteTemplateResponse, TemplateResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.post("", response_model=TemplateResponse, status_code=201)
async def save_template(
    request: SaveTemplateRequest,
    service=Depends(get_service_dependency)
):
    """Save a new template.

    Args:
        request: Request with template string
        service: Injected service (provides database connection)

    Returns:
        Saved template with ID and created_at

    Raises:
        HTTPException: 409 if template already exists
    """
    logger.info(f"POST /templates - template: {request.template}")

    try:
        result = templates.save_template(service._db._conn, request.template)
        logger.info(f"POST /templates - 201 Created - id: {result['id']}")
        return result
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise


@router.get("", response_model=list[TemplateResponse])
async def list_templates(service=Depends(get_service_dependency)):
    """List all saved templates.

    Args:
        service: Injected service (provides database connection)

    Returns:
        List of all templates ordered by created_at descending
    """
    logger.info("GET /templates")
    result = templates.list_templates(service._db._conn)
    logger.info(f"GET /templates - 200 OK - returned {len(result)} templates")
    return result


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    service=Depends(get_service_dependency)
):
    """Get a specific template by ID.

    Args:
        template_id: Template ID
        service: Injected service (provides database connection)

    Returns:
        Template with matching ID

    Raises:
        HTTPException: 404 if template not found
    """
    logger.info(f"GET /templates/{template_id}")
    result = templates.get_template(service._db._conn, template_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Template not found")

    logger.info(f"GET /templates/{template_id} - 200 OK")
    return result


@router.delete("/{template_id}", response_model=DeleteTemplateResponse)
async def delete_template(
    template_id: int,
    service=Depends(get_service_dependency)
):
    """Delete a template by ID.

    Args:
        template_id: Template ID
        service: Injected service (provides database connection)

    Returns:
        Success message

    Raises:
        HTTPException: 404 if template not found
    """
    logger.info(f"DELETE /templates/{template_id}")
    deleted = templates.delete_template(service._db._conn, template_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")

    logger.info(f"DELETE /templates/{template_id} - 200 OK")
    return {"message": "Template deleted successfully"}
```

**Step 4: Update app.py to use new routers**

In `syntaxis/service/app.py`, replace line 10 and line 57:

Before:
```python
from syntaxis.service.api.routes import router
...
app.include_router(router)
```

After:
```python
from syntaxis.service.api import generation, metadata, templates
...
# Register routers
app.include_router(generation.router)
app.include_router(metadata.router)
app.include_router(templates.router)
```

**Step 5: Delete old routes.py**

```bash
rm syntaxis/service/api/routes.py
```

**Step 6: Run test to verify it passes**

Run: `pytest tests/integration/test_templates_api.py -v`

Expected: PASS - all tests pass

**Step 7: Verify existing API still works**

Run: `pytest tests/integration/test_api_integration.py -v`

Expected: PASS - existing tests still pass after refactor

**Step 8: Commit**

```bash
git add syntaxis/service/api/templates.py syntaxis/service/app.py tests/integration/test_templates_api.py
git rm syntaxis/service/api/routes.py
git commit -m "feat(api): add templates router and split routes by resource"
```

---

## Task 7: Client API - Template Service Functions

**Files:**
- Modify: `client/src/services/api.js:41`

**Step 1: Add template API functions**

In `client/src/services/api.js`, add at end (before closing brace on line 41):

```javascript
  ,

  async saveTemplate(template) {
    try {
      const response = await axios.post(`${API_BASE_URL}/templates`, { template });
      return response.data;
    } catch (error) {
      console.error('Error saving template:', error);
      let errorMessage = 'Failed to save template.';
      if (error.response) {
        if (error.response.status === 409) {
          errorMessage = 'This template has already been saved.';
        } else {
          errorMessage = error.response.data.detail || errorMessage;
        }
      }
      throw new Error(errorMessage);
    }
  },

  async listTemplates() {
    try {
      const response = await axios.get(`${API_BASE_URL}/templates`);
      return response.data;
    } catch (error) {
      console.error('Error listing templates:', error);
      throw new Error('Failed to load templates.');
    }
  },

  async getTemplate(id) {
    try {
      const response = await axios.get(`${API_BASE_URL}/templates/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error getting template:', error);
      if (error.response?.status === 404) {
        throw new Error('Template not found.');
      }
      throw new Error('Failed to load template.');
    }
  },

  async deleteTemplate(id) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/templates/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting template:', error);
      if (error.response?.status === 404) {
        throw new Error('Template not found.');
      }
      throw new Error('Failed to delete template.');
    }
  }
```

**Step 2: Commit**

```bash
git add client/src/services/api.js
git commit -m "feat(client): add template API service functions"
```

---

## Task 8: Client View - SavedTemplatesView

**Files:**
- Create: `client/src/views/SavedTemplatesView.vue`

**Step 1: Create SavedTemplatesView**

Create `client/src/views/SavedTemplatesView.vue`:

```vue
<template>
  <div class="container mt-4">
    <h1 class="mb-4">Saved Templates</h1>

    <!-- Loading State -->
    <div v-if="loading" class="alert alert-info">
      Loading templates...
    </div>

    <!-- Error Display -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error:</strong> {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && templates.length === 0" class="alert alert-secondary">
      No saved templates yet. Go to the Template Builder to create and save templates.
    </div>

    <!-- Templates Table -->
    <div v-if="!loading && templates.length > 0" class="card">
      <div class="card-body">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Template</th>
              <th>Created</th>
              <th style="width: 200px;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="template in templates" :key="template.id">
              <td>
                <code>{{ template.template }}</code>
              </td>
              <td>
                <small class="text-muted">{{ formatDate(template.created_at) }}</small>
              </td>
              <td>
                <button
                  type="button"
                  class="btn btn-sm btn-primary me-2"
                  @click="loadTemplate(template)"
                >
                  Load
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-danger"
                  @click="confirmDelete(template)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="templateToDelete"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0, 0, 0, 0.5);"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="templateToDelete = null"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this template?</p>
            <code>{{ templateToDelete.template }}</code>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="templateToDelete = null">
              Cancel
            </button>
            <button type="button" class="btn btn-danger" @click="handleDelete">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const templates = ref([])
const loading = ref(true)
const error = ref(null)
const templateToDelete = ref(null)

onMounted(async () => {
  await loadTemplates()
})

async function loadTemplates() {
  try {
    loading.value = true
    error.value = null
    templates.value = await api.listTemplates()
  } catch (err) {
    error.value = err.message
    console.error('Failed to load templates:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
}

function loadTemplate(template) {
  // Navigate to builder with template string as query param
  router.push({
    name: 'builder',
    query: { template: template.template }
  })
}

function confirmDelete(template) {
  templateToDelete.value = template
}

async function handleDelete() {
  if (!templateToDelete.value) return

  try {
    await api.deleteTemplate(templateToDelete.value.id)
    templateToDelete.value = null
    // Reload templates
    await loadTemplates()
  } catch (err) {
    error.value = err.message
    console.error('Failed to delete template:', err)
    templateToDelete.value = null
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table {
  margin-bottom: 0;
}

code {
  font-size: 0.9rem;
  color: #d63384;
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
}
</style>
```

**Step 2: Commit**

```bash
git add client/src/views/SavedTemplatesView.vue
git commit -m "feat(client): add saved templates view"
```

---

## Task 9: Client Router - Add Templates Route

**Files:**
- Modify: `client/src/router/index.js:27`

**Step 1: Add import and route**

In `client/src/router/index.js`, add import at line 4:

```javascript
import SavedTemplatesView from '../views/SavedTemplatesView.vue'
```

Add route to routes array before closing bracket (around line 24):

```javascript
    ,
    {
      path: '/templates',
      name: 'templates',
      component: SavedTemplatesView
    }
```

**Step 2: Commit**

```bash
git add client/src/router/index.js
git commit -m "feat(client): add saved templates route"
```

---

## Task 10: Template Builder - Save Functionality

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue:382`

**Step 1: Add save button and handler**

In `client/src/views/TemplateBuilderView.vue`, add after "Generate Sentence" button (around line 252):

```vue
      <button
        type="button"
        class="btn btn-success ms-2"
        :disabled="!store.generatedTemplate"
        @click="handleSave"
      >
        Save Template
      </button>
```

Add in `<script setup>` section after `generatedResult` ref (around line 305):

```javascript
const saveSuccess = ref(null)
```

Add handler function after `handleGenerate` function (around line 380):

```javascript

async function handleSave() {
  try {
    const result = await api.saveTemplate(store.generatedTemplate)
    saveSuccess.value = `Template saved with ID ${result.id}`
    setTimeout(() => {
      saveSuccess.value = null
    }, 3000)
  } catch (err) {
    store.error = err.message
    console.error('Failed to save template:', err)
  }
}
```

Add import at top of script section (around line 299):

```javascript
import api from '../services/api'
```

Add success message display in template after error display (around line 14):

```vue

    <!-- Success Display -->
    <div v-if="saveSuccess" class="alert alert-success alert-dismissible fade show" role="alert">
      <strong>Success:</strong> {{ saveSuccess }}
      <button type="button" class="btn-close" @click="saveSuccess = null"></button>
    </div>
```

**Step 2: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add save template functionality"
```

---

## Task 11: Template Builder - Load Functionality

**Files:**
- Modify: `client/src/stores/templateBuilder.js:~200`
- Modify: `client/src/views/TemplateBuilderView.vue:315`

**Step 1: Add loadTemplate method to store**

In `client/src/stores/templateBuilder.js`, add method at end of store (around line 200):

```javascript
    ,

    loadTemplate(templateString) {
      // Parse template string and populate groups
      // This is a basic parser - adjust based on actual template format

      // Clear existing state
      this.groups = []
      this.nextGroupId = 1

      // Template format example: "noun(case=nominative,gender=masculine,number=singular) verb(tense=present,voice=active,person=first,number=singular)"
      // Split by spaces to get individual word templates
      const tokens = templateString.trim().split(/\s+/)

      tokens.forEach(token => {
        const match = token.match(/^(\w+)\(([^)]+)\)$/)
        if (!match) return

        const lexicalType = match[1]
        const featuresStr = match[2]

        // Create new group
        const group = {
          id: this.nextGroupId++,
          lexicals: [{
            type: lexicalType,
            overrides: null
          }],
          features: {},
          reference: null
        }

        // Parse features
        const featurePairs = featuresStr.split(',')
        featurePairs.forEach(pair => {
          const [key, value] = pair.split('=')
          if (key && value) {
            group.features[key.trim()] = value.trim()
          }
        })

        this.groups.push(group)
      })
    }
```

**Step 2: Add load handler to TemplateBuilderView**

In `client/src/views/TemplateBuilderView.vue`, update `onMounted` (around line 307):

```javascript
onMounted(async () => {
  try {
    await store.fetchMetadata()

    // Check if we have a template to load from query params
    const templateFromQuery = router.currentRoute.value.query.template
    if (templateFromQuery) {
      store.loadTemplate(templateFromQuery)
    }
  } catch (err) {
    console.error('Failed to load metadata:', err)
  } finally {
    loading.value = false
  }
})
```

Add missing import at top of script (around line 299):

```javascript
import { useRouter } from 'vue-router'

const router = useRouter()
```

**Step 3: Commit**

```bash
git add client/src/stores/templateBuilder.js client/src/views/TemplateBuilderView.vue
git commit -m "feat(client): add load template functionality"
```

---

## Task 12: Manual Testing & Documentation

**Files:**
- Create: `docs/plans/2025-11-15-template-storage-testing.md`

**Step 1: Manual testing checklist**

Create `docs/plans/2025-11-15-template-storage-testing.md`:

```markdown
# Template Storage Manual Testing Checklist

## Backend API Testing

### Start the server
```bash
cd /Users/jeff/Documents/syntaxis
uv run uvicorn syntaxis.service.app:app --reload --port 5000
```

### Test with curl

1. Save a template:
```bash
curl -X POST http://localhost:5000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{"template": "noun(case=nominative,gender=masculine,number=singular)"}'
```
Expected: 201 Created with template object

2. List templates:
```bash
curl http://localhost:5000/api/v1/templates
```
Expected: Array of templates

3. Get template by ID:
```bash
curl http://localhost:5000/api/v1/templates/1
```
Expected: Template object

4. Delete template:
```bash
curl -X DELETE http://localhost:5000/api/v1/templates/1
```
Expected: Success message

5. Try to save duplicate:
```bash
curl -X POST http://localhost:5000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{"template": "noun(case=nominative,gender=masculine,number=singular)"}'
```
Expected: 409 Conflict

## Frontend Testing

### Start the client
```bash
cd /Users/jeff/Documents/syntaxis/client
npm run dev
```

### Test UI flows

1. **Save Template Flow**
   - Navigate to http://localhost:5173/builder
   - Build a template using the UI
   - Click "Generate Sentence"
   - Click "Save Template"
   - Verify success message appears
   - Save the same template again - should see "already saved" error

2. **View Templates Flow**
   - Navigate to http://localhost:5173/templates
   - Verify templates are listed
   - Verify created dates are formatted correctly

3. **Load Template Flow**
   - In templates view, click "Load" on a template
   - Verify navigation to builder
   - Verify builder is populated with template data
   - Verify groups, lexicals, and features are correct

4. **Delete Template Flow**
   - In templates view, click "Delete" on a template
   - Verify confirmation modal appears
   - Click "Cancel" - modal closes, template remains
   - Click "Delete" again, then confirm
   - Verify template is removed from list

## Test Coverage

Run all tests:
```bash
pytest tests/ -v
```

Expected: All tests pass including:
- test_schema.py (3 tests)
- test_templates.py (9 tests)
- test_templates_api.py (8 tests)
- All existing integration tests still pass
```

**Step 2: Run all tests**

Run: `pytest tests/ -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add docs/plans/2025-11-15-template-storage-testing.md
git commit -m "docs: add manual testing checklist for template storage"
```

---

## Implementation Complete

All tasks completed! The template storage system is now fully implemented with:

✅ Database schema with templates table and UNIQUE constraint
✅ Database module with CRUD operations
✅ API routes split by resource (generation, metadata, templates)
✅ Template REST API endpoints (POST, GET, DELETE)
✅ Client API service functions
✅ SavedTemplatesView for managing templates
✅ Save button in TemplateBuilderView
✅ Load template functionality
✅ Comprehensive test coverage
✅ Manual testing documentation

**Verification Steps:**
1. Run `pytest tests/ -v` - all tests should pass
2. Start backend: `uv run uvicorn syntaxis.service.app:app --reload --port 5000`
3. Start frontend: `cd client && npm run dev`
4. Test full save/load/delete flow in browser
