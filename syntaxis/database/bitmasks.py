"""Mapping constants for database tables and valid features."""

from syntaxis.models import constants as c

# Maps POS to its valid feature names
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

# Maps POS string to database table name
POS_TO_TABLE_MAP: dict[str, str] = {
    c.ADJECTIVE: c.TABLE_ADJECTIVE,
    c.ADVERB: c.TABLE_ADVERB,
    c.ARTICLE: c.TABLE_ARTICLE,
    c.CONJUNCTION: c.TABLE_CONJUNCTION,
    c.NOUN: c.TABLE_NOUN,
    c.PREPOSITION: c.TABLE_PREPOSITION,
    c.PRONOUN: c.TABLE_PRONOUN,
    c.VERB: c.TABLE_VERB,
}
