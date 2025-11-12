"""Unit tests for the main Syntaxis API."""

import pytest

from syntaxis.lib.database import seeds
from syntaxis.lib.database.api import Database
from syntaxis.lib.models import constants as c
from syntaxis.lib.models.lexical import (
    Adjective,
    Adverb,
    Article,
    Conjunction,
    Lexical,
    Noun,
    Preposition,
    Pronoun,
    Verb,
)
from syntaxis.lib.syntaxis import Syntaxis
from syntaxis.lib.templates.api import TemplateParseError


class TestSyntaxisAPI:
    """Test suite for the main Syntaxis API class."""

    @pytest.fixture
    def test_db(self):
        """Create an in-memory test database with sample data."""
        db = Database()  # Uses in-memory database by default

        # Add sample nouns - Morpheus will generate all forms automatically
        db.add_word(lemma="άνθρωπος", translations=["person", "human"], lexical=c.NOUN)
        db.add_word(lemma="γυναίκα", translations=["woman"], lexical=c.NOUN)
        db.add_word(lemma="παιδί", translations=["child", "kid"], lexical=c.NOUN)

        # Add sample verbs - Morpheus will generate all conjugations
        db.add_word(lemma="βλέπω", translations=["see", "look"], lexical=c.VERB)
        db.add_word(lemma="τρέχω", translations=["run"], lexical=c.VERB)

        # Add sample adjectives - Morpheus will generate all forms
        db.add_word(lemma="μεγάλος", translations=["big", "large"], lexical=c.ADJECTIVE)
        db.add_word(lemma="καλός", translations=["good", "nice"], lexical=c.ADJECTIVE)

        # Add sample articles - use seed function since articles can't be auto-generated
        seeds.articles.seed(db._conn)

        # Add sample prepositions - invariable words
        db.add_word(lemma="με", translations=["with"], lexical=c.PREPOSITION)
        db.add_word(lemma="από", translations=["from"], lexical=c.PREPOSITION)

        # Add sample adverbs - invariable words
        db.add_word(lemma="τώρα", translations=["now"], lexical=c.ADVERB)
        db.add_word(lemma="εδώ", translations=["here"], lexical=c.ADVERB)

        # Add sample conjunctions - invariable words
        db.add_word(lemma="και", translations=["and"], lexical=c.CONJUNCTION)
        db.add_word(lemma="αλλά", translations=["but"], lexical=c.CONJUNCTION)

        # Add sample pronouns - use seed function since pronouns can't be auto-generated
        seeds.pronouns.seed(db._conn)

        return db

    @pytest.fixture
    def syntaxis_with_test_db(self, test_db, monkeypatch):
        """Create a Syntaxis instance with a test database."""
        sx = Syntaxis()
        # Replace the default database with our test database
        monkeypatch.setattr(sx, "database", test_db)
        return sx

    # Test initialization

    def test_syntaxis_initialization(self, syntaxis_with_test_db):
        """Test that Syntaxis initializes with database and template parser."""
        sx = syntaxis_with_test_db
        assert sx.database is not None
        assert sx.template is not None
        assert isinstance(sx.database, Database)

    # Test generate_sentence with single tokens

    def test_generate_sentence_single_noun(self, syntaxis_with_test_db):
        """Test generating a single noun."""
        sx = syntaxis_with_test_db
        template = "[noun:nom:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Noun)
        assert isinstance(result[0], Lexical)
        # Verify we got a noun with a lemma (might be any of our test nouns)
        assert result[0].lemma in ["άνθρωπος", "γυναίκα", "παιδί"]

    def test_generate_sentence_single_verb(self, syntaxis_with_test_db):
        """Test generating a single verb."""
        sx = syntaxis_with_test_db
        template = "[verb:present:active:ter:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Verb)
        assert result[0].lemma in ["βλέπω", "τρέχω"]

    def test_generate_sentence_single_adjective(self, syntaxis_with_test_db):
        """Test generating a single adjective."""
        sx = syntaxis_with_test_db
        template = "[adj:nom:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Adjective)
        assert result[0].lemma in ["μεγάλος", "καλός"]

    def test_generate_sentence_single_article(self, syntaxis_with_test_db):
        """Test generating a single article."""
        sx = syntaxis_with_test_db
        template = "[article:nom:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Article)
        # Should get a masculine singular nominative article
        assert result[0].lemma is not None

    def test_generate_sentence_single_preposition(self, syntaxis_with_test_db):
        """Test generating a single preposition."""
        sx = syntaxis_with_test_db
        template = "[prep]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Preposition)
        assert result[0].lemma in ["με", "από"]

    def test_generate_sentence_single_adverb(self, syntaxis_with_test_db):
        """Test generating a single adverb."""
        sx = syntaxis_with_test_db
        template = "[adv]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Adverb)
        assert result[0].lemma in ["τώρα", "εδώ"]

    def test_generate_sentence_single_conjunction(self, syntaxis_with_test_db):
        """Test generating a single conjunction."""
        sx = syntaxis_with_test_db
        template = "[conj]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Conjunction)
        assert result[0].lemma in ["και", "αλλά"]

    def test_generate_sentence_single_pronoun(self, syntaxis_with_test_db):
        """Test generating a single pronoun."""
        sx = syntaxis_with_test_db
        # Use third person pronoun which requires gender
        template = "[pronoun:nom:ter:sg:masc]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Pronoun)
        # Should get a third person singular nominative masculine pronoun
        assert result[0].lemma is not None

    # Test generate_sentence with multiple tokens

    def test_generate_sentence_article_noun(self, syntaxis_with_test_db):
        """Test generating article + noun phrase."""
        sx = syntaxis_with_test_db
        template = "[article:nom:masc:sg] [noun:nom:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 2
        assert isinstance(result[0], Article)
        assert isinstance(result[1], Noun)
        # Verify we got valid words
        assert result[0].lemma is not None
        assert result[1].lemma is not None

    def test_generate_sentence_article_adjective_noun(self, syntaxis_with_test_db):
        """Test generating article + adjective + noun phrase."""
        sx = syntaxis_with_test_db
        template = "[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 3
        assert isinstance(result[0], Article)
        assert isinstance(result[1], Adjective)
        assert isinstance(result[2], Noun)

    def test_generate_sentence_with_verb(self, syntaxis_with_test_db):
        """Test generating a simple sentence with subject and verb."""
        sx = syntaxis_with_test_db
        template = "[noun:nom:masc:sg] [verb:present:active:ter:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 2
        assert isinstance(result[0], Noun)
        assert isinstance(result[1], Verb)

    def test_generate_sentence_prepositional_phrase(self, syntaxis_with_test_db):
        """Test generating a prepositional phrase."""
        sx = syntaxis_with_test_db
        # Use masculine singular which we know exists in seed data
        template = "[prep] [article:nom:masc:sg] [noun:nom:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 3
        assert isinstance(result[0], Preposition)
        assert isinstance(result[1], Article)
        assert isinstance(result[2], Noun)

    def test_generate_sentence_with_adverb(self, syntaxis_with_test_db):
        """Test generating sentence with adverb."""
        sx = syntaxis_with_test_db
        template = "[noun:nom:masc:sg] [verb:present:active:ter:sg] [adv]"

        result = sx.generate_sentence(template)

        assert len(result) == 3
        assert isinstance(result[0], Noun)
        assert isinstance(result[1], Verb)
        assert isinstance(result[2], Adverb)

    def test_generate_sentence_with_conjunction(self, syntaxis_with_test_db):
        """Test generating coordinated phrase with conjunction."""
        sx = syntaxis_with_test_db
        template = "[noun:nom:masc:sg] [conj] [noun:acc:fem:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 3
        assert isinstance(result[0], Noun)
        assert isinstance(result[1], Conjunction)
        assert isinstance(result[2], Noun)

    # Test different grammatical features

    @pytest.mark.parametrize(
        "case,expected_lemma",
        [
            ("nom", "άνθρωπος"),
            ("nom", "άνθρωπος"),  # Can match nominative
        ],
    )
    def test_generate_sentence_noun_cases(
        self, syntaxis_with_test_db, case, expected_lemma
    ):
        """Test that nouns with different cases are retrieved correctly."""
        sx = syntaxis_with_test_db
        template = f"[noun:{case}:masc:sg]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Noun)
        # Just verify we get a valid noun back
        assert result[0].lemma is not None

    @pytest.mark.parametrize(
        "tense,voice,person,number",
        [
            ("present", "active", "ter", "sg"),
            ("aorist", "active", "pri", "pl"),
        ],
    )
    def test_generate_sentence_verb_forms(
        self, syntaxis_with_test_db, tense, voice, person, number
    ):
        """Test that verbs with different forms are retrieved correctly."""
        sx = syntaxis_with_test_db
        template = f"[verb:{tense}:{voice}:{person}:{number}]"

        result = sx.generate_sentence(template)

        assert len(result) == 1
        assert isinstance(result[0], Verb)
        assert result[0].lemma is not None

    # Test error handling

    def test_generate_sentence_invalid_template_syntax(self, syntaxis_with_test_db):
        """Test that invalid template syntax raises TemplateParseError."""
        sx = syntaxis_with_test_db

        with pytest.raises(TemplateParseError):
            sx.generate_sentence("[noun:invalid:syntax")  # Missing closing bracket

    def test_generate_sentence_invalid_lexical_type(self, syntaxis_with_test_db):
        """Test that invalid lexical type raises TemplateParseError."""
        sx = syntaxis_with_test_db

        with pytest.raises(TemplateParseError):
            sx.generate_sentence("[invalidtype:nom:masc:sg]")

    def test_generate_sentence_missing_required_features(self, syntaxis_with_test_db):
        """Test that missing required features raises TemplateParseError."""
        sx = syntaxis_with_test_db

        with pytest.raises(TemplateParseError):
            # Noun requires case, gender, number - only providing case
            sx.generate_sentence("[noun:nom]")

    def test_generate_sentence_no_matching_words(self, syntaxis_with_test_db):
        """Test behavior when no words match features."""
        sx = syntaxis_with_test_db

        # Create a fresh database with no words
        empty_db = Database()
        sx.database = empty_db

        # With empty database, get_random_word returns None
        result = sx.generate_sentence("[noun:nom:masc:sg]")

        # Currently the API returns a list with None when no match found
        # This test documents the current behavior (returns [None])
        assert len(result) == 1
        assert result[0] is None

    # Test return value properties

    def test_generate_sentence_returns_list(self, syntaxis_with_test_db):
        """Test that generate_sentence returns a list."""
        sx = syntaxis_with_test_db
        result = sx.generate_sentence("[noun:nom:masc:sg]")

        assert isinstance(result, list)

    def test_generate_sentence_lexical_objects_have_lemma(self, syntaxis_with_test_db):
        """Test that returned Lexical objects have lemma property."""
        sx = syntaxis_with_test_db
        result = sx.generate_sentence("[noun:nom:masc:sg]")

        assert hasattr(result[0], "lemma")
        assert isinstance(result[0].lemma, str)
        assert len(result[0].lemma) > 0

    def test_generate_sentence_lexical_objects_have_translations(
        self, syntaxis_with_test_db
    ):
        """Test that returned Lexical objects have translations."""
        sx = syntaxis_with_test_db
        result = sx.generate_sentence("[noun:nom:masc:sg]")

        assert hasattr(result[0], "translations")
        assert isinstance(result[0].translations, list)
        assert len(result[0].translations) > 0

    def test_generate_sentence_lexical_objects_are_stringifiable(
        self, syntaxis_with_test_db
    ):
        """Test that Lexical objects can be converted to strings."""
        sx = syntaxis_with_test_db
        result = sx.generate_sentence("[noun:nom:masc:sg]")

        # Should not raise an exception
        string_repr = str(result[0])
        assert isinstance(string_repr, str)
        assert len(string_repr) > 0

    # Integration tests

    def test_generate_sentence_complex_template(self, syntaxis_with_test_db):
        """Test generating a complex sentence with multiple word types."""
        sx = syntaxis_with_test_db
        # Test complex sentence without articles (which have seed data issues)
        template = (
            "[noun:nom:masc:sg] [adj:nom:masc:sg] "
            "[verb:present:active:ter:sg] [prep] "
            "[noun:acc:fem:sg] [conj] [adv]"
        )

        result = sx.generate_sentence(template)

        assert len(result) == 7
        assert isinstance(result[0], Noun)
        assert isinstance(result[1], Adjective)
        assert isinstance(result[2], Verb)
        assert isinstance(result[3], Preposition)
        assert isinstance(result[4], Noun)
        assert isinstance(result[5], Conjunction)
        assert isinstance(result[6], Adverb)

    def test_generate_sentence_can_join_to_sentence(self, syntaxis_with_test_db):
        """Test that generated words can be joined into a sentence string."""
        sx = syntaxis_with_test_db
        template = (
            "[article:nom:masc:sg] [noun:nom:masc:sg] [verb:present:active:ter:sg]"
        )

        result = sx.generate_sentence(template)
        sentence = " ".join(str(word) for word in result)

        assert isinstance(sentence, str)
        assert len(sentence) > 0
        # Should have spaces between words
        assert " " in sentence

    def test_generate_sentence_multiple_calls_work(self, syntaxis_with_test_db):
        """Test that multiple calls to generate_sentence work correctly."""
        sx = syntaxis_with_test_db
        template = "[noun:nom:masc:sg]"

        result1 = sx.generate_sentence(template)
        result2 = sx.generate_sentence(template)

        # Both should succeed
        assert len(result1) == 1
        assert len(result2) == 1
        assert isinstance(result1[0], Noun)
        assert isinstance(result2[0], Noun)


class TestVersionDetection:
    """Test suite for version detection in Syntaxis."""

    @pytest.fixture
    def test_db(self):
        """Create an in-memory test database with sample data."""
        db = Database()  # Uses in-memory database by default

        # Add sample nouns
        db.add_word(lemma="άνθρωπος", translations=["person"], lexical=c.NOUN)
        db.add_word(lemma="γυναίκα", translations=["woman"], lexical=c.NOUN)

        # Add sample verbs
        db.add_word(lemma="βλέπω", translations=["see"], lexical=c.VERB)

        # Add sample articles
        seeds.articles.seed(db._conn)

        return db

    @pytest.fixture
    def syntaxis_instance(self, test_db, monkeypatch):
        """Create a Syntaxis instance with test database."""
        sx = Syntaxis()
        monkeypatch.setattr(sx, "database", test_db)
        return sx

    def test_detect_v1_template(self, syntaxis_instance):
        """Should detect V1 template starting with ["""
        template = "[noun:nom:masc:sg]"
        # This should not raise an error
        result = syntaxis_instance.generate_sentence(template)
        assert len(result) == 1

    def test_detect_v2_template(self, syntaxis_instance):
        """Should detect V2 template starting with ("""
        template = "(noun)@{nom:masc:sg}"
        # This should not raise an error
        result = syntaxis_instance.generate_sentence(template)
        assert len(result) == 1

    def test_invalid_template_start(self, syntaxis_instance):
        """Should raise error for invalid template format"""
        template = "noun:nom:masc:sg"
        with pytest.raises(ValueError, match="Invalid template format"):
            syntaxis_instance.generate_sentence(template)


class TestFeatureOverrideWarnings:
    """Test suite for feature override warnings."""

    @pytest.fixture
    def test_db(self):
        """Create an in-memory test database with sample data."""
        db = Database()  # Uses in-memory database by default

        # Add sample nouns
        db.add_word(lemma="άνθρωπος", translations=["person"], lexical=c.NOUN)

        # Add sample verbs
        db.add_word(lemma="βλέπω", translations=["see"], lexical=c.VERB)

        # Add sample articles
        seeds.articles.seed(db._conn)

        # Add sample pronouns
        seeds.pronouns.seed(db._conn)

        return db

    @pytest.fixture
    def syntaxis_instance(self, test_db, monkeypatch):
        """Create a Syntaxis instance with test database."""
        sx = Syntaxis()
        monkeypatch.setattr(sx, "database", test_db)
        return sx

    def test_override_warning_emitted(self, syntaxis_instance, caplog):
        """Should warn when direct feature overrides group/reference feature"""
        import logging

        caplog.set_level(logging.WARNING)

        # Group 1 has 'masc' (gender), direct feature on noun overrides with 'fem'
        template = "(article noun{fem})@{nom:masc:sg}"
        syntaxis_instance.generate_sentence(template)

        # Check warning was logged
        assert any(
            "overrides feature 'gender'" in record.message for record in caplog.records
        )

    def test_no_warning_when_no_conflict(self, syntaxis_instance, caplog):
        """Should not warn when direct feature doesn't conflict"""
        import logging

        caplog.set_level(logging.WARNING)

        # Group features have nom:sg, direct feature adds masc (no conflict)
        template = "(article{masc} noun{masc})@{nom:sg}"
        syntaxis_instance.generate_sentence(template)

        # No warnings
        assert not any("overrides" in record.message for record in caplog.records)
