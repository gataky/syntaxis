from typing import Type, TypeVar

import modern_greek_inflexion as mgi

from syntaxis.models.part_of_speech import (
    Adjective,
    Adverb,
    Article,
    Noun,
    Numberal,
    Pronoun,
    Verb,
)
from syntaxis.models.enums import PartOfSpeech as POSEnum

# TypeVar for part of speech classes
T = TypeVar("T", Adjective, Adverb, Article, Noun, Numberal, Pronoun, Verb)


class Morpheus:

    @staticmethod
    def create(lemma: str, pos: POSEnum) -> T:
        """Generic method to create any POS type from lemma.

        Args:
            lemma: The base form of the word
            pos: Part of speech enum value

        Returns:
            Appropriate PartOfSpeech subclass instance with forms populated

        Raises:
            KeyError: If pos is not in the method map

        Examples:
            >>> Morpheus.create("άνθρωπος", POSEnum.NOUN)
            Noun(lemma="άνθρωπος", forms={...})
        """
        method_map = {
            POSEnum.NOUN: Morpheus.noun,
            POSEnum.VERB: Morpheus.verb,
            POSEnum.ADJECTIVE: Morpheus.adjective,
            POSEnum.ARTICLE: Morpheus.article,
            POSEnum.PRONOUN: Morpheus.pronoun,
            POSEnum.ADVERB: Morpheus.adverb,
            POSEnum.NUMERAL: Morpheus.numeral,
        }
        return method_map[pos](lemma)

    @staticmethod
    def _get_inflected_forms(lemma: str, pos_class: Type[T]) -> T:
        """Generic method to get inflected forms for any part of speech."""
        # Map our classes to the mgi classes
        mgi_class = getattr(mgi, pos_class.__name__)
        forms = mgi_class(lemma).all()
        return pos_class(lemma, forms)

    @staticmethod
    def adjective(lemma: str) -> Adjective:
        return Morpheus._get_inflected_forms(lemma, Adjective)

    @staticmethod
    def adverb(lemma: str) -> Adverb:
        return Morpheus._get_inflected_forms(lemma, Adverb)

    @staticmethod
    def article(lemma: str) -> Article:
        return Morpheus._get_inflected_forms(lemma, Article)

    @staticmethod
    def noun(lemma: str) -> Noun:
        return Morpheus._get_inflected_forms(lemma, Noun)

    @staticmethod
    def numeral(lemma: str) -> Numberal:
        return Morpheus._get_inflected_forms(lemma, Numberal)

    @staticmethod
    def pronoun(lemma: str) -> Pronoun:
        return Morpheus._get_inflected_forms(lemma, Pronoun)

    @staticmethod
    def verb(lemma: str) -> Verb:
        return Morpheus._get_inflected_forms(lemma, Verb)
