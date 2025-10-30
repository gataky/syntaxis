"""Integration tests for get_random_word with real Greek words."""

import pytest

from syntaxis.database.manager import LexicalManager
from syntaxis.database.mask_calculator import calculate_masks_for_word
from syntaxis.models.enums import (
    Case,
    Gender,
    Number,
)
from syntaxis.models.enums import PartOfSpeech as POSEnum
from syntaxis.models.enums import (
    Tense,
    Voice,
)


def test_full_workflow_noun():
    """Complete workflow: calculate masks, store word, retrieve with features."""
    manager = LexicalManager()

    # Calculate masks for a Greek noun
    lemma = "άνθρωπος"
    masks = calculate_masks_for_word(lemma, POSEnum.NOUN)

    # Insert word with masks
    conn = manager._conn
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (lemma, "MASCULINE", masks["number_mask"], masks["case_mask"], "validated"),
    )

    # Add English translation
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)", ("person", "NOUN")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (1, 1, "NOUN"),
    )
    conn.commit()

    # Retrieve with features
    result = manager.get_random_word(
        POSEnum.NOUN, number=Number.SINGULAR, case=Case.NOMINATIVE
    )

    assert result is not None
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]

    # Verify forms are populated
    assert result.forms is not None
    assert len(result.forms) > 0
    # Verify the forms contain the expected lemma form
    assert any("άνθρωπος" in str(forms) for forms in result.forms.values())


def test_full_workflow_verb():
    """Complete workflow with verb."""
    manager = LexicalManager()

    lemma = "τρώω"
    masks = calculate_masks_for_word(lemma, POSEnum.VERB)

    conn = manager._conn
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO greek_verbs
        (lemma, tense_mask, voice_mask, mood_mask, number_mask, person_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            lemma,
            masks["tense_mask"],
            masks["voice_mask"],
            masks["mood_mask"],
            masks["number_mask"],
            masks["person_mask"],
            masks["case_mask"],
            "validated",
        ),
    )

    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)", ("eat", "VERB")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (1, 1, "VERB"),
    )
    conn.commit()

    # Retrieve with verb features
    result = manager.get_random_word(
        POSEnum.VERB, tense=Tense.PRESENT, voice=Voice.ACTIVE
    )

    assert result is not None
    assert result.lemma == "τρώω"
    assert result.translations == ["eat"]


def test_no_match_returns_none():
    """Should return None when features don't match any words."""
    manager = LexicalManager()

    # Insert word with only PLURAL
    lemma = "ψαλίδι"
    conn = manager._conn
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (lemma, "NEUTER", 2, 15, "validated"),  # number_mask=2 is only PLURAL
    )
    conn.commit()

    # Request SINGULAR - should return None
    result = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)

    assert result is None
