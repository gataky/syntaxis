"""Mapping constants for database tables and valid features."""

from syntaxis.models import constants as c

# Maps lexical to its valid feature names
VALID_FEATURES: dict[str, set[str]] = {
    c.NOUN: {c.GENDER, c.NUMBER, c.FORM},
    c.VERB: {c.TENSE, c.VOICE, c.MOOD, c.NUMBER, c.PERSON, c.FORM},
    c.ADJECTIVE: {c.GENDER, c.NUMBER, c.FORM},
    c.ARTICLE: {c.GENDER, c.NUMBER, c.FORM},
    c.PRONOUN: {c.GENDER, c.NUMBER, c.FORM, c.PERSON, c.TYPE},
    c.ADVERB: set(),
    c.PREPOSITION: set(),
    c.CONJUNCTION: set(),
}

# Maps lexical string to database table name
LEXICAL_TO_TABLE_MAP: dict[str, str] = {
    c.ADJECTIVE: c.TABLE_ADJECTIVE,
    c.ADVERB: c.TABLE_ADVERB,
    c.ARTICLE: c.TABLE_ARTICLE,
    c.CONJUNCTION: c.TABLE_CONJUNCTION,
    c.NOUN: c.TABLE_NOUN,
    c.PREPOSITION: c.TABLE_PREPOSITION,
    c.PRONOUN: c.TABLE_PRONOUN,
    c.VERB: c.TABLE_VERB,
}

LEXICAL_CONFIG = {
    c.NOUN: {
        "table": c.TABLE_NOUN,
        "fields": [c.LEMMA, c.GENDER, c.NUMBER, c.FORM, "validation_status"],
    },
    c.VERB: {
        "table": c.TABLE_VERB,
        "fields": [
            c.LEMMA,
            "verb_group",
            c.TENSE,
            c.VOICE,
            c.MOOD,
            c.NUMBER,
            c.PERSON,
            c.FORM,
            "validation_status",
        ],
    },
    c.ADJECTIVE: {
        "table": c.TABLE_ADJECTIVE,
        "fields": [c.LEMMA, c.GENDER, c.NUMBER, c.FORM, "validation_status"],
    },
    c.ARTICLE: {
        "table": c.TABLE_ARTICLE,
        "fields": [c.LEMMA, c.GENDER, c.NUMBER, c.FORM, "validation_status"],
    },
    c.PRONOUN: {
        "table": c.TABLE_PRONOUN,
        "fields": [
            c.LEMMA,
            c.TYPE,
            c.PERSON,
            c.GENDER,
            c.NUMBER,
            c.FORM,
            "validation_status",
        ],
    },
    c.ADVERB: {
        "table": c.TABLE_ADVERB,
        "fields": [c.LEMMA, "validation_status"],
    },
    c.PREPOSITION: {
        "table": c.TABLE_PREPOSITION,
        "fields": [c.LEMMA, "validation_status"],
    },
    c.CONJUNCTION: {
        "table": c.TABLE_CONJUNCTION,
        "fields": [c.LEMMA, "validation_status"],
    },
}
