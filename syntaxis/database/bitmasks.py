"""Mapping constants for database tables and valid features."""

from syntaxis.models.enums import PartOfSpeech as POSEnum

# Maps POS to its valid feature names
VALID_FEATURES: dict[POSEnum, set[str]] = {
    POSEnum.NOUN: {"gender", "number", "case_name"},
    POSEnum.VERB: {"tense", "voice", "mood", "number", "person", "case_name"},
    POSEnum.ADJECTIVE: {"gender", "number", "case_name"},
    POSEnum.ARTICLE: {"gender", "number", "case_name"},
    POSEnum.PRONOUN: {"gender", "number", "case_name", "person", "type"},
    POSEnum.ADVERB: set(),
    POSEnum.PREPOSITION: set(),
    POSEnum.CONJUNCTION: set(),
}

# Maps POS enum to database table name
POS_TO_TABLE_MAP: dict[POSEnum, str] = {
    POSEnum.NOUN: "greek_nouns",
    POSEnum.VERB: "greek_verbs",
    POSEnum.ADJECTIVE: "greek_adjectives",
    POSEnum.ARTICLE: "greek_articles",
    POSEnum.PRONOUN: "greek_pronouns",
    POSEnum.ADVERB: "greek_adverbs",
    POSEnum.PREPOSITION: "greek_prepositions",
    POSEnum.CONJUNCTION: "greek_conjunctions",
}
