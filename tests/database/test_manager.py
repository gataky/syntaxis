import sqlite3
import pytest
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeech as POSEnum, Number, Case, Gender
from syntaxis.models.part_of_speech import Noun, Verb


def test_create_word_from_row_creates_noun_with_translations():
    """Should create Noun object with lemma and translations."""
    manager = LexicalManager()

    # Simulate a database row
    conn = manager._conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Insert test data
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, validation_status) VALUES (?, ?, ?)",
        ("άνθρωπος", "MASCULINE", "validated")
    )
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)",
        ("person", "NOUN")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (1, 1, "NOUN")
    )
    conn.commit()

    # Create mock row
    cursor.execute(
        """
        SELECT g.id, g.lemma, GROUP_CONCAT(e.word, '|') as translations
        FROM greek_nouns g
        LEFT JOIN translations t ON t.greek_word_id = g.id AND t.greek_pos_type = 'NOUN'
        LEFT JOIN english_words e ON e.id = t.english_word_id
        WHERE g.id = 1
        GROUP BY g.id
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, POSEnum.NOUN)

    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]
    assert result.forms is not None


def test_create_word_from_row_handles_multiple_translations():
    """Should split pipe-delimited translations."""
    manager = LexicalManager()

    conn = manager._conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO greek_verbs (lemma, validation_status) VALUES (?, ?)",
        ("τρώω", "validated")
    )
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)",
        ("eat", "VERB")
    )
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)",
        ("consume", "VERB")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (1, 1, "VERB")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (2, 1, "VERB")
    )
    conn.commit()

    cursor.execute(
        """
        SELECT g.id, g.lemma, GROUP_CONCAT(e.word, '|') as translations
        FROM greek_verbs g
        LEFT JOIN translations t ON t.greek_word_id = g.id AND t.greek_pos_type = 'VERB'
        LEFT JOIN english_words e ON e.id = t.english_word_id
        WHERE g.id = 1
        GROUP BY g.id
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, POSEnum.VERB)

    assert isinstance(result, Verb)
    assert set(result.translations) == {"eat", "consume"}


def test_create_word_from_row_handles_no_translations():
    """Should set translations to None when no translations exist."""
    manager = LexicalManager()

    conn = manager._conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, validation_status) VALUES (?, ?, ?)",
        ("άνθρωπος", "MASCULINE", "validated")
    )
    conn.commit()

    cursor.execute(
        """
        SELECT g.id, g.lemma, GROUP_CONCAT(e.word, '|') as translations
        FROM greek_nouns g
        LEFT JOIN translations t ON t.greek_word_id = g.id AND t.greek_pos_type = 'NOUN'
        LEFT JOIN english_words e ON e.id = t.english_word_id
        WHERE g.id = 1
        GROUP BY g.id
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, POSEnum.NOUN)

    assert result.translations is None


def test_get_random_word_returns_noun_without_features():
    """Should return a random noun when no features specified."""
    manager = LexicalManager()

    conn = manager._conn
    cursor = conn.cursor()

    # Insert test noun with bitmasks
    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("άνθρωπος", "MASCULINE", 3, 15, "validated")  # All numbers, all cases
    )
    conn.commit()

    result = manager.get_random_word(POSEnum.NOUN)

    assert result is not None
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"


def test_get_random_word_filters_by_single_feature():
    """Should filter words by a single feature."""
    manager = LexicalManager()

    conn = manager._conn
    cursor = conn.cursor()

    # Insert nouns with different features
    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("άνθρωπος", "MASCULINE", 3, 15, "validated")  # Has SINGULAR (bit 1)
    )
    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("ψαλίδι", "NEUTER", 2, 15, "validated")  # Only PLURAL (bit 2), no SINGULAR
    )
    conn.commit()

    # Request SINGULAR - should get άνθρωπος, not ψαλίδι
    result = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)

    assert result is not None
    assert result.lemma == "άνθρωπος"


def test_get_random_word_filters_by_multiple_features():
    """Should filter by multiple features simultaneously."""
    manager = LexicalManager()

    conn = manager._conn
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("άνθρωπος", "MASCULINE", 3, 15, "validated")  # All cases
    )
    cursor.execute(
        """
        INSERT INTO greek_nouns
        (lemma, gender, number_mask, case_mask, validation_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("όνομα", "NEUTER", 3, 1, "validated")  # Only NOMINATIVE
    )
    conn.commit()

    # Request SINGULAR + ACCUSATIVE - should get άνθρωπος (has bit 4)
    result = manager.get_random_word(
        POSEnum.NOUN,
        number=Number.SINGULAR,
        case=Case.ACCUSATIVE
    )

    assert result is not None
    assert result.lemma == "άνθρωπος"


def test_get_random_word_returns_none_when_no_match():
    """Should return None when no words match criteria."""
    manager = LexicalManager()

    result = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)

    assert result is None


def test_get_random_word_raises_error_for_invalid_feature():
    """Should raise ValueError for invalid feature."""
    manager = LexicalManager()

    with pytest.raises(ValueError) as exc_info:
        manager.get_random_word(POSEnum.NOUN, tense="invalid")

    assert "Invalid features" in str(exc_info.value)
    assert "tense" in str(exc_info.value)
