import pytest

from syntaxis.database.bitmasks import build_mask, enum_to_bit, has_feature
from syntaxis.models.enums import Case, Gender, Number


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


def test_build_mask_combines_single_value():
    """Single enum value should produce its bit."""
    result = build_mask([Number.SINGULAR])
    assert result == 1


def test_build_mask_combines_multiple_values():
    """Multiple enum values should OR together."""
    result = build_mask([Number.SINGULAR, Number.PLURAL])
    assert result == 3  # 1 | 2


def test_build_mask_combines_case_values():
    """Should work with Case enums."""
    result = build_mask([Case.NOMINATIVE, Case.ACCUSATIVE, Case.GENITIVE])
    assert result == 13  # 1 | 4 | 8


def test_build_mask_empty_list():
    """Empty list should produce 0."""
    result = build_mask([])
    assert result == 0


def test_has_feature_returns_true_when_present():
    """Should return True if feature bit is set."""
    mask = 3  # SINGULAR | PLURAL
    assert has_feature(mask, Number.SINGULAR) is True
    assert has_feature(mask, Number.PLURAL) is True


def test_has_feature_returns_false_when_absent():
    """Should return False if feature bit is not set."""
    mask = 1  # Only SINGULAR
    assert has_feature(mask, Number.PLURAL) is False


def test_has_feature_with_case_values():
    """Should work with Case enums."""
    mask = 13  # NOMINATIVE | ACCUSATIVE | GENITIVE
    assert has_feature(mask, Case.NOMINATIVE) is True
    assert has_feature(mask, Case.ACCUSATIVE) is True
    assert has_feature(mask, Case.GENITIVE) is True
    assert has_feature(mask, Case.VOCATIVE) is False
