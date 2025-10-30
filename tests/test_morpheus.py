import pytest

from syntaxis.models.enums import PartOfSpeech as POSEnum
from syntaxis.models.part_of_speech import Adjective, Article, Noun, Verb
from syntaxis.morpheus import Morpheus


def test_morpheus_create_returns_noun_for_noun_pos():
    """create() with NOUN pos should return Noun instance."""
    result = Morpheus.create("άνθρωπος", POSEnum.NOUN)
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"


def test_morpheus_create_returns_verb_for_verb_pos():
    """create() with VERB pos should return Verb instance."""
    result = Morpheus.create("τρώω", POSEnum.VERB)
    assert isinstance(result, Verb)
    assert result.lemma == "τρώω"


def test_morpheus_create_returns_adjective_for_adjective_pos():
    """create() with ADJECTIVE pos should return Adjective instance."""
    result = Morpheus.create("καλός", POSEnum.ADJECTIVE)
    assert isinstance(result, Adjective)
    assert result.lemma == "καλός"


def test_morpheus_create_returns_article_for_article_pos():
    """create() with ARTICLE pos should return Article instance."""
    result = Morpheus.create("ο", POSEnum.ARTICLE)
    assert isinstance(result, Article)
    assert result.lemma == "ο"


def test_morpheus_create_populates_forms():
    """create() should populate forms dictionary."""
    result = Morpheus.create("άνθρωπος", POSEnum.NOUN)
    assert result.forms is not None
    assert len(result.forms) > 0
