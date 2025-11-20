"""String constants for syntaxis grammatical features.

These constants define the canonical string representations used throughout
syntaxis. The morpheus module handles translation to/from modern_greek_inflexion.
"""

LEMMA = "lemma"

# Lexical constants (using template-friendly abbreviations)
NOUN = "noun"
VERB = "verb"
ADJECTIVE = "adjective"
ADVERB = "adverb"
ARTICLE = "article"
PRONOUN = "pronoun"
NUMERAL = "numeral"
PREPOSITION = "preposition"
CONJUNCTION = "conjunction"
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
    # DEFINITE,
    INDEFINITE,
}

# Gender constants (MGI abbreviations)
MASCULINE = "masc"
FEMININE = "fem"
NEUTER = "neut"
GENDER_WILDCARD = f"*{GENDER}*"  # Wildcard for random gender selection
GENDER_VALUES = {MASCULINE, FEMININE, NEUTER, GENDER_WILDCARD}

# Number constants (MGI abbreviations)
SINGULAR = "sg"
PLURAL = "pl"
NUMBER_WILDCARD = f"*{NUMBER}*"  # Wildcard for random number selection
NUMBER_VALUES = {SINGULAR, PLURAL, NUMBER_WILDCARD}

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
PERSON_WILDCARD = f"*{PERSON}*"
PERSON_VALUES = {FIRST, SECOND, THIRD, PERSON_WILDCARD}

# Aspect constants (MGI abbreviations)
PERFECT = "perf"
IMPERFECT = "imperf"

WILDCARD_FEATURES = {GENDER_WILDCARD, NUMBER_WILDCARD, PERSON_WILDCARD}

# Feature category mappings from design document
FEATURE_CATEGORIES = {
    # Case
    NOMINATIVE: CASE,
    GENITIVE: CASE,
    ACCUSATIVE: CASE,
    VOCATIVE: CASE,
    # Gender
    MASCULINE: GENDER,
    FEMININE: GENDER,
    NEUTER: GENDER,
    GENDER: GENDER,
    GENDER_WILDCARD: GENDER,
    # Number
    SINGULAR: NUMBER,
    PLURAL: NUMBER,
    NUMBER: NUMBER,
    NUMBER_WILDCARD: NUMBER,
    # Tense
    PRESENT: TENSE,
    AORIST: TENSE,
    PARATATIKOS: TENSE,
    # Voice
    ACTIVE: VOICE,
    PASSIVE: VOICE,
    # Person
    FIRST: PERSON,
    SECOND: PERSON,
    THIRD: PERSON,
    PERSON: PERSON,
    PERSON_WILDCARD: PERSON,
    # Pronoun
    PERSONAL_STRONG: TYPE,
    PERSONAL_WEAK: TYPE,
    DEMONSTRATIVE: TYPE,
    INTERROGATIVE: TYPE,
    POSSESSIVE: TYPE,
    RELATIVE: TYPE,
    DEFINITE: TYPE,
    INDEFINITE: TYPE,
}

VALID_CASE_FEATURES = {
    NOUN:      {NUMBER, CASE, GENDER,                                  },
    ADJECTIVE: {NUMBER, CASE, GENDER,                                  },
    ARTICLE:   {NUMBER, CASE, GENDER,                                  },
    PRONOUN:   {NUMBER, CASE, GENDER, PERSON, TYPE,                    },
    VERB:      {NUMBER, CASE,         PERSON,       TENSE, VOICE, MOOD,},

    ADVERB:      set(),
    PREPOSITION: set(),
    CONJUNCTION: set(),
}


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

LEXICAL_TO_TABLE_MAP = {
    NOUN: TABLE_NOUN,
    VERB: TABLE_VERB,
    ADJECTIVE: TABLE_ADJECTIVE,
    ARTICLE: TABLE_ARTICLE,
    PRONOUN: TABLE_PRONOUN,
    ADVERB: TABLE_ADVERB,
    PREPOSITION: TABLE_PREPOSITION,
    CONJUNCTION: TABLE_CONJUNCTION,
}

VALIDATION_STATUS = "validation_status"

_table = "table"
_fields = "fields"

LEXICAL_CONFIG = {
    NOUN: {
        _table: TABLE_NOUN,
        _fields: [LEMMA, GENDER, NUMBER, CASE, VALIDATION_STATUS],
    },
    VERB: {
        _table: TABLE_VERB,
        _fields: [
            LEMMA,
            "verb_group",
            TENSE,
            VOICE,
            MOOD,
            NUMBER,
            PERSON,
            CASE,
            VALIDATION_STATUS,
        ],
    },
    ADJECTIVE: {
        _table: TABLE_ADJECTIVE,
        _fields: [LEMMA, GENDER, NUMBER, CASE, VALIDATION_STATUS],
    },
    ARTICLE: {
        _table: TABLE_ARTICLE,
        _fields: [LEMMA, TYPE, GENDER, NUMBER, CASE, VALIDATION_STATUS],
    },
    PRONOUN: {
        _table: TABLE_PRONOUN,
        _fields: [
            LEMMA,
            TYPE,
            PERSON,
            GENDER,
            NUMBER,
            CASE,
            VALIDATION_STATUS,
        ],
    },
    ADVERB: {
        _table: TABLE_ADVERB,
        _fields: [LEMMA, VALIDATION_STATUS],
    },
    PREPOSITION: {
        _table: TABLE_PREPOSITION,
        _fields: [LEMMA, VALIDATION_STATUS],
    },
    CONJUNCTION: {
        _table: TABLE_CONJUNCTION,
        _fields: [LEMMA, VALIDATION_STATUS],
    },
}
