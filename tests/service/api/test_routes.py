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
            "pos": "noun",
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
    mock_service.generate_from_template.side_effect = ValueError(
        "Invalid template syntax"
    )

    with pytest.raises(HTTPException) as exc_info:
        await generate(request=request, service=mock_service)

    assert exc_info.value.status_code == 400
    assert "Invalid template" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_endpoint_no_matching_words(mock_service):
    """Generate endpoint returns 400 when no words match."""
    request = GenerateRequest(template="[noun:nom:masc:sg]")

    # Simulate no matching words
    mock_service.generate_from_template.side_effect = ValueError("No words found")

    with pytest.raises(HTTPException) as exc_info:
        await generate(request=request, service=mock_service)

    assert exc_info.value.status_code == 400
    assert "No words found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generate_endpoint_multiple_lexicals(mock_service):
    """Generate endpoint handles multiple lexicals."""
    request = GenerateRequest(template="[article:nom:masc:sg] [noun:nom:masc:sg]")

    mock_service.generate_from_template.return_value = [
        {
            "pos": "article",
            "lemma": "ο",
            "word": {"ο"},
            "translations": {"the"},
            "features": {"case": "nom", "gender": "masc", "number": "sg"},
        },
        {
            "pos": "noun",
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


class TestV2TemplateRoutes:
    """Tests for V2 template support in API routes."""

    @pytest.mark.asyncio
    async def test_generate_endpoint_v2_template(self, mock_service):
        """POST /generate should accept V2 templates"""
        request = GenerateRequest(template="(noun)@{nom:masc:sg}")

        mock_service.generate_from_template.return_value = [
            {
                "pos": "noun",
                "lemma": "άνδρας",
                "word": {"άνδρας"},
                "translations": {"man"},
                "features": {"case": "nom", "gender": "masc", "number": "sg"},
            }
        ]

        response = await generate(request=request, service=mock_service)

        assert response.template == "(noun)@{nom:masc:sg}"
        assert len(response.lexicals) == 1
        assert response.lexicals[0].lemma == "άνδρας"
        mock_service.generate_from_template.assert_called_once_with(
            "(noun)@{nom:masc:sg}"
        )

    @pytest.mark.asyncio
    async def test_generate_endpoint_v2_with_reference(self, mock_service):
        """POST /generate should handle V2 references"""
        request = GenerateRequest(template="(article)@{nom:sg} (noun)@$1")

        mock_service.generate_from_template.return_value = [
            {
                "pos": "article",
                "lemma": "ο",
                "word": {"ο"},
                "translations": {"the"},
                "features": {"case": "nom", "number": "sg"},
            },
            {
                "pos": "noun",
                "lemma": "άνδρας",
                "word": {"άνδρας"},
                "translations": {"man"},
                "features": {"case": "nom", "number": "sg"},
            },
        ]

        response = await generate(request=request, service=mock_service)

        assert response.template == "(article)@{nom:sg} (noun)@$1"
        assert len(response.lexicals) == 2

    @pytest.mark.asyncio
    async def test_generate_endpoint_v2_multiple_groups(self, mock_service):
        """POST /generate should handle V2 multiple groups"""
        request = GenerateRequest(
            template="(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"
        )

        mock_service.generate_from_template.return_value = [
            {
                "pos": "article",
                "lemma": "ο",
                "word": {"ο"},
                "translations": {"the"},
                "features": {"case": "nom", "gender": "masc", "number": "sg"},
            },
            {
                "pos": "noun",
                "lemma": "άνδρας",
                "word": {"άνδρας"},
                "translations": {"man"},
                "features": {"case": "nom", "gender": "masc", "number": "sg"},
            },
            {
                "pos": "verb",
                "lemma": "βλέπω",
                "word": {"βλέπει"},
                "translations": {"sees"},
                "features": {
                    "tense": "present",
                    "voice": "active",
                    "person": "ter",
                    "number": "sg",
                },
            },
        ]

        response = await generate(request=request, service=mock_service)

        assert len(response.lexicals) == 3
        assert response.lexicals[0].lemma == "ο"
        assert response.lexicals[1].lemma == "άνδρας"
        assert response.lexicals[2].lemma == "βλέπω"

    @pytest.mark.asyncio
    async def test_generate_endpoint_v2_direct_features(self, mock_service):
        """POST /generate should handle V2 direct feature overrides"""
        request = GenerateRequest(template="(article noun{fem})@{nom:masc:sg}")

        mock_service.generate_from_template.return_value = [
            {
                "pos": "article",
                "lemma": "ο",
                "word": {"ο"},
                "translations": {"the"},
                "features": {"case": "nom", "gender": "masc", "number": "sg"},
            },
            {
                "pos": "noun",
                "lemma": "γυναίκα",
                "word": {"γυναίκα"},
                "translations": {"woman"},
                "features": {"case": "nom", "gender": "fem", "number": "sg"},
            },
        ]

        response = await generate(request=request, service=mock_service)

        assert len(response.lexicals) == 2
        assert response.lexicals[0].features["gender"] == "masc"
        assert response.lexicals[1].features["gender"] == "fem"

    @pytest.mark.asyncio
    async def test_generate_endpoint_v2_invalid_syntax(self, mock_service):
        """POST /generate should handle V2 syntax errors"""
        request = GenerateRequest(
            template="(noun@{nom:sg}"
        )  # Missing closing parenthesis

        # V2 parser raises ValueError with "Invalid" or "template" to trigger 400 response
        mock_service.generate_from_template.side_effect = ValueError(
            "Invalid template syntax: Unclosed group (mismatched parentheses)"
        )

        with pytest.raises(HTTPException) as exc_info:
            await generate(request=request, service=mock_service)

        assert exc_info.value.status_code == 400
        assert "Invalid template" in exc_info.value.detail


def test_get_lexical_schema(client):
    """Test GET /api/v1/lexicals/schema endpoint."""
    response = client.get("/api/v1/lexicals/schema")

    assert response.status_code == 200
    data = response.json()

    assert "lexicals" in data
    assert "noun" in data["lexicals"]
    assert "required" in data["lexicals"]["noun"]
    assert "case" in data["lexicals"]["noun"]["required"]
    assert "gender" in data["lexicals"]["noun"]["required"]
    assert "number" in data["lexicals"]["noun"]["required"]

    # Verify verb requirements
    assert "verb" in data["lexicals"]
    assert "tense" in data["lexicals"]["verb"]["required"]
    assert "voice" in data["lexicals"]["verb"]["required"]
    assert "person" in data["lexicals"]["verb"]["required"]

    # Verify pronoun requirements (type required, others optional)
    assert "pronoun" in data["lexicals"]
    assert "type" in data["lexicals"]["pronoun"]["required"]
    assert "optional" in data["lexicals"]["pronoun"]
    assert "case" in data["lexicals"]["pronoun"]["optional"]
    assert "person" in data["lexicals"]["pronoun"]["optional"]
    assert "number" in data["lexicals"]["pronoun"]["optional"]
    assert "gender" in data["lexicals"]["pronoun"]["optional"]

    # Verify invariable lexicals
    assert "adverb" in data["lexicals"]
    assert data["lexicals"]["adverb"]["required"] == []


def test_get_features(client):
    """Test GET /api/v1/features endpoint."""
    response = client.get("/api/v1/features")

    assert response.status_code == 200
    data = response.json()

    # Verify case features
    assert "case" in data
    assert "nom" in data["case"]
    assert "acc" in data["case"]
    assert "gen" in data["case"]
    assert "voc" in data["case"]

    # Verify gender features
    assert "gender" in data
    assert "masc" in data["gender"]
    assert "fem" in data["gender"]
    assert "neut" in data["gender"]

    # Verify number features
    assert "number" in data
    assert "sg" in data["number"]
    assert "pl" in data["number"]

    # Verify tense features
    assert "tense" in data
    assert "present" in data["tense"]
    assert "aorist" in data["tense"]
    assert "paratatikos" in data["tense"]

    # Verify voice features
    assert "voice" in data
    assert "active" in data["voice"]
    assert "passive" in data["voice"]

    # Verify person features
    assert "person" in data
    assert "pri" in data["person"]
    assert "sec" in data["person"]
    assert "ter" in data["person"]

    # Verify type features (for pronouns)
    assert "type" in data
    assert "personal_strong" in data["type"]
    assert "personal_weak" in data["type"]
    assert "demonstrative" in data["type"]
    assert "interrogative" in data["type"]
    assert "possessive" in data["type"]
    assert "relative" in data["type"]
    assert "indefinite" in data["type"]


def test_lexical_schema_and_features_consistency(client):
    """Test that schema required features match available features."""
    schema_response = client.get("/api/v1/lexicals/schema")
    features_response = client.get("/api/v1/features")

    schema = schema_response.json()["lexicals"]
    features = features_response.json()

    # Collect all required and optional feature categories
    all_categories = set()
    for lexical_info in schema.values():
        all_categories.update(lexical_info["required"])
        if "optional" in lexical_info:
            all_categories.update(lexical_info["optional"])

    # Verify all categories have feature definitions
    for category in all_categories:
        assert category in features, f"Category {category} required/optional but not in features"
        assert len(features[category]) > 0, f"Category {category} has no values"


def test_invalid_feature_combination_returns_error(client):
    """Test that invalid feature combinations return clear error message."""
    # personal_weak pronouns don't exist in nominative case
    response = client.post(
        "/api/v1/generate",
        json={"template": "(pronoun)@{personal_weak:nom:ter:pl:masc}"}
    )

    assert response.status_code == 400
    data = response.json()
    assert "No pronoun found matching features" in data["detail"]
    assert "personal_weak" in data["detail"] or "nom" in data["detail"]
