"""String constants for syntaxis grammatical features.

These constants define the canonical string representations used throughout
syntaxis. The morpheus module handles translation to/from modern_greek_inflexion.
"""

LEMMA = "lemma"

# Lexical constants (using template-friendly abbreviations)
NOUN = "noun"
VERB = "verb"
ADJECTIVE = "adj"
ADVERB = "adv"
ARTICLE = "article"
PRONOUN = "pronoun"
NUMERAL = "numeral"
PREPOSITION = "prep"
CONJUNCTION = "conj"
LEXICAL_VALUES = {
    NOUN,
    VERB,
    ADJECTIVE,
    ADVERB,
    ARTICLE,
    PRONOUN,
    NUMERAL,
    PREPOSITION,
    CONJUNCTION,
}

# Lexical features
GENDER = "gender"
NUMBER = "number"
CASE = "case"
TENSE = "tense"
VOICE = "voice"
MOOD = "mood"
PERSON = "person"
TYPE = "type"
LEXICAL_FEATURES = {GENDER, NUMBER, CASE, TENSE, VOICE, MOOD, PERSON, TYPE}


# Pronoun types
PERSONAL_STRONG = "personal_strong"
PERSONAL_WEAK = "personal_weak"
DEMONSTRATIVE = "demonstrative"
INTERROGATIVE = "interrogative"
POSSESSIVE = "possessive"
RELATIVE = "relative"
DEFINITE = "definite"
INDEFINITE = "indefinite"
PRONOUN_TYPES = {
    PERSONAL_STRONG,
    PERSONAL_WEAK,
    DEMONSTRATIVE,
    INTERROGATIVE,
    POSSESSIVE,
    RELATIVE,
    DEFINITE,
    INDEFINITE,
}

# Gender constants (MGI abbreviations)
MASCULINE = "masc"
FEMININE = "fem"
NEUTER = "neut"
GENDER_VALUES = {MASCULINE, FEMININE, NEUTER}

# Number constants (MGI abbreviations)
SINGULAR = "sg"
PLURAL = "pl"
NUMBER_VALUES = {SINGULAR, PLURAL}

# Case constants (MGI abbreviations)
NOMINATIVE = "nom"
ACCUSATIVE = "acc"
GENITIVE = "gen"
VOCATIVE = "voc"
CASE_VALUES = {NOMINATIVE, ACCUSATIVE, GENITIVE, VOCATIVE}

# Tense constants (MGI full names)
PRESENT = "present"
AORIST = "aorist"
PARATATIKOS = "paratatikos"
FUTURE = "future c"
FUTURE_SIMPLE = "future s"
TENSE_VALUES = {PRESENT, AORIST, PARATATIKOS}

# Voice constants (MGI full names)
ACTIVE = "active"
PASSIVE = "passive"
VOICE_VALUES = {ACTIVE, PASSIVE}

# Mood constants (MGI abbreviations)
INDICATIVE = "ind"
IMPERATIVE = "imp"
MOOD_VALUES = {INDICATIVE, IMPERATIVE}

# Person constants (MGI abbreviations)
FIRST = "pri"
SECOND = "sec"
THIRD = "ter"
PERSON_VALUES = {FIRST, SECOND, THIRD}

# Aspect constants (MGI abbreviations)
PERFECT = "perf"
IMPERFECT = "imperf"

# Mapping between CSV dictionary and internal lexical types.
# TODO: do we really need this? Perhaps just force the csv to follow conventions here.
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
