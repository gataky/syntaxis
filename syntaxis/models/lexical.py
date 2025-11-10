from dataclasses import dataclass
from typing import Generic, TypeVar

from syntaxis.models import constants as c
from syntaxis.models import types

pos = TypeVar("pos")


@dataclass
class Lexical(Generic[pos]):
    """Base class for all parts of speech with common fields."""

    lemma: str
    forms: pos
    word: str | None = None
    translations: list[str] | None = None

    def __str__(self):
        if self.word:
            return list(self.word)[0]
        return "NONE"


@dataclass
class Adjective(Lexical[types.Adjective]):
    def get_form(self, gender: str, number: str, case: str, **extra) -> set[str]:
        return self.forms["adj"][number][gender][case]


@dataclass
class Adverb(Lexical[types.Adverb]):
    def get_form(self, **extra) -> set[str]:
        return self.forms[c.ADVERB]


@dataclass
class Article(Lexical[types.Article]):
    def get_form(self, number: str, gender: str, case: str, **extra) -> set[str]:
        return self.forms[number][gender][case]


@dataclass
class Noun(Lexical[types.Noun]):
    def get_form(self, gender: str, number: str, case: str, **extra) -> set[str]:
        return self.forms[gender][number][case]


@dataclass
class Numberal(Lexical[types.Numeral]):
    def get_form(self, number: str, gender: str, case: str, **extra) -> set[str]:
        return self.forms[c.ADJECTIVE][number][gender][case]


@dataclass
class Pronoun(Lexical[types.Pronoun]):
    def get_form(self, number: str, gender: str, case: str, **extra) -> set[str]:
        return self.forms[number][gender][case]


@dataclass
class Verb(Lexical[types.Verb]):
    def get_form(
        self,
        tense: str,
        voice: str,
        number: str,
        person: str,
        case: str = c.NOMINATIVE,
        mood: str = c.INDICATIVE,
        **extra,
    ) -> set[str]:
        return self.forms[tense][voice][mood][number][person]


@dataclass
class Preposition(Lexical[types.Preposition]):
    def get_form(self, **extra) -> set[str]:
        return self.forms["prep"]


@dataclass
class Conjunction(Lexical[types.Conjunction]):
    def get_form(self, **extra) -> set[str]:
        return self.forms["conj"]
