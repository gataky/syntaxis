from unittest.mock import Mock

import pytest

from syntaxis.lib.syntaxis import Syntaxis
from syntaxis.lib.models.lexical import Noun
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
