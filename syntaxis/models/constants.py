"""String constants for syntaxis grammatical features.

These constants define the canonical string representations used throughout
syntaxis. The morpheus module handles translation to/from modern_greek_inflexion.
"""

LEMMA = "lemma"

# Features
GENDER = "gender"
NUMBER = "number"
FORM = "form"
TENSE = "tense"
VOICE = "voice"
MOOD = "mood"
PERSON = "person"
TYPE = "type"

# Part of speech constants (using template-friendly abbreviations)
NOUN = "noun"
VERB = "verb"
ADJECTIVE = "adj"
ADVERB = "adv"
ARTICLE = "article"
PRONOUN = "pronoun"
NUMERAL = "numeral"
PREPOSITION = "prep"
CONJUNCTION = "conj"

# ---- TODO names these
DEFINITE = "definite"
INDEFINITE = "indefinite"

PERSONAL_STRONG = "personal_strong"
PERSONAL_WEAK = "personal_weak"
DEMONSTRATIVE = "demonstrative"
INTERROGATIVE = "interrogative"
POSSESSIVE = "possessive"
RELATIVE = "relative"
# ----

# Gender constants (MGI abbreviations)
MASCULINE = "masc"
FEMININE = "fem"
NEUTER = "neut"

# Number constants (MGI abbreviations)
SINGULAR = "sg"
PLURAL = "pl"

# Case constants (MGI abbreviations)
NOMINATIVE = "nom"
ACCUSATIVE = "acc"
GENITIVE = "gen"
VOCATIVE = "voc"

# Tense constants (MGI full names)
PRESENT = "present"
AORIST = "aorist"
PARATATIKOS = "paratatikos"
FUTURE = "future c"
FUTURE_SIMPLE = "future s"

# Voice constants (MGI full names)
ACTIVE = "active"
PASSIVE = "passive"

# Mood constants (MGI abbreviations)
INDICATIVE = "ind"
IMPERATIVE = "imp"

# Person constants (MGI abbreviations)
FIRST = "pri"
SECOND = "sec"
THIRD = "ter"

# Aspect constants (MGI abbreviations)
PERFECT = "perf"
IMPERFECT = "imperf"

LEXICAL_MAP = {
    "noun": NOUN,
    "verb": VERB,
    "adjective": ADJECTIVE,
    "adverb": ADVERB,
    "article": ARTICLE,
    "pronoun": PRONOUN,
    "numeral": NUMERAL,
    "preposition": PREPOSITION,
    "conjunction": CONJUNCTION,
}

# SQL table names
TABLE_NOUN = "greek_nouns"
TABLE_VERB = "greek_verbs"
TABLE_ADJECTIVE = "greek_adjectives"
TABLE_ARTICLE = "greek_articles"
TABLE_PRONOUN = "greek_pronouns"
TABLE_ADVERB = "greek_adverbs"
TABLE_PREPOSITION = "greek_prepositions"
TABLE_CONJUNCTION = "greek_conjunctions"
