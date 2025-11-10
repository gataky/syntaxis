from dataclasses import dataclass
from typing import Generic, TypeVar, cast

from syntaxis.models import constants as c
from syntaxis.models import types

lexical = TypeVar("lexical")


@dataclass
class Lexical(Generic[lexical]):
    """Base class for all parts of speech with common fields."""

    # The dictionary form of the word in the nom, masc, sg form.
    lemma: str
    # All the forms for this word from modern-greek-lexical
    forms: lexical
    # The final word after declining with a given set of features.  This word is set after
    # calling apply_features. Based on the features given we will extract from forms to find
    # the final word.
    word: set[str] | None = None
    # The English translations for the given lemma. Note that the forms of these words to not
    # decline i.e. If the word is in the plural form in Greek it will be in the singular form
    # here in translations.
    translations: list[str] | None = None

    def __str__(self) -> str:
        if self.word is not None:
            return list(self.word)[0]
        else:
            return self.lemma

    def apply_features(self, *args, **kwargs) -> set[str]:
        """apply_features will extract the morphed word from forms for the given set of features"""
        raise NotImplementedError("apply_features not implemented for this Lexical")


class Adjective(Lexical[types.Adjective]):
    def apply_features(self, gender: str, number: str, case: str, **extra) -> set[str]:
        adjective_forms: types.Adjective = self.forms
        self.word = adjective_forms["adj"][number][gender][case]
        return self.word


class Adverb(Lexical[types.Adverb]):
    def apply_features(self, **extra) -> set[str]:
        self.word = self.forms[c.ADVERB]
        return self.word


class Article(Lexical[types.Article]):
    def apply_features(self, number: str, gender: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[number][gender][case])
        return self.word


class Noun(Lexical[types.Noun]):
    def apply_features(self, gender: str, number: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[gender][number][case])
        return self.word


class Numberal(Lexical[types.Numeral]):
    def apply_features(self, number: str, gender: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[c.ADJECTIVE][number][gender][case])
        return self.word


class Pronoun(Lexical[types.Pronoun]):
    def apply_features(self, number: str, gender: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[number][gender][case])
        return self.word


class Verb(Lexical[types.Verb]):
    def apply_features(
        self,
        tense: str,
        voice: str,
        number: str,
        person: str,
        case: str = c.NOMINATIVE,
        mood: str = c.INDICATIVE,
        **extra,
    ) -> set[str]:
        self.word = cast(set[str], self.forms[tense][voice][mood][number][person])
        return self.word


class Preposition(Lexical[types.Preposition]):
    def apply_features(self, **extra) -> set[str]:
        self.word = self.forms["prep"]
        return self.word


class Conjunction(Lexical[types.Conjunction]):
    def apply_features(self, **extra) -> set[str]:
        self.word = self.forms["conj"]
        return self.word
