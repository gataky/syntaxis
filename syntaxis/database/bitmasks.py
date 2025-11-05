"""Bitmask utilities for feature-based word filtering."""

from enum import Enum
from typing import Iterable

from syntaxis.models.enums import PartOfSpeech as POSEnum


def enum_to_bit(enum_value: Enum) -> int:
    """Convert enum to its bit position (1, 2, 4, 8, ...).

    Args:
        enum_value: Enum member to convert

    Returns:
        Power of 2 corresponding to enum's position (1 << position)

    Examples:
        >>> enum_to_bit(Number.SINGULAR)  # First member
        1
        >>> enum_to_bit(Number.PLURAL)  # Second member
        2
        >>> enum_to_bit(Case.ACCUSATIVE)  # Third member
        4
    """
    members = list(type(enum_value).__members__.values())
    position = members.index(enum_value)
    return 1 << position


def build_mask(enum_values: Iterable[Enum]) -> int:
    """Combine multiple enum values into a bitmask.

    Args:
        enum_values: Iterable of enum members to combine

    Returns:
        Integer bitmask with bits set for each enum value

    Examples:
        >>> build_mask([Number.SINGULAR, Number.PLURAL])
        3  # 1 | 2
        >>> build_mask([Case.NOMINATIVE, Case.ACCUSATIVE])
        5  # 1 | 4
    """
    mask = 0
    for value in enum_values:
        mask |= enum_to_bit(value)
    return mask


def has_feature(mask: int, feature: Enum) -> bool:
    """Check if a bitmask contains a specific feature.

    Args:
        mask: Integer bitmask to check
        feature: Enum member to look for

    Returns:
        True if the feature's bit is set in the mask, False otherwise

    Examples:
        >>> has_feature(3, Number.SINGULAR)  # 3 = SINGULAR | PLURAL
        True
        >>> has_feature(1, Number.PLURAL)  # 1 = only SINGULAR
        False
    """
    return (mask & enum_to_bit(feature)) != 0


# Maps POS to its valid feature names
VALID_FEATURES: dict[POSEnum, set[str]] = {
    POSEnum.NOUN: {"gender", "number", "case"},
    POSEnum.VERB: {"tense", "voice", "mood", "number", "person", "case"},
    POSEnum.ADJECTIVE: {"gender", "number", "case"},
    POSEnum.ARTICLE: {"gender", "number", "case"},
    POSEnum.PRONOUN: {"gender", "number", "case"},
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
