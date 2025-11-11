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
