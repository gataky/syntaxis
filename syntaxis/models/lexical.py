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

    case:   str | None = None
    gender: str | None = None
    mood:   str | None = None
    number: str | None = None
    person: str | None = None
    tense:  str | None = None
    voice:  str | None = None

    def __str__(self) -> str:
        if self.word is not None:
            return list(self.word)[0]
        else:
            return self.lemma

    def apply_features(self, *args, **kwargs) -> set[str]:
        """apply_features will extract the morphed word from forms for the given set of features"""
        raise NotImplementedError("apply_features not implemented for this Lexical")


class Adjective(Lexical[types.Adjective]):
    """Greek adjective with full declension forms.

    Adjectives in Greek decline for gender (masculine, feminine, neuter),
    number (singular, plural), and case (nominative, genitive, accusative, vocative).

    Attributes:
        lemma: Dictionary form of the adjective (masculine nominative singular)
        forms: Nested dictionary structure containing all declined forms
            Format: forms["adj"][number][gender][case] -> set[str]
        word: The specific declined form after applying features
        translations: English translations of the lemma

    Example:
        >>> adj = Adjective(lemma="μεγάλος", forms=..., translations=["big", "large"])
        >>> adj.apply_features(gender="fem", number="pl", case="acc")
        {"μεγάλες"}
    """

    def apply_features(self, gender: str, number: str, case: str, **extra) -> set[str]:
        adjective_forms: types.Adjective = self.forms
        self.word = adjective_forms["adj"][number][gender][case]
        return self.word


class Adverb(Lexical[types.Adverb]):
    """Greek adverb (invariable word).

    Adverbs in Greek typically do not decline - they have a single invariable form.

    Attributes:
        lemma: The adverb in its standard form
        forms: Dictionary with single entry under "adverb" key
            Format: forms["adverb"] -> set[str]
        word: The adverb (same as lemma since invariable)
        translations: English translations

    Example:
        >>> adv = Adverb(lemma="τώρα", forms={"adverb": {"τώρα"}}, translations=["now"])
        >>> adv.apply_features()
        {"τώρα"}
    """

    def apply_features(self, **extra) -> set[str]:
        self.word = self.forms[c.ADVERB]
        return self.word


class Article(Lexical[types.Article]):
    """Greek article (definite or indefinite).

    Articles in Greek decline for gender, number, and case to agree with
    the noun they modify. Both definite (ο, η, το) and indefinite (ένας, μία, ένα)
    articles are represented by this class.

    Attributes:
        lemma: Base form of the article (e.g., "ο" for definite masculine)
        forms: Nested dictionary structure containing all declined forms
            Format: forms[number][gender][case] -> set[str]
        word: The specific declined form after applying features
        translations: English translation (typically "the" or "a/an")

    Example:
        >>> art = Article(lemma="ο", forms=..., translations=["the"])
        >>> art.apply_features(number="pl", gender="masc", case="acc")
        {"τους"}
    """

    def apply_features(self, number: str, gender: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[number][gender][case])
        return self.word


class Noun(Lexical[types.Noun]):
    """Greek noun with full declension forms.

    Nouns in Greek have inherent gender (masculine, feminine, or neuter) and
    decline for number (singular, plural) and case (nominative, genitive,
    accusative, vocative).

    Attributes:
        lemma: Dictionary form of the noun (nominative singular)
        forms: Nested dictionary structure containing all declined forms
            Format: forms[gender][number][case] -> set[str]
        word: The specific declined form after applying features
        translations: English translations of the lemma

    Example:
        >>> noun = Noun(lemma="άνθρωπος", forms=..., translations=["person", "human"])
        >>> noun.apply_features(gender="masc", number="pl", case="nom")
        {"άνθρωποι"}
    """

    def apply_features(self, gender: str, number: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[gender][number][case])
        return self.word


class Numeral(Lexical[types.Numeral]):
    """Greek numeral (cardinal or ordinal numbers).

    Numerals in Greek typically decline like adjectives, agreeing with the noun
    they modify in gender, number, and case.

    Attributes:
        lemma: Base form of the numeral (e.g., "ένας" for "one")
        forms: Nested dictionary structure similar to adjectives
            Format: forms["adjective"][number][gender][case] -> set[str]
        word: The specific declined form after applying features
        translations: English translations (e.g., ["one"], ["first"])

    Example:
        >>> num = Numeral(lemma="ένας", forms=..., translations=["one"])
        >>> num.apply_features(number="sg", gender="fem", case="nom")
        {"μία"}

    Note:
        This class was previously misspelled as "Numberal" in the codebase.
    """

    def apply_features(self, number: str, gender: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[c.ADJECTIVE][number][gender][case])
        return self.word


class Pronoun(Lexical[types.Pronoun]):
    """Greek pronoun with full declension forms.

    Pronouns in Greek decline for person (1st, 2nd, 3rd), number (singular, plural),
    case (nominative, genitive, accusative), and gender (for 3rd person only).

    Attributes:
        lemma: Base form of the pronoun (e.g., "εγώ" for "I")
        forms: Nested dictionary structure containing all declined forms
            Format: forms[number][gender][case] -> set[str]
        word: The specific declined form after applying features
        translations: English translations (e.g., ["I"], ["he"], ["they"])

    Example:
        >>> pron = Pronoun(lemma="εγώ", forms=..., translations=["I"])
        >>> pron.apply_features(number="sg", gender="masc", case="acc")
        {"με"}

    Note:
        Gender is only required for 3rd person pronouns. For 1st and 2nd person,
        the gender parameter is present but not used in some forms.
    """

    def apply_features(self, number: str, gender: str, case: str, **extra) -> set[str]:
        self.word = cast(set[str], self.forms[number][gender][case])
        return self.word


class Verb(Lexical[types.Verb]):
    """Greek verb with full conjugation forms.

    Verbs in Greek conjugate for tense (present, aorist, paratatikos, etc.),
    voice (active, passive), mood (indicative, subjunctive, imperative),
    person (1st, 2nd, 3rd), and number (singular, plural).

    Attributes:
        lemma: Dictionary form of the verb (1st person singular present active)
        forms: Nested dictionary structure containing all conjugated forms
            Format: forms[tense][voice][mood][number][person] -> set[str]
        word: The specific conjugated form after applying features
        translations: English translations of the lemma (infinitive form)

    Example:
        >>> verb = Verb(lemma="βλέπω", forms=..., translations=["see", "look"])
        >>> verb.apply_features(tense="present", voice="active", number="sg", person="ter")
        {"βλέπει"}

    Note:
        The case and mood parameters have default values since they are less
        commonly varied in basic sentence construction.
    """

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
    """Greek preposition (invariable word).

    Prepositions in Greek do not decline - they have a single invariable form.
    They govern specific cases for the nouns that follow them.

    Attributes:
        lemma: The preposition in its standard form
        forms: Dictionary with single entry under "prep" key
            Format: forms["prep"] -> set[str]
        word: The preposition (same as lemma since invariable)
        translations: English translations (e.g., ["with"], ["from"], ["to"])

    Example:
        >>> prep = Preposition(lemma="με", forms={"prep": {"με"}}, translations=["with"])
        >>> prep.apply_features()
        {"με"}

    Note:
        While prepositions themselves don't decline, they require the following
        noun to be in a specific case (which varies by preposition).
    """

    def apply_features(self, **extra) -> set[str]:
        self.word = self.forms["prep"]
        return self.word


class Conjunction(Lexical[types.Conjunction]):
    """Greek conjunction (invariable word).

    Conjunctions in Greek do not decline - they have a single invariable form.
    They connect words, phrases, or clauses.

    Attributes:
        lemma: The conjunction in its standard form
        forms: Dictionary with single entry under "conj" key
            Format: forms["conj"] -> set[str]
        word: The conjunction (same as lemma since invariable)
        translations: English translations (e.g., ["and"], ["but"], ["or"])

    Example:
        >>> conj = Conjunction(lemma="και", forms={"conj": {"και"}}, translations=["and"])
        >>> conj.apply_features()
        {"και"}

    Note:
        Common Greek conjunctions include και (and), αλλά (but), ή (or),
        ότι (that), επειδή (because), etc.
    """

    def apply_features(self, **extra) -> set[str]:
        self.word = self.forms["conj"]
        return self.word
