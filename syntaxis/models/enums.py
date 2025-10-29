from enum import Enum

from modern_greek_inflexion import resources


class PartOfSpeech(Enum):
    NOUN = "noun"
    VERB = "verb"
    PRONOUN = "pronoun"
    NUMERAL = "numeral"
    ADVERB = "adv"
    ARTICLE = "article"
    ADJECTIVE = "adj"


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
