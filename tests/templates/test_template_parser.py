"""Unit tests for template parser."""

import pytest

from syntaxis.templates.models import (
    Case,
    Gender,
    Number,
    PartOfSpeech,
    Person,
    Tense,
    Voice,
)
from syntaxis.templates.parser import (
    TemplateParseError,
    TemplateParser,
)


class TestTemplateParser:
    """Test suite for TemplateParser class."""

    @pytest.fixture
    def parser(self):
        """Create a TemplateParser instance for testing."""
        return TemplateParser()

    # Valid template tests

    @pytest.mark.parametrize(
        "template,expected_pos,expected_case,expected_gender,expected_number",
        [
            (
                "[Noun:nom:m:sg]",
                PartOfSpeech.NOUN,
                Case.NOMINATIVE,
                Gender.MASCULINE,
                Number.SINGULAR,
            ),
            (
                "[Article:acc:f:pl]",
                PartOfSpeech.ARTICLE,
                Case.ACCUSATIVE,
                Gender.FEMININE,
                Number.PLURAL,
            ),
            (
                "[Adj:gen:n:sg]",
                PartOfSpeech.ADJECTIVE,
                Case.GENITIVE,
                Gender.NEUTER,
                Number.SINGULAR,
            ),
        ],
    )
    def test_parse_nominal_tokens(
        self,
        parser,
        template,
        expected_pos,
        expected_case,
        expected_gender,
        expected_number,
    ):
        """Test parsing nominal tokens (nouns, articles, adjectives)."""
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == expected_pos
        assert token.case == expected_case
        assert token.gender == expected_gender
        assert token.number == expected_number

    def test_parse_simple_verb(self, parser):
        """Test parsing a simple verb token."""
        template = "[Verb:pres:act:3:pl]"
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == PartOfSpeech.VERB
        assert token.tense == Tense.PRESENT
        assert token.voice == Voice.ACTIVE
        assert token.person == Person.THIRD
        assert token.number == Number.PLURAL

    @pytest.mark.parametrize(
        "template,expected_pos",
        [
            ("[Preposition]", PartOfSpeech.PREPOSITION),
            ("[Adverb]", PartOfSpeech.ADVERB),
            ("[Conjunction]", PartOfSpeech.CONJUNCTION),
        ],
    )
    def test_parse_invariable_words(self, parser, template, expected_pos):
        """Test parsing invariable words."""
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == expected_pos
        assert token.is_invariable()
        assert token.case is None
        assert token.gender is None
        assert token.number is None

    def test_parse_complex_template(self, parser):
        """Test parsing a template with multiple tokens."""
        template = (
            "[Article:nom:m:sg] [Adj:nom:m:sg] [Noun:nom:m:sg] [Verb:aor:act:3:sg]"
        )
        result = parser.parse(template)

        assert len(result.tokens) == 4
        assert result.tokens[0].pos == PartOfSpeech.ARTICLE
        assert result.tokens[1].pos == PartOfSpeech.ADJECTIVE
        assert result.tokens[2].pos == PartOfSpeech.NOUN
        assert result.tokens[3].pos == PartOfSpeech.VERB

    def test_parse_prd_example_template(self, parser):
        """Test parsing the example from the PRD."""
        template = "[Article:nom:n:pl] [Adj:nom:n:pl] [Noun:nom:n:pl] [Verb:pres:act:3:pl] [Adverb]"
        result = parser.parse(template)

        assert len(result.tokens) == 5
        # Verify neuter plural nominative agreement
        assert result.tokens[0].gender == Gender.NEUTER
        assert result.tokens[0].number == Number.PLURAL
        assert result.tokens[1].gender == Gender.NEUTER
        assert result.tokens[1].number == Number.PLURAL
        assert result.tokens[2].gender == Gender.NEUTER
        assert result.tokens[2].number == Number.PLURAL
        # Verify verb
        assert result.tokens[3].tense == Tense.PRESENT
        assert result.tokens[3].number == Number.PLURAL
        # Verify adverb
        assert result.tokens[4].is_invariable()

    def test_parse_features_in_different_order(self, parser):
        """Test that feature order doesn't matter for nominals."""
        template1 = "[Noun:nom:m:sg]"
        template2 = "[Noun:sg:nom:m]"
        template3 = "[Noun:m:sg:nom]"

        result1 = parser.parse(template1)
        result2 = parser.parse(template2)
        result3 = parser.parse(template3)

        # All should parse to the same token features
        for result in [result1, result2, result3]:
            token = result.tokens[0]
            assert token.case == Case.NOMINATIVE
            assert token.gender == Gender.MASCULINE
            assert token.number == Number.SINGULAR

    def test_parse_verb_features_different_order(self, parser):
        """Test that feature order doesn't matter for verbs."""
        template1 = "[Verb:pres:act:3:pl]"
        template2 = "[Verb:pl:3:act:pres]"
        template3 = "[Verb:act:pl:pres:3]"

        result1 = parser.parse(template1)
        result2 = parser.parse(template2)
        result3 = parser.parse(template3)

        # All should parse to the same token features
        for result in [result1, result2, result3]:
            token = result.tokens[0]
            assert token.tense == Tense.PRESENT
            assert token.voice == Voice.ACTIVE
            assert token.person == Person.THIRD
            assert token.number == Number.PLURAL

    # Error handling tests

    @pytest.mark.parametrize(
        "template,error_match",
        [
            ("", "cannot be empty"),
            ("   ", "cannot be empty"),
            ("just some text without brackets", "No valid tokens found"),
            ("[InvalidPOS:nom:m:sg]", "Unknown part of speech"),
            ("[Noun:nom:m]", "requires exactly 3 features"),
            ("[Noun:nom:m:sg:extra]", "requires exactly 3 features"),
            ("[Verb:pres:act:3]", "requires exactly 4 features"),
            ("[Verb:pres:act:3:pl:extra]", "requires exactly 4 features"),
            ("[Noun:invalid:m:sg]", "Invalid or duplicate feature"),
            ("[Noun:nom:invalid:sg]", "Invalid or duplicate feature"),
            ("[Noun:nom:m:invalid]", "Invalid or duplicate feature"),
            ("[Verb:invalid:act:3:pl]", "Invalid or duplicate feature"),
            ("[Noun:nom:nom:m]", "Invalid or duplicate feature"),
            ("[Adverb:nom:m:sg]", "should not have features"),
        ],
    )
    def test_parse_errors(self, parser, template, error_match):
        """Test various parsing error conditions."""
        with pytest.raises(TemplateParseError, match=error_match):
            parser.parse(template)

    @pytest.mark.parametrize("case", list(Case))
    def test_all_cases_valid(self, parser, case):
        """Test that all case values are recognized."""
        template = f"[Noun:{case.value}:m:sg]"
        result = parser.parse(template)
        assert result.tokens[0].case == case

    @pytest.mark.parametrize("gender", list(Gender))
    def test_all_genders_valid(self, parser, gender):
        """Test that all gender values are recognized."""
        template = f"[Noun:nom:{gender.value}:sg]"
        result = parser.parse(template)
        assert result.tokens[0].gender == gender

    @pytest.mark.parametrize("number", list(Number))
    def test_all_numbers_valid(self, parser, number):
        """Test that all number values are recognized."""
        template = f"[Noun:nom:m:{number.value}]"
        result = parser.parse(template)
        assert result.tokens[0].number == number

    @pytest.mark.parametrize("tense", list(Tense))
    def test_all_tenses_valid(self, parser, tense):
        """Test that all tense values are recognized."""
        template = f"[Verb:{tense.value}:act:3:sg]"
        result = parser.parse(template)
        assert result.tokens[0].tense == tense

    @pytest.mark.parametrize("voice", list(Voice))
    def test_all_voices_valid(self, parser, voice):
        """Test that all voice values are recognized."""
        template = f"[Verb:pres:{voice.value}:3:sg]"
        result = parser.parse(template)
        assert result.tokens[0].voice == voice

    @pytest.mark.parametrize("person", list(Person))
    def test_all_persons_valid(self, parser, person):
        """Test that all person values are recognized."""
        template = f"[Verb:pres:act:{person.value}:sg]"
        result = parser.parse(template)
        assert result.tokens[0].person == person

    def test_parsed_template_iteration(self, parser):
        """Test that ParsedTemplate supports iteration."""
        template = "[Noun:nom:m:sg] [Verb:pres:act:3:sg]"
        result = parser.parse(template)

        tokens = list(result)
        assert len(tokens) == 2
        assert tokens[0].pos == PartOfSpeech.NOUN
        assert tokens[1].pos == PartOfSpeech.VERB

    def test_parsed_template_length(self, parser):
        """Test that ParsedTemplate supports len()."""
        template = "[Noun:nom:m:sg] [Verb:pres:act:3:sg] [Adverb]"
        result = parser.parse(template)

        assert len(result) == 3

    def test_raw_template_preserved(self, parser):
        """Test that raw template string is preserved."""
        template = "[Article:nom:n:pl] [Noun:nom:n:pl]"
        result = parser.parse(template)

        assert result.raw_template == template

    # Pronoun template parsing tests

    @pytest.mark.parametrize(
        "template,expected_case,expected_person,expected_number,expected_gender",
        [
            # First person (no gender)
            (
                "[Pronoun:nom:1:sg]",
                Case.NOMINATIVE,
                Person.FIRST,
                Number.SINGULAR,
                None,
            ),
            ("[Pronoun:acc:1:pl]", Case.ACCUSATIVE, Person.FIRST, Number.PLURAL, None),
            ("[Pronoun:gen:1:sg]", Case.GENITIVE, Person.FIRST, Number.SINGULAR, None),
            # Second person (no gender)
            (
                "[Pronoun:nom:2:sg]",
                Case.NOMINATIVE,
                Person.SECOND,
                Number.SINGULAR,
                None,
            ),
            ("[Pronoun:acc:2:pl]", Case.ACCUSATIVE, Person.SECOND, Number.PLURAL, None),
            # Third person with gender
            (
                "[Pronoun:nom:3:sg:m]",
                Case.NOMINATIVE,
                Person.THIRD,
                Number.SINGULAR,
                Gender.MASCULINE,
            ),
            (
                "[Pronoun:gen:3:sg:f]",
                Case.GENITIVE,
                Person.THIRD,
                Number.SINGULAR,
                Gender.FEMININE,
            ),
            (
                "[Pronoun:acc:3:pl:n]",
                Case.ACCUSATIVE,
                Person.THIRD,
                Number.PLURAL,
                Gender.NEUTER,
            ),
            (
                "[Pronoun:voc:3:sg:m]",
                Case.VOCATIVE,
                Person.THIRD,
                Number.SINGULAR,
                Gender.MASCULINE,
            ),
        ],
    )
    def test_parse_pronoun_valid_forms(
        self,
        parser,
        template,
        expected_case,
        expected_person,
        expected_number,
        expected_gender,
    ):
        """Test parsing various valid pronoun forms."""
        result = parser.parse(template)

        assert len(result.tokens) == 1
        token = result.tokens[0]
        assert token.pos == PartOfSpeech.PRONOUN
        assert token.case == expected_case
        assert token.person == expected_person
        assert token.number == expected_number
        assert token.gender == expected_gender

    @pytest.mark.parametrize("case", list(Case))
    def test_parse_pronoun_all_cases(self, parser, case):
        """Test that all cases work with pronouns."""
        template = f"[Pronoun:{case.value}:1:sg]"
        result = parser.parse(template)
        assert result.tokens[0].case == case
        assert result.tokens[0].person == Person.FIRST
        assert result.tokens[0].number == Number.SINGULAR

    @pytest.mark.parametrize("person", list(Person))
    def test_parse_pronoun_all_persons(self, parser, person):
        """Test that all persons work with pronouns."""
        # Third person needs gender, others don't
        if person == Person.THIRD:
            template = f"[Pronoun:nom:{person.value}:sg:m]"
        else:
            template = f"[Pronoun:nom:{person.value}:sg]"
        result = parser.parse(template)
        assert result.tokens[0].person == person

    def test_parse_pronoun_subject_verb_template(self, parser):
        """Test parsing a template with pronoun subject and verb."""
        template = "[Pronoun:nom:1:sg] [Verb:pres:act:1:sg]"
        result = parser.parse(template)

        assert len(result.tokens) == 2
        assert result.tokens[0].pos == PartOfSpeech.PRONOUN
        assert result.tokens[0].person == Person.FIRST
        assert result.tokens[1].pos == PartOfSpeech.VERB
        assert result.tokens[1].person == Person.FIRST

    def test_parse_complex_template_with_pronoun(self, parser):
        """Test parsing a complex template including pronouns."""
        template = "[Pronoun:nom:3:sg:m] [Verb:aor:act:3:sg] [Article:acc:n:sg] [Noun:acc:n:sg]"
        result = parser.parse(template)

        assert len(result.tokens) == 4
        assert result.tokens[0].pos == PartOfSpeech.PRONOUN
        assert result.tokens[0].person == Person.THIRD
        assert result.tokens[0].gender == Gender.MASCULINE
        assert result.tokens[1].pos == PartOfSpeech.VERB
        assert result.tokens[2].pos == PartOfSpeech.ARTICLE
        assert result.tokens[3].pos == PartOfSpeech.NOUN

    # Negative tests for invalid pronoun templates

    @pytest.mark.parametrize(
        "template,error_match",
        [
            # Wrong number of features
            ("[Pronoun:nom:1]", "requires 3-4 features"),
            ("[Pronoun:nom]", "requires 3-4 features"),
            ("[Pronoun:nom:1:sg:m:extra]", "requires 3-4 features"),
            # Invalid feature values
            ("[Pronoun:invalid:1:sg]", "Invalid or duplicate feature"),
            ("[Pronoun:nom:invalid:sg]", "Invalid or duplicate feature"),
            ("[Pronoun:nom:1:invalid]", "Invalid or duplicate feature"),
            ("[Pronoun:nom:1:sg:invalid]", "Invalid or duplicate feature"),
            # Duplicate features
            ("[Pronoun:nom:nom:1:sg]", "Invalid or duplicate feature"),
            ("[Pronoun:nom:1:1:sg]", "Invalid or duplicate feature"),
            ("[Pronoun:nom:1:sg:sg]", "Invalid or duplicate feature"),
        ],
    )
    def test_parse_invalid_pronoun_templates(self, parser, template, error_match):
        """Test that invalid pronoun templates raise appropriate errors."""
        with pytest.raises(TemplateParseError, match=error_match):
            parser.parse(template)
