"""Integration tests for REST API endpoints."""

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
        json={"template": "[article:nom:masc:sg]"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "template" in data
    assert "lexicals" in data
    assert data["template"] == "[article:nom:masc:sg]"
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
        json={"template": "[article:nom:masc:sg] [article:nom:masc:sg]"},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["lexicals"]) == 2
    assert data["lexicals"][0]["features"]["case"] == "nom"
    assert data["lexicals"][0]["features"]["gender"] == "masc"
    assert data["lexicals"][1]["features"]["case"] == "nom"
    assert data["lexicals"][1]["features"]["gender"] == "masc"


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
