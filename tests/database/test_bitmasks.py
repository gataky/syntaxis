import pytest
from syntaxis.database.bitmasks import enum_to_bit, build_mask, has_feature
from syntaxis.models.enums import Number, Case, Gender


def test_enum_to_bit_converts_first_enum_to_one():
    """First enum member should map to bit position 1."""
    result = enum_to_bit(Number.SINGULAR)
    assert result == 1


def test_enum_to_bit_converts_second_enum_to_two():
    """Second enum member should map to bit position 2."""
    result = enum_to_bit(Number.PLURAL)
    assert result == 2


def test_enum_to_bit_converts_case_enums():
    """Case enum members should map to powers of 2."""
    assert enum_to_bit(Case.NOMINATIVE) == 1
    assert enum_to_bit(Case.VOCATIVE) == 2
    assert enum_to_bit(Case.ACCUSATIVE) == 4
    assert enum_to_bit(Case.GENITIVE) == 8
