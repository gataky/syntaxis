"""Mapping constants for database tables and valid features."""

from syntaxis.models import constants as c

# Maps POS to its valid feature names
VALID_FEATURES: dict[str, set[str]] = {
    c.NOUN: {"gender", "number", "case_name"},
    c.VERB: {"tense", "voice", "mood", "number", "person", "case_name"},
    c.ADJECTIVE: {"gender", "number", "case_name"},
    c.ARTICLE: {"gender", "number", "case_name"},
    c.PRONOUN: {"gender", "number", "case_name", "person", "type"},
    c.ADVERB: set(),
    c.PREPOSITION: set(),
    c.CONJUNCTION: set(),
}

# Maps POS string to database table name
POS_TO_TABLE_MAP: dict[str, str] = {
    c.NOUN: "greek_nouns",
    c.VERB: "greek_verbs",
    c.ADJECTIVE: "greek_adjectives",
    c.ARTICLE: "greek_articles",
    c.PRONOUN: "greek_pronouns",
    c.ADVERB: "greek_adverbs",
    c.PREPOSITION: "greek_prepositions",
    c.CONJUNCTION: "greek_conjunctions",
}
