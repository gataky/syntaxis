from dataclasses import dataclass
from typing import Generic, TypeVar

from syntaxis.models import enums, types

pos = TypeVar("pos")


@dataclass
class PartOfSpeech(Generic[pos]):
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
class Adjective(PartOfSpeech[types.Adjective]):
    def get_form(self, gender: enums.Gender, number: enums.Number, case: enums.Case, **extra) -> set[str]:
        return self.forms["adj"][number][gender][case]


@dataclass
class Adverb(PartOfSpeech[types.Adverb]):
    def get_form(self, **extra) -> set[str]:
        return self.forms[enums.PartOfSpeech.ADVERB]


@dataclass
class Article(PartOfSpeech[types.Article]):
    def get_form(
        self, number: enums.Number, gender: enums.Gender, case: enums.Case, **extra
    ) -> set[str]:
        return self.forms[number][gender][case]


@dataclass
class Noun(PartOfSpeech[types.Noun]):
    def get_form(
        self,
        gender: enums.Gender,
        number: enums.Number,
        case: enums.Case,
        **extra
    ) -> set[str]:
        return self.forms[gender][number][case]


@dataclass
class Numberal(PartOfSpeech[types.Numeral]):
    def get_form(
        self, number: enums.Number, gender: enums.Gender, case: enums.Case, **extra
    ) -> set[str]:
        return self.forms[enums.PartOfSpeech.ADJECTIVE][number][gender][case]


@dataclass
class Pronoun(PartOfSpeech[types.Pronoun]):
    def get_form(
        self, number: enums.Number, gender: enums.Gender, case: enums.Case, **extra
    ) -> set[str]:
        return self.forms[number][gender][case]


@dataclass
class Verb(PartOfSpeech[types.Verb]):
    def get_form(
        self,
        tense: enums.Tense,
        voice: enums.Voice,
        number: enums.Number,
        person: enums.Person,
        case: enums.Case = enums.Case.NOMINATIVE.value,
        mood: enums.Mood = enums.Mood.INDICATIVE.value,
        **extra,
    ) -> set[str]:
        import pudb; pudb.set_trace()
        return self.forms[tense][voice][mood][number][person]


@dataclass
class Preposition(PartOfSpeech[types.Preposition]):
    def get_form(self, **extra) -> set[str]:
        return self.forms["prep"]


@dataclass
class Conjunction(PartOfSpeech[types.Conjunction]):
    def get_form(self, **extra) -> set[str]:
        return self.forms["conj"]
