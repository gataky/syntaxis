"""Data models for template parsing and representation."""

from dataclasses import dataclass
from enum import Enum


class PartOfSpeech(Enum):
    """Part of speech types supported in templates."""

    NOUN = "Noun"
    VERB = "Verb"
    ADJECTIVE = "Adj"
    ARTICLE = "Article"
    PRONOUN = "Pronoun"
    PREPOSITION = "Preposition"
    CONJUNCTION = "Conjunction"
    ADVERB = "Adverb"


class Case(Enum):
    """Greek grammatical cases."""

    NOMINATIVE = "nom"
    GENITIVE = "gen"
    ACCUSATIVE = "acc"
    VOCATIVE = "voc"


class Gender(Enum):
    """Greek grammatical genders."""

    MASCULINE = "m"
    FEMININE = "f"
    NEUTER = "n"


class Number(Enum):
    """Greek grammatical numbers."""

    SINGULAR = "sg"
    PLURAL = "pl"


class Voice(Enum):
    """Greek verb voices."""

    ACTIVE = "act"
    PASSIVE = "pass"


class Tense(Enum):
    """Greek verb tenses."""

    AORIST = "aor"
    FUTURE_PERFECT = "futperf"
    IMPERFECT = "impf"
    PERFECT = "perf"
    PLUPERFECT = "plup"
    PRESENT = "pres"
    SIMPLE_FUTURE = "fut"


class Person(Enum):
    """Greek grammatical persons."""

    FIRST = "1"
    SECOND = "2"
    THIRD = "3"


@dataclass
class TokenFeatures:
    """Represents the grammatical features required for a token in a template.

    Attributes:
        pos: Part of speech (required for all tokens)
        case: Grammatical case (required for nouns, adjectives, articles)
        gender: Grammatical gender (required for nouns, adjectives, articles)
        number: Grammatical number (required for nouns, adjectives, articles, verbs)
        tense: Verb tense (required for verbs)
        voice: Verb voice (required for verbs)
        person: Grammatical person (required for verbs)
    """

    pos: PartOfSpeech
    case: Case | None = None
    gender: Gender | None = None
    number: Number | None = None
    tense: Tense | None = None
    voice: Voice | None = None
    person: Person | None = None

    def is_inflectable(self) -> bool:
        """Check if this token type requires inflection."""
        return self.pos in {
            PartOfSpeech.NOUN,
            PartOfSpeech.VERB,
            PartOfSpeech.ADJECTIVE,
            PartOfSpeech.ARTICLE,
            PartOfSpeech.PRONOUN,
        }

    def is_invariable(self) -> bool:
        """Check if this token type is invariable (doesn't inflect)."""
        return self.pos in {
            PartOfSpeech.PREPOSITION,
            PartOfSpeech.CONJUNCTION,
            PartOfSpeech.ADVERB,
        }


@dataclass
class ParsedTemplate:
    """Represents a fully parsed template with all token features extracted.

    Attributes:
        raw_template: The original template string
        tokens: List of TokenFeatures extracted from the template
    """

    raw_template: str
    tokens: list[TokenFeatures]

    def __len__(self) -> int:
        """Return the number of tokens in the template."""
        return len(self.tokens)

    def __iter__(self):
        """Allow iteration over tokens."""
        return iter(self.tokens)
