"""Tests for syntaxis constants."""

import pytest


def test_gender_wildcard_constant():
    """Test that GENDER_WILDCARD is defined and has correct value."""
    from syntaxis.lib.constants import GENDER_WILDCARD, GENDER

    assert GENDER_WILDCARD == "*gender*"


def test_number_wildcard_constant():
    """Test that NUMBER_WILDCARD is defined and has correct value."""
    from syntaxis.lib.constants import NUMBER_WILDCARD, NUMBER

    assert NUMBER_WILDCARD == "*number*"


def test_gender_values_includes_wildcard():
    """Test that GENDER_VALUES includes wildcard."""
    from syntaxis.lib.constants import GENDER_VALUES, GENDER_WILDCARD

    assert GENDER_WILDCARD in GENDER_VALUES


def test_number_values_includes_wildcard():
    """Test that NUMBER_VALUES includes wildcard."""
    from syntaxis.lib.constants import NUMBER_VALUES, NUMBER_WILDCARD

    assert NUMBER_WILDCARD in NUMBER_VALUES


def test_wildcard_feature_categories():
    """Test that wildcards map to correct categories."""
    from syntaxis.lib.constants import (
        FEATURE_CATEGORIES,
        GENDER_WILDCARD,
        NUMBER_WILDCARD,
        GENDER,
        NUMBER,
    )

    assert FEATURE_CATEGORIES[GENDER_WILDCARD] == GENDER
    assert FEATURE_CATEGORIES[NUMBER_WILDCARD] == NUMBER
