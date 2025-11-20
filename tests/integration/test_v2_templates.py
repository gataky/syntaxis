# tests/integration/test_v2_templates.py
import pytest

from syntaxis.lib import constants as c
from syntaxis.lib.database import seeds
from syntaxis.lib.database.api import Database
from syntaxis.lib.syntaxis import Syntaxis


@pytest.fixture
def syntaxis_instance():
    """Create Syntaxis instance with test database"""
    # Create in-memory database
    db = Database()

    # Add sample nouns (masc, fem, neut for wildcard testing)
    db.add_word(lemma="άνθρωπος", translations=["person"], lexical=c.NOUN)
    db.add_word(lemma="γυναίκα", translations=["woman"], lexical=c.NOUN)
    db.add_word(lemma="παιδί", translations=["child"], lexical=c.NOUN)

    # Add sample verbs
    db.add_word(lemma="βλέπω", translations=["see"], lexical=c.VERB)

    # Add sample adjectives
    db.add_word(lemma="μεγάλος", translations=["big"], lexical=c.ADJECTIVE)

    # Add sample articles
    seeds.articles.seed(db._conn)

    # Add sample pronouns
    seeds.pronouns.seed(db._conn)

    # Create Syntaxis instance and replace database
    sx = Syntaxis()
    sx.database = db

    return sx


class TestV2BasicGrouping:
    def test_single_group_generates_words(self, syntaxis_instance):
        """V2: (article adj noun)@{nom:masc:sg} should generate 3 words"""
        template = "(article adj noun)@{nom:masc:sg}"
        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 3
        # Check the types of the returned objects
        from syntaxis.lib.models.lexical import Adjective, Article, Noun

        assert isinstance(result[0], Article)
        assert isinstance(result[1], Adjective)
        assert isinstance(result[2], Noun)

    def test_multiple_groups_generates_words(self, syntaxis_instance):
        """V2: Multiple groups should each generate their words"""
        template = "(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"
        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 3
        from syntaxis.lib.models.lexical import Verb

        assert isinstance(result[2], Verb)


class TestV2References:
    def test_reference_inherits_features(self, syntaxis_instance):
        """V2: Group with @$1 should inherit features from group 1"""
        template = "(article)@{nom:masc:sg} (noun)@$1"
        result = syntaxis_instance.generate_sentence(template)

        # Both should have same features
        assert result[0].case == result[1].case
        assert result[0].gender == result[1].gender
        assert result[0].number == result[1].number


class TestV2DirectFeatures:
    def test_direct_feature_override(self, syntaxis_instance):
        """V2: Direct features should override group features"""
        template = "(article noun{fem})@{nom:masc:sg}"
        result = syntaxis_instance.generate_sentence(template)

        # Article has masc (from group)
        assert result[0].gender == "masc"

        # Noun has fem (direct override)
        assert result[1].gender == "fem"


class TestV1V2Equivalence:
    def test_v1_v2_same_output_structure(self, syntaxis_instance):
        """V1 and V2 should produce equivalent structures"""
        # V1 uses full feature names like "present", "active"
        v1 = "[noun:nom:masc:sg] [verb:present:active:ter:sg]"
        # V2 uses abbreviated feature names like "pres", "act"
        v2 = "(noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"

        result_v1 = syntaxis_instance.generate_sentence(v1)
        result_v2 = syntaxis_instance.generate_sentence(v2)

        assert len(result_v1) == len(result_v2)
        # Both should return same types
        assert type(result_v1[0]) == type(result_v2[0])
        assert type(result_v1[1]) == type(result_v2[1])


class TestV2WildcardTemplates:
    """Integration tests for wildcard template functionality."""

    def test_gender_wildcard_generates_sentence(self, syntaxis_instance):
        """V2: Template with gender wildcard should generate successfully"""
        template = "(article noun)@{nom:gender*:sg}"

        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 2
        from syntaxis.lib.models.lexical import Article, Noun

        assert isinstance(result[0], Article)
        assert isinstance(result[1], Noun)

    def test_number_wildcard_generates_sentence(self, syntaxis_instance):
        """V2: Template with number wildcard should generate successfully"""
        template = "(article noun)@{nom:masc:number*}"

        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 2

    def test_both_wildcards_generates_sentence(self, syntaxis_instance):
        """V2: Template with both gender and number wildcards should generate"""
        template = "(article noun)@{nom:gender*:number*}"

        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 2

    def test_wildcard_variety_across_generations(self, syntaxis_instance):
        """V2: Multiple generations should produce varied results (probabilistic test)"""
        template = "(noun)@{nom:gender*:sg}"

        # Generate multiple times and collect genders
        results = []
        for _ in range(20):
            result = syntaxis_instance.generate_sentence(template)
            # Check the gender by examining the lemma (άνθρωπος is masc, γυναίκα is fem)
            lemma = result[0].lemma
            results.append(lemma)

        # With 20 generations, we should see at least some variety
        # (This could fail by chance but is very unlikely)
        unique_lemmas = set(results)
        assert len(unique_lemmas) > 1, "Expected variety in wildcard generations"
