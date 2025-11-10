"""Data models for template parsing and representation."""

from dataclasses import dataclass

from syntaxis.models import constants as c


@dataclass
class Token:
    """Represents the grammatical features required for a token in a template.

    Attributes:
        lexical: Part of speech (required for all tokens)
        form: Grammatical form (required for nouns, adjectives, articles)
        gender: Grammatical gender (required for nouns, adjectives, articles)
        number: Grammatical number (required for nouns, adjectives, articles, verbs)
        tense: Verb tense (required for verbs)
        voice: Verb voice (required for verbs)
        person: Grammatical person (required for verbs)
    """

    lexical: str
    # Features for the lexical
    form: str | None = None
    gender: str | None = None
    number: str | None = None
    tense: str | None = None
    voice: str | None = None
    person: str | None = None

    def is_inflectable(self) -> bool:
        """Check if this token type requires inflection."""
        return self.lexical in {c.NOUN, c.VERB, c.ADJECTIVE, c.ARTICLE, c.PRONOUN}

    def is_invariable(self) -> bool:
        """Check if this token type is invariable (doesn't inflect)."""
        return self.lexical in {c.PREPOSITION, c.CONJUNCTION, c.ADVERB}

    def features(self) -> dict[str, str]:
        features = {}
        for k, v in self.__dict__.items():
            if k == "lexical":
                continue
            if v is None:
                continue
            features[k] = v
        return features


@dataclass
class ParsedTemplate:
    """Represents a fully parsed template with all token features extracted.

    Attributes:
        raw_template: The original template string
        tokens: List of TokenFeatures extracted from the template
    """

    raw_template: str
    tokens: list[Token]

    def __len__(self) -> int:
        """Return the number of tokens in the template."""
        return len(self.tokens)

    def __iter__(self):
        """Allow iteration over tokens."""
        return iter(self.tokens)
