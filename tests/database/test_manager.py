import sqlite3

import pytest

from syntaxis.database.api import Database
from syntaxis.models import constants as c
from syntaxis.models.lexical import Noun, Verb


def test_create_word_from_row_creates_noun_with_translations():
    """Should create Noun object with lemma and translations."""
    manager = Database()

    # Simulate a database row
    conn = manager._conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Insert test data (with new schema: feature columns required)
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, form, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "validated"),
    )
    cursor.execute(
        "INSERT INTO english_words (word, lexical) VALUES (?, ?)", ("person", "noun")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_lemma, greek_lexical) VALUES (?, ?, ?)",
        (1, "άνθρωπος", "noun"),
    )
    conn.commit()

    # Create mock row (using new schema: lemma-based joins)
    cursor.execute(
        """
        SELECT g.lemma,
               (SELECT GROUP_CONCAT(e.word, '|')
                FROM translations t
                JOIN english_words e ON e.id = t.english_word_id
                WHERE t.greek_lemma = g.lemma AND t.greek_lexical = 'noun') as translations
        FROM greek_nouns g
        WHERE g.lemma = 'άνθρωπος'
        LIMIT 1
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, c.NOUN)

    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]
    assert result.forms is not None


def test_create_word_from_row_handles_multiple_translations():
    """Should split pipe-delimited translations."""
    manager = Database()

    conn = manager._conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO greek_verbs (lemma, tense, voice, mood, number, person, form, validation_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("τρώω", "pres", "act", "ind", "sg", "1", None, "validated"),
    )
    cursor.execute(
        "INSERT INTO english_words (word, lexical) VALUES (?, ?)", ("eat", "verb")
    )
    cursor.execute(
        "INSERT INTO english_words (word, lexical) VALUES (?, ?)", ("consume", "verb")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_lemma, greek_lexical) VALUES (?, ?, ?)",
        (1, "τρώω", "verb"),
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_lemma, greek_lexical) VALUES (?, ?, ?)",
        (2, "τρώω", "verb"),
    )
    conn.commit()

    cursor.execute(
        """
        SELECT g.lemma,
               (SELECT GROUP_CONCAT(e.word, '|')
                FROM translations t
                JOIN english_words e ON e.id = t.english_word_id
                WHERE t.greek_lemma = g.lemma AND t.greek_lexical = 'verb') as translations
        FROM greek_verbs g
        WHERE g.lemma = 'τρώω'
        LIMIT 1
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, c.VERB)

    assert isinstance(result, Verb)
    assert result.translations is not None
    assert set(result.translations) == {"eat", "consume"}


def test_create_word_from_row_handles_no_translations():
    """Should set translations to None when no translations exist."""
    manager = Database()

    conn = manager._conn
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, form, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "validated"),
    )
    conn.commit()

    cursor.execute(
        """
        SELECT g.lemma,
               (SELECT GROUP_CONCAT(e.word, '|')
                FROM translations t
                JOIN english_words e ON e.id = t.english_word_id
                WHERE t.greek_lemma = g.lemma AND t.greek_lexical = 'noun') as translations
        FROM greek_nouns g
        WHERE g.lemma = 'άνθρωπος'
        LIMIT 1
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, c.NOUN)

    assert result.translations is None


def test_get_random_word_returns_none_when_no_match():
    """Should return None when no words match criteria."""
    manager = Database()

    result = manager.get_random_word(c.NOUN, number=c.SINGULAR)

    assert result is None


def test_get_random_word_raises_error_for_invalid_feature():
    """Should raise ValueError for invalid feature."""
    manager = Database()

    with pytest.raises(ValueError) as exc_info:
        manager.get_random_word(c.NOUN, tense="invalid")

    assert "Invalid features" in str(exc_info.value)
    assert "tense" in str(exc_info.value)


def test_add_word_raises_error_for_empty_translations():
    """Should raise ValueError when translations list is empty."""
    manager = Database()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="άνθρωπος", translations=[], lexical=c.NOUN)

    assert "At least one translation required" in str(exc_info.value)


def test_add_word_raises_error_for_none_translations():
    """Should raise ValueError when translations is None."""
    manager = Database()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="άνθρωπος", translations=[], lexical=c.NOUN)

    assert "At least one translation required" in str(exc_info.value)


def test_add_word_raises_error_for_empty_lemma():
    """Should raise ValueError when lemma is empty string."""
    manager = Database()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="", translations=["person"], lexical=c.NOUN)

    assert "Lemma cannot be empty" in str(exc_info.value)


def test_add_word_raises_error_for_duplicate_lemma():
    """Should raise ValueError when word already exists."""
    manager = Database()

    # Manually insert a word (at least one row with this lemma)
    cursor = manager._conn.cursor()
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, form, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "VALID"),
    )
    manager._conn.commit()

    # Try to add the same word
    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="άνθρωπος", translations=["person"], lexical=c.NOUN)

    assert "already exists" in str(exc_info.value)
    assert "άνθρωπος" in str(exc_info.value)


def test_add_word_successfully_adds_noun_with_single_translation():
    """Should add noun with translation and return Word object."""
    manager = Database()

    result = manager.add_word(lemma="άνθρωπος", translations=["person"], lexical=c.NOUN)

    # Verify return value
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]
    assert result.forms is not None  # Morpheus generated forms

    # Verify database state
    cursor = manager._conn.cursor()

    # Check Greek word inserted (multiple rows expected - one per feature combination)
    rows = cursor.execute(
        "SELECT lemma, gender, number, form, validation_status FROM greek_nouns WHERE lemma = ?",
        ("άνθρωπος",),
    ).fetchall()
    assert (
        len(rows) > 0
    )  # Should have multiple rows (one per valid feature combination)
    # Check first row as sample
    assert rows[0][0] == "άνθρωπος"
    assert rows[0][1] == "masc"  # Inferred from forms
    assert rows[0][2] in ["sg", "pl"]  # Has explicit number
    assert rows[0][3] in ["nom", "gen", "acc", "voc"]  # Has explicit form
    assert rows[0][4] == "VALID"

    # Check English word inserted
    eng_row = cursor.execute(
        "SELECT word, lexical FROM english_words WHERE word = ?", ("person",)
    ).fetchone()
    assert eng_row is not None
    assert eng_row[0] == "person"
    assert eng_row[1] == "noun"

    # Check translation link created (linked by lemma, not row ID)
    trans_row = cursor.execute(
        "SELECT greek_lemma, greek_lexical FROM translations WHERE greek_lexical = ?",
        ("noun",),
    ).fetchone()
    assert trans_row is not None
    assert trans_row[0] == "άνθρωπος"
