from enum import Enum

from modern_greek_inflexion import resources


class PartOfSpeech(Enum):
    # The following POS appear in the modern_greek_inflexion
    # library
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    NUMERAL = "numeral"
    ADVERB = "adv"
    ARTICLE = "article"
    ADJECTIVE = "adj"
    # These two POS do not appear in modern_greek_inflexion
    # because they don't decline
    PREPOSITION = "prep"
    CONJUNCTION = "conj"


PartOfSpeechMap = {
    "noun": PartOfSpeech.NOUN,
    "verb": PartOfSpeech.VERB,
    "pronoun": PartOfSpeech.PRONOUN,
    "numeral": PartOfSpeech.NUMERAL,
    "adverb": PartOfSpeech.ADVERB,
    "article": PartOfSpeech.ARTICLE,
    "adjective": PartOfSpeech.ADJECTIVE,
    "preposition": PartOfSpeech.PREPOSITION,
    "conjunction": PartOfSpeech.CONJUNCTION,
}


class Gender(Enum):
    MASCULINE = resources.MASC
    FEMININE = resources.FEM
    NEUTER = resources.NEUT


class Number(Enum):
    SINGULAR = resources.SG
    PLURAL = resources.PL


class Case(Enum):
    NOMINATIVE = resources.NOM
    VOCATIVE = resources.VOC
    ACCUSATIVE = resources.ACC
    GENITIVE = resources.GEN


class Mood(Enum):
    INDICATIVE = resources.IND
    IMPERATIVE = resources.IMP


class Person(Enum):
    FIRST = resources.PRI
    SECOND = resources.SEC
    THIRD = resources.TER


class Voice(Enum):
    ACTIVE = resources.ACTIVE
    PASSIVE = resources.PASSIVE


class Tense(Enum):
    # Simple past
    AORIST = resources.AORIST
    # Past continuous (imperfect)
    PARATATIKOS = resources.PARATATIKOS
    # Present simple/continuous
    PRESENT = resources.PRESENT

    # These values do not appear in modern_greek_inflexion and
    # will have to be derived.
    FUTURE = "future c"
    FUTURE_SIMPLE = "future s"


class Aspect(Enum):
    PERFECT = resources.PERF
    IMPERFECT = resources.IMPERF
