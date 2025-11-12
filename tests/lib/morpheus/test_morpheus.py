from syntaxis.lib import constants as c
from syntaxis.lib.models.lexical import Adjective, Article, Noun, Verb
from syntaxis.lib.morpheus import Morpheus


def test_morpheus_create_returns_noun_for_noun_lexical():
    """create() with NOUN lexical should return Noun instance."""
    result = Morpheus.create("άνθρωπος", c.NOUN)
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"


def test_morpheus_create_returns_verb_for_verb_lexical():
    """create() with VERB lexical should return Verb instance."""
    result = Morpheus.create("τρώω", c.VERB)
    assert isinstance(result, Verb)
    assert result.lemma == "τρώω"


def test_morpheus_create_returns_adjective_for_adjective_lexical():
    """create() with ADJECTIVE lexical should return Adjective instance."""
    result = Morpheus.create("καλός", c.ADJECTIVE)
    assert isinstance(result, Adjective)
    assert result.lemma == "καλός"


def test_morpheus_create_returns_article_for_article_lexical():
    """create() with ARTICLE lexical should return Article instance."""
    result = Morpheus.create("ο", c.ARTICLE)
    assert isinstance(result, Article)
    assert result.lemma == "ο"


def test_morpheus_create_populates_forms():
    """create() should populate forms dictionary."""
    result = Morpheus.create("άνθρωπος", c.NOUN)
    assert result.forms is not None
    assert len(result.forms) > 0
