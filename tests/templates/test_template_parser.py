"""Unit tests for template parser."""

import pytest

from syntaxis.models import constants as c
from syntaxis.templates.api import (
    Template,
    TemplateParseError,
)


class TestTemplateParser:
    """Test suite for TemplateParser class."""

    @pytest.fixture
    def parser(self):
        """Create a TemplateParser instance for testing."""
        return Template()

    # Valid template tests

    @pytest.mark.parametrize(
        "template,expected_pos,expected_form,expected_gender,expected_number",
        [
            (
                "[noun:nom:masc:sg]",
                c.NOUN,
                c.NOMINATIVE,
                c.MASCULINE,
                c.SINGULAR,
            ),
            (
                "[article:acc:fem:pl]",
                c.ARTICLE,
                c.ACCUSATIVE,
                c.FEMININE,
                c.PLURAL,
            ),
            (
                "[adj:gen:neut:sg]",
                c.ADJECTIVE,
                c.GENITIVE,
                c.NEUTER,
                c.SINGULAR,
            ),
        ],
    )
    def test_parse_nominal_tokens(
        self,
        parser,
        template,
        expected_pos,
        expected_form,
        expected_gender,
        expected_number,
    ):
        """Test parsing nominal tokens (nouns, articles, adjectives)."""
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == expected_pos
        assert token.form == expected_form
        assert token.gender == expected_gender
        assert token.number == expected_number

    def test_parse_simple_verb(self, parser):
        """Test parsing a simple verb token."""
        template = "[verb:present:active:ter:pl]"
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == c.VERB
        assert token.tense == c.PRESENT
        assert token.voice == c.ACTIVE
        assert token.person == c.THIRD
        assert token.number == c.PLURAL

    @pytest.mark.parametrize(
        "template,expected_pos",
        [
            ("[prep]", c.PREPOSITION),
            ("[adv]", c.ADVERB),
            ("[conj]", c.CONJUNCTION),
        ],
    )
    def test_parse_invariable_words(self, parser, template, expected_pos):
        """Test parsing invariable words."""
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == expected_pos
        assert token.is_invariable()
        assert token.form is None
        assert token.gender is None
        assert token.number is None

    def test_parse_complex_template(self, parser):
        """Test parsing a template with multiple tokens."""
        template = "[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg] [verb:aorist:active:ter:sg]"
        result = parser.parse(template)

        assert len(result.tokens) == 4
        assert result.tokens[0].pos == c.ARTICLE
        assert result.tokens[1].pos == c.ADJECTIVE
        assert result.tokens[2].pos == c.NOUN
        assert result.tokens[3].pos == c.VERB

    def test_parse_prd_example_template(self, parser):
        """Test parsing the example from the PRD."""
        template = "[article:nom:neut:pl] [adj:nom:neut:pl] [noun:nom:neut:pl] [verb:present:active:ter:pl] [adv]"
        result = parser.parse(template)

        assert len(result.tokens) == 5
        # Verify neuter plural nominative agreement
        assert result.tokens[0].gender == c.NEUTER
        assert result.tokens[0].number == c.PLURAL
        assert result.tokens[1].gender == c.NEUTER
        assert result.tokens[1].number == c.PLURAL
        assert result.tokens[2].gender == c.NEUTER
        assert result.tokens[2].number == c.PLURAL
        # Verify verb
        assert result.tokens[3].tense == c.PRESENT
        assert result.tokens[3].number == c.PLURAL
        # Verify adverb
        assert result.tokens[4].is_invariable()

    def test_parse_features_in_different_order(self, parser):
        """Test that feature order doesn't matter for nominals."""
        template1 = "[noun:nom:masc:sg]"
        template2 = "[noun:sg:nom:masc]"
        template3 = "[noun:masc:sg:nom]"

        result1 = parser.parse(template1)
        result2 = parser.parse(template2)
        result3 = parser.parse(template3)

        # All should parse to the same token features
        for result in [result1, result2, result3]:
            token = result.tokens[0]
            assert token.form == c.NOMINATIVE
            assert token.gender == c.MASCULINE
            assert token.number == c.SINGULAR

    def test_parse_verb_features_different_order(self, parser):
        """Test that feature order doesn't matter for verbs."""
        template1 = "[verb:present:active:ter:pl]"
        template2 = "[verb:pl:ter:active:present]"
        template3 = "[verb:active:pl:present:ter]"

        result1 = parser.parse(template1)
        result2 = parser.parse(template2)
        result3 = parser.parse(template3)

        # All should parse to the same token features
        for result in [result1, result2, result3]:
            token = result.tokens[0]
            assert token.tense == c.PRESENT
            assert token.voice == c.ACTIVE
            assert token.person == c.THIRD
            assert token.number == c.PLURAL

    # Error handling tests

    @pytest.mark.parametrize(
        "template,error_match",
        [
            ("", "cannot be empty"),
            ("   ", "cannot be empty"),
            ("just some text without brackets", "No valid tokens found"),
            ("[InvalidPOS:nom:masc:sg]", "Unknown part of speech"),
            ("[noun:nom:masc]", "requires exactly 3 features"),
            ("[noun:nom:masc:sg:extra]", "requires exactly 3 features"),
            ("[verb:present:active:3]", "requires exactly 4 features"),
            ("[verb:present:active:ter:pl:extra]", "requires exactly 4 features"),
            ("[noun:invalid:masc:sg]", "Invalid or duplicate feature"),
            ("[noun:nom:invalid:sg]", "Invalid or duplicate feature"),
            ("[noun:nom:masc:invalid]", "Invalid or duplicate feature"),
            ("[verb:invalid:active:ter:pl]", "Invalid or duplicate feature"),
            ("[noun:nom:nom:masc]", "Invalid or duplicate feature"),
            ("[adv:nom:masc:sg]", "should not have features"),
        ],
    )
    def test_parse_errors(self, parser, template, error_match):
        """Test various parsing error conditions."""
        with pytest.raises(TemplateParseError, match=error_match):
            parser.parse(template)

    @pytest.mark.parametrize(
        "form", [c.NOMINATIVE, c.ACCUSATIVE, c.GENITIVE, c.VOCATIVE]
    )
    def test_all_forms_valid(self, parser, form):
        """Test that all form values are recognized."""
        template = f"[noun:{form}:masc:sg]"
        result = parser.parse(template)
        assert result.tokens[0].form == form

    @pytest.mark.parametrize("gender", [c.MASCULINE, c.FEMININE, c.NEUTER])
    def test_all_genders_valid(self, parser, gender):
        """Test that all gender values are recognized."""
        template = f"[noun:nom:{gender}:sg]"
        result = parser.parse(template)
        assert result.tokens[0].gender == gender

    @pytest.mark.parametrize("number", [c.SINGULAR, c.PLURAL])
    def test_all_numbers_valid(self, parser, number):
        """Test that all number values are recognized."""
        template = f"[noun:nom:masc:{number}]"
        result = parser.parse(template)
        assert result.tokens[0].number == number

    @pytest.mark.parametrize("tense", [c.PRESENT, c.AORIST, c.PARATATIKOS])
    def test_all_tenses_valid(self, parser, tense):
        """Test that all tense values are recognized."""
        template = f"[verb:{tense}:active:ter:sg]"
        result = parser.parse(template)
        assert result.tokens[0].tense == tense

    @pytest.mark.parametrize("voice", [c.ACTIVE, c.PASSIVE])
    def test_all_voices_valid(self, parser, voice):
        """Test that all voice values are recognized."""
        template = f"[verb:present:{voice}:ter:sg]"
        result = parser.parse(template)
        assert result.tokens[0].voice == voice

    @pytest.mark.parametrize("person", [c.FIRST, c.SECOND, c.THIRD])
    def test_all_persons_valid(self, parser, person):
        """Test that all person values are recognized."""
        template = f"[verb:present:active:{person}:sg]"
        result = parser.parse(template)
        assert result.tokens[0].person == person

    def test_parsed_template_iteration(self, parser):
        """Test that ParsedTemplate supports iteration."""
        template = "[noun:nom:masc:sg] [verb:present:active:ter:sg]"
        result = parser.parse(template)

        tokens = list(result)
        assert len(tokens) == 2
        assert tokens[0].pos == c.NOUN
        assert tokens[1].pos == c.VERB

    def test_parsed_template_length(self, parser):
        """Test that ParsedTemplate supports len()."""
        template = "[noun:nom:masc:sg] [verb:present:active:ter:sg] [adv]"
        result = parser.parse(template)

        assert len(result) == 3

    def test_raw_template_preserved(self, parser):
        """Test that raw template string is preserved."""
        template = "[article:nom:neut:pl] [noun:nom:neut:pl]"
        result = parser.parse(template)

        assert result.raw_template == template

    # Pronoun template parsing tests

    @pytest.mark.parametrize(
        "template,expected_form,expected_person,expected_number,expected_gender",
        [
            # First person (no gender)
            (
                "[pronoun:nom:pri:sg]",
                c.NOMINATIVE,
                c.FIRST,
                c.SINGULAR,
                None,
            ),
            ("[pronoun:acc:pri:pl]", c.ACCUSATIVE, c.FIRST, c.PLURAL, None),
            ("[pronoun:gen:pri:sg]", c.GENITIVE, c.FIRST, c.SINGULAR, None),
            # Second person (no gender)
            (
                "[pronoun:nom:sec:sg]",
                c.NOMINATIVE,
                c.SECOND,
                c.SINGULAR,
                None,
            ),
            ("[pronoun:acc:sec:pl]", c.ACCUSATIVE, c.SECOND, c.PLURAL, None),
            # Third person with gender
            (
                "[pronoun:nom:ter:sg:masc]",
                c.NOMINATIVE,
                c.THIRD,
                c.SINGULAR,
                c.MASCULINE,
            ),
            (
                "[pronoun:gen:ter:sg:fem]",
                c.GENITIVE,
                c.THIRD,
                c.SINGULAR,
                c.FEMININE,
            ),
            (
                "[pronoun:acc:ter:pl:neut]",
                c.ACCUSATIVE,
                c.THIRD,
                c.PLURAL,
                c.NEUTER,
            ),
            (
                "[pronoun:voc:ter:sg:masc]",
                c.VOCATIVE,
                c.THIRD,
                c.SINGULAR,
                c.MASCULINE,
            ),
        ],
    )
    def test_parse_pronoun_valid_forms(
        self,
        parser,
        template,
        expected_form,
        expected_person,
        expected_number,
        expected_gender,
    ):
        """Test parsing various valid pronoun forms."""
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == c.PRONOUN
        assert token.form == expected_form
        assert token.person == expected_person
        assert token.number == expected_number
        assert token.gender == expected_gender

    @pytest.mark.parametrize(
        "form", [c.NOMINATIVE, c.ACCUSATIVE, c.GENITIVE, c.VOCATIVE]
    )
    def test_parse_pronoun_all_forms(self, parser, form):
        """Test that all forms work with pronouns."""
        template = f"[pronoun:{form}:pri:sg]"
        result = parser.parse(template)
        assert result.tokens[0].form == form
        assert result.tokens[0].person == c.FIRST
        assert result.tokens[0].number == c.SINGULAR

    @pytest.mark.parametrize("person", [c.FIRST, c.SECOND, c.THIRD])
    def test_parse_pronoun_all_persons(self, parser, person):
        """Test that all persons work with pronouns."""
        # Third person needs gender, others don't
        if person == c.THIRD:
            template = f"[pronoun:nom:{person}:sg:masc]"
        else:
            template = f"[pronoun:nom:{person}:sg]"
        result = parser.parse(template)
        assert result.tokens[0].person == person

    def test_parse_pronoun_subject_verb_template(self, parser):
        """Test parsing a template with pronoun subject and verb."""
        template = "[pronoun:nom:pri:sg] [verb:present:active:pri:sg]"
        result = parser.parse(template)

        assert len(result.tokens) == 2
        assert result.tokens[0].pos == c.PRONOUN
        assert result.tokens[0].person == c.FIRST
        assert result.tokens[1].pos == c.VERB
        assert result.tokens[1].person == c.FIRST

    def test_parse_complex_template_with_pronoun(self, parser):
        """Test parsing a complex template including pronouns."""
        template = "[pronoun:nom:ter:sg:masc] [verb:aorist:active:ter:sg] [article:acc:neut:sg] [noun:acc:neut:sg]"
        result = parser.parse(template)

        assert len(result.tokens) == 4
        assert result.tokens[0].pos == c.PRONOUN
        assert result.tokens[0].person == c.THIRD
        assert result.tokens[0].gender == c.MASCULINE
        assert result.tokens[1].pos == c.VERB
        assert result.tokens[2].pos == c.ARTICLE
        assert result.tokens[3].pos == c.NOUN

    # Negative tests for invalid pronoun templates

    @pytest.mark.parametrize(
        "template,error_match",
        [
            # Wrong number of features
            ("[pronoun:nom:pri]", "requires 3-4 features"),
            ("[pronoun:nom]", "requires 3-4 features"),
            ("[pronoun:nom:pri:sg:masc:extra]", "requires 3-4 features"),
            # Invalid feature values
            ("[pronoun:invalid:pri:sg]", "Invalid or duplicate feature"),
            ("[pronoun:nom:invalid:sg]", "Invalid or duplicate feature"),
            ("[pronoun:nom:pri:invalid]", "Invalid or duplicate feature"),
            ("[pronoun:nom:pri:sg:invalid]", "Invalid or duplicate feature"),
            # Duplicate features
            ("[pronoun:nom:nom:pri:sg]", "Invalid or duplicate feature"),
            ("[pronoun:nom:pri:1:sg]", "Invalid or duplicate feature"),
            ("[pronoun:nom:pri:sg:sg]", "Invalid or duplicate feature"),
        ],
    )
    def test_parse_invalid_pronoun_templates(self, parser, template, error_match):
        """Test that invalid pronoun templates raise appropriate errors."""
        with pytest.raises(TemplateParseError, match=error_match):
            parser.parse(template)
