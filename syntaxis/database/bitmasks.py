"""Mapping constants for database tables and valid features."""

from syntaxis.models import constants as c

# Maps lexical to its valid feature names
VALID_FEATURES = {
    c.NOUN: {c.GENDER, c.NUMBER, c.CASE},
    c.VERB: {c.TENSE, c.VOICE, c.MOOD, c.NUMBER, c.PERSON, c.CASE},
    c.ADJECTIVE: {c.GENDER, c.NUMBER, c.CASE},
    c.ARTICLE: {c.GENDER, c.NUMBER, c.CASE},
    c.PRONOUN: {c.GENDER, c.NUMBER, c.CASE, c.PERSON, c.TYPE},
    c.ADVERB: set(),
    c.PREPOSITION: set(),
    c.CONJUNCTION: set(),
}

LEXICAL_TO_TABLE_MAP = {
    c.NOUN: "greek_nouns",
    c.VERB: "greek_verbs",
    c.ADJECTIVE: "greek_adjectives",
    c.ARTICLE: "greek_articles",
    c.PRONOUN: "greek_pronouns",
    c.ADVERB: "greek_adverbs",
    c.PREPOSITION: "greek_prepositions",
    c.CONJUNCTION: "greek_conjunctions",
}

LEXICAL_CONFIG = {
    c.NOUN: {
        "table": "greek_nouns",
        "fields": [c.LEMMA, c.GENDER, c.NUMBER, c.CASE, "validation_status"],
    },
    c.VERB: {
        "table": "greek_verbs",
        "fields": [
            c.LEMMA,
            "verb_group",
            c.TENSE,
            c.VOICE,
            c.MOOD,
            c.NUMBER,
            c.PERSON,
            c.CASE,
            "validation_status",
        ],
    },
    c.ADJECTIVE: {
        "table": "greek_adjectives",
        "fields": [c.LEMMA, c.GENDER, c.NUMBER, c.CASE, "validation_status"],
    },
    c.ARTICLE: {
        "table": "greek_articles",
        "fields": [c.LEMMA, "type", c.GENDER, c.NUMBER, c.CASE, "validation_status"],
    },
    c.PRONOUN: {
        "table": "greek_pronouns",
        "fields": [
            c.LEMMA,
            c.TYPE,
            c.PERSON,
            c.GENDER,
            c.NUMBER,
            c.CASE,
            "validation_status",
        ],
    },
    c.ADVERB: {
        "table": "greek_adverbs",
        "fields": [c.LEMMA, "validation_status"],
    },
    c.PREPOSITION: {
        "table": "greek_prepositions",
        "fields": [c.LEMMA, "validation_status"],
    },
    c.CONJUNCTION: {
        "table": "greek_conjunctions",
        "fields": [c.LEMMA, "validation_status"],
    },
}
