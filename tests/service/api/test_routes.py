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
    """Generate endpoint returns 500 when no words match."""
    request = GenerateRequest(template="[noun:nom:masc:sg]")

    # Simulate no matching words
    mock_service.generate_from_template.side_effect = ValueError("No words found")

    with pytest.raises(ValueError) as exc_info:
        await generate(request=request, service=mock_service)


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
