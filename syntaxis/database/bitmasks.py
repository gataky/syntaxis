"""Bitmask utilities for feature-based word filtering."""

from enum import Enum
from typing import Iterable


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
