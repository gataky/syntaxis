import sqlite3
import pytest
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeech as POSEnum
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
