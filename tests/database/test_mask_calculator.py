import pytest

from syntaxis.database.mask_calculator import calculate_masks_for_word
from syntaxis.models.enums import Case, Number
from syntaxis.models.enums import PartOfSpeech as POSEnum


def test_calculate_masks_for_noun():
    """Should calculate number_mask and case_mask for noun."""
    masks = calculate_masks_for_word("άνθρωπος", POSEnum.NOUN)

    assert "number_mask" in masks
    assert "case_mask" in masks
    assert masks["number_mask"] > 0  # Should have at least one number
    assert masks["case_mask"] > 0  # Should have at least one case


def test_calculate_masks_for_verb():
    """Should calculate all verb feature masks."""
    masks = calculate_masks_for_word("τρώω", POSEnum.VERB)

    expected_keys = {
        "tense_mask",
        "voice_mask",
        "mood_mask",
        "number_mask",
        "person_mask",
        "case_mask",
    }
    assert set(masks.keys()) == expected_keys

    # All masks except case_mask should have at least one bit set
    # (Greek verbs don't have case)
    for key, value in masks.items():
        if key == "case_mask":
            assert value == 0, "Verbs should have case_mask = 0"
        else:
            assert value > 0, f"{key} should have at least one feature"


def test_calculate_masks_for_adjective():
    """Should calculate number_mask and case_mask for adjective."""
    masks = calculate_masks_for_word("καλός", POSEnum.ADJECTIVE)

    assert "number_mask" in masks
    assert "case_mask" in masks
    assert masks["number_mask"] > 0
    assert masks["case_mask"] > 0


def test_calculate_masks_for_adverb():
    """Should return empty dict for adverb (no features)."""
    masks = calculate_masks_for_word("καλά", POSEnum.ADVERB)

    assert masks == {}
