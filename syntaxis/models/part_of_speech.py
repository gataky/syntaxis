from dataclasses import dataclass
from typing import Generic, TypeVar

from syntaxis.models import enums, types

pos = TypeVar("pos")


@dataclass
class PartOfSpeech(Generic[pos]):
    """Base class for all parts of speech with common fields."""

    lemma: str
    forms: pos
    translations: list[str] | None = None


@dataclass
class Adjective(PartOfSpeech[types.Adjective]):
    def get_form(self, number: enums.Number, case: enums.Case) -> set[str]:
        return self.forms[enums.PartOfSpeech.ADJECTIVE][number][case]


@dataclass
class Adverb(PartOfSpeech[types.Adverb]):
    def get_form(self) -> set[str]:
        return self.forms[enums.PartOfSpeech.ADVERB]


@dataclass
class Article(PartOfSpeech[types.Article]):
    def get_form(
        self, number: enums.Number, gender: enums.Gender, case: enums.Case
    ) -> set[str]:
        return self.forms[number][gender][case]


@dataclass
class Noun(PartOfSpeech[types.Noun]):
    def get_form(
        self,
        gender: enums.Gender,
        number: enums.Number,
        case: enums.Case,
    ) -> set[str]:
        return self.forms[gender][number][case]


@dataclass
class Numberal(PartOfSpeech[types.Numeral]):
    def get_form(
        self, number: enums.Number, gender: enums.Gender, case: enums.Case
    ) -> set[str]:
        return self.forms[enums.PartOfSpeech.ADJECTIVE][number][gender][case]


@dataclass
class Pronoun(PartOfSpeech[types.Pronoun]):
    def get_form(
        self, number: enums.Number, gender: enums.Gender, case: enums.Case
    ) -> set[str]:
        return self.forms[number][gender][case]

@dataclass
class Preposition(PartOfSpeech[types.Preposition]):
    def get_form(self) -> set[str]:
        return self.forms["prep"]

@dataclass
class Conjunction(PartOfSpeech[types.Conjunction]):
    def get_form(self) -> set[str]:
        return self.forms["conj"]

@dataclass
class Verb(PartOfSpeech[types.Verb]):
    def get_form(
        self,
        tense: enums.Tense,
        voice: enums.Voice,
        mood: enums.Mood,
        number: enums.Number,
        person: enums.Person,
        case: enums.Case,
    ) -> set[str]:
        return self.forms[tense][voice][mood][number][person][case]
