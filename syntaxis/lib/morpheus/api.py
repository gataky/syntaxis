"""Morpheus: Translation layer between modern_greek_inflexion and syntaxis."""

from typing import TypeVar, cast

import modern_greek_inflexion as mgi

from syntaxis.lib.models import constants as c
from syntaxis.lib.models.lexical import (
    Adjective,
    Adverb,
    Article,
    Conjunction,
    Noun,
    Numeral,
    Preposition,
    Pronoun,
    Verb,
)

from .translator import translate_forms

T = TypeVar("T", Adjective, Adverb, Article, Noun, Numeral, Pronoun, Verb, Preposition)


class Morpheus:
    """Translation layer between modern_greek_inflexion and syntaxis.

    This class handles all interaction with modern_greek_inflexion,
    translating between mgi's constants and syntaxis's string constants.
    """

    @staticmethod
    def create(lemma: str, lexical: str) -> T:
        """Generic method to create any lexical type from lemma.

        Args:
            lemma: The base form of the word
            lexical: Part of speech string constant (c.NOUN, c.VERB, etc.)

        Returns:
            Appropriate PartOfSpeech subclass with forms using syntaxis constants

        Raises:
            KeyError: If lexical is not in the method map

        Examples:
            >>> Morpheus.create("άνθρωπος", c.NOUN)
            Noun(lemma="άνθρωπος", forms={...})
        """
        method_map = {
            c.NOUN: Morpheus.noun,
            c.VERB: Morpheus.verb,
            c.ADJECTIVE: Morpheus.adjective,
            c.ARTICLE: Morpheus.article,
            c.PRONOUN: Morpheus.pronoun,
            c.ADVERB: Morpheus.adverb,
            c.NUMERAL: Morpheus.numeral,
            c.PREPOSITION: Morpheus.preposition,
            c.CONJUNCTION: Morpheus.conjunction,
        }
        return method_map[lexical](lemma)

    @staticmethod
    def _get_inflected_forms(lemma: str, lexical_class: type[T]) -> T:
        """Generic method to get inflected forms for any part of speech.

        Gets forms from modern_greek_inflexion and translates to syntaxis constants.
        """
        # Map our classes to the mgi classes
        mgi_class = getattr(mgi, lexical_class.__name__)
        mgi_forms = mgi_class(lemma).all()
        syntaxis_forms = cast(dict, translate_forms(mgi_forms))
        lexical_name = lexical_class.__name__.lower()
        return lexical_class(lexical_name, lemma, syntaxis_forms)

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
    def numeral(lemma: str) -> Numeral:
        return Morpheus._get_inflected_forms(lemma, Numeral)

    @staticmethod
    def pronoun(lemma: str) -> Pronoun:
        return Morpheus._get_inflected_forms(lemma, Pronoun)

    @staticmethod
    def verb(lemma: str) -> Verb:
        return Morpheus._get_inflected_forms(lemma, Verb)

    # The following lexicals do not exist in modern_greek_inflexion
    # because they don't inflect in any way. So we "inflect"
    # them ourselves by returning a forms like dict with the
    # lemma as the declined word.

    @staticmethod
    def preposition(lemma: str) -> Preposition:
        return Preposition(c.PREPOSITION, lemma, forms={"prep": {lemma}})

    @staticmethod
    def conjunction(lemma: str) -> Conjunction:
        return Conjunction(c.CONJUNCTION, lemma, forms={"conj": {lemma}})
