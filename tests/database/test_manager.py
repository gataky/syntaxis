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
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "validated"),
    )
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)", ("person", "noun")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_lemma, greek_pos_type) VALUES (?, ?, ?)",
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
                WHERE t.greek_lemma = g.lemma AND t.greek_pos_type = 'noun') as translations
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
        "INSERT INTO greek_verbs (lemma, tense, voice, mood, number, person, case_name, validation_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("τρώω", "pres", "act", "ind", "sg", "1", None, "validated"),
    )
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)", ("eat", "verb")
    )
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)", ("consume", "verb")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_lemma, greek_pos_type) VALUES (?, ?, ?)",
        (1, "τρώω", "verb"),
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_lemma, greek_pos_type) VALUES (?, ?, ?)",
        (2, "τρώω", "verb"),
    )
    conn.commit()

    cursor.execute(
        """
        SELECT g.lemma,
               (SELECT GROUP_CONCAT(e.word, '|')
                FROM translations t
                JOIN english_words e ON e.id = t.english_word_id
                WHERE t.greek_lemma = g.lemma AND t.greek_pos_type = 'verb') as translations
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
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "validated"),
    )
    conn.commit()

    cursor.execute(
        """
        SELECT g.lemma,
               (SELECT GROUP_CONCAT(e.word, '|')
                FROM translations t
                JOIN english_words e ON e.id = t.english_word_id
                WHERE t.greek_lemma = g.lemma AND t.greek_pos_type = 'noun') as translations
        FROM greek_nouns g
        WHERE g.lemma = 'άνθρωπος'
        LIMIT 1
        """
    )
    row = cursor.fetchone()

    result = manager._create_word_from_row(row, c.NOUN)

    assert result.translations is None


def test_get_random_word_returns_noun_without_features():
    """Should return a random noun when no features specified."""
    manager = Database()

    conn = manager._conn
    cursor = conn.cursor()

    # Insert test noun rows (one per feature combination)
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "validated"),
    )
    conn.commit()

    result = manager.get_random_word(c.NOUN)

    assert result is not None
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"


def test_get_random_word_filters_by_single_feature():
    """Should filter words by a single feature."""
    manager = Database()

    conn = manager._conn
    cursor = conn.cursor()

    # Insert nouns with different features
    # άνθρωπος has SINGULAR
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "validated"),
    )
    # ψαλίδι only has PLURAL, no SINGULAR rows
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("ψαλίδι", "neut", "pl", "nom", "validated"),
    )
    conn.commit()

    # Request SINGULAR - should get άνθρωπος, not ψαλίδι
    result = manager.get_random_word(c.NOUN, number=c.SINGULAR)

    assert result is not None
    assert result.lemma == "άνθρωπος"


def test_get_random_word_filters_by_multiple_features():
    """Should filter by multiple features simultaneously."""
    manager = Database()

    conn = manager._conn
    cursor = conn.cursor()

    # άνθρωπος has all cases including ACCUSATIVE
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "acc", "validated"),
    )
    # όνομα only has NOMINATIVE
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("όνομα", "neut", "sg", "nom", "validated"),
    )
    conn.commit()

    # Request SINGULAR + ACCUSATIVE - should get άνθρωπος (not όνομα)
    result = manager.get_random_word(c.NOUN, number=c.SINGULAR, case_name=c.ACCUSATIVE)

    assert result is not None
    assert result.lemma == "άνθρωπος"


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
        manager.add_word(lemma="άνθρωπος", translations=[], pos=c.NOUN)

    assert "At least one translation required" in str(exc_info.value)


def test_add_word_raises_error_for_none_translations():
    """Should raise ValueError when translations is None."""
    manager = Database()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="άνθρωπος", translations=[], pos=c.NOUN)

    assert "At least one translation required" in str(exc_info.value)


def test_add_word_raises_error_for_empty_lemma():
    """Should raise ValueError when lemma is empty string."""
    manager = Database()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="", translations=["person"], pos=c.NOUN)

    assert "Lemma cannot be empty" in str(exc_info.value)


def test_add_word_raises_error_for_duplicate_lemma():
    """Should raise ValueError when word already exists."""
    manager = Database()

    # Manually insert a word (at least one row with this lemma)
    cursor = manager._conn.cursor()
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, number, case_name, validation_status) VALUES (?, ?, ?, ?, ?)",
        ("άνθρωπος", "masc", "sg", "nom", "VALID"),
    )
    manager._conn.commit()

    # Try to add the same word
    with pytest.raises(ValueError) as exc_info:
        manager.add_word(lemma="άνθρωπος", translations=["person"], pos=c.NOUN)

    assert "already exists" in str(exc_info.value)
    assert "άνθρωπος" in str(exc_info.value)


def test_add_word_successfully_adds_noun_with_single_translation():
    """Should add noun with translation and return Word object."""
    manager = Database()

    result = manager.add_word(lemma="άνθρωπος", translations=["person"], pos=c.NOUN)

    # Verify return value
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]
    assert result.forms is not None  # Morpheus generated forms

    # Verify database state
    cursor = manager._conn.cursor()

    # Check Greek word inserted (multiple rows expected - one per feature combination)
    rows = cursor.execute(
        "SELECT lemma, gender, number, case_name, validation_status FROM greek_nouns WHERE lemma = ?",
        ("άνθρωπος",),
    ).fetchall()
    assert (
        len(rows) > 0
    )  # Should have multiple rows (one per valid feature combination)
    # Check first row as sample
    assert rows[0][0] == "άνθρωπος"
    assert rows[0][1] == "masc"  # Inferred from forms
    assert rows[0][2] in ["sg", "pl"]  # Has explicit number
    assert rows[0][3] in ["nom", "gen", "acc", "voc"]  # Has explicit case
    assert rows[0][4] == "VALID"

    # Check English word inserted
    eng_row = cursor.execute(
        "SELECT word, pos_type FROM english_words WHERE word = ?", ("person",)
    ).fetchone()
    assert eng_row is not None
    assert eng_row[0] == "person"
    assert eng_row[1] == "noun"

    # Check translation link created (linked by lemma, not row ID)
    trans_row = cursor.execute(
        "SELECT greek_lemma, greek_pos_type FROM translations WHERE greek_pos_type = ?",
        ("noun",),
    ).fetchone()
    assert trans_row is not None
    assert trans_row[0] == "άνθρωπος"


def test_get_words_by_english_returns_empty_list_for_nonexistent_word():
    """Should return empty list when English word not found."""
    manager = Database()

    result = manager.get_words_by_english("nonexistent")

    assert result == []


def test_get_words_by_english_finds_single_noun():
    """Should find Greek noun by English translation."""
    manager = Database()

    # Add a word using add_word
    manager.add_word(lemma="άνθρωπος", translations=["person"], pos=c.NOUN)

    result = manager.get_words_by_english("person")

    assert len(result) == 1
    assert isinstance(result[0], Noun)
    assert result[0].lemma == "άνθρωπος"
    assert result[0].translations is not None
    assert "person" in result[0].translations


def test_get_words_by_english_finds_multiple_greek_words():
    """Should find multiple Greek words that share same English translation."""
    manager = Database()

    # Add two different Greek words with the same English translation
    manager.add_word(lemma="άνθρωπος", translations=["person", "human"], pos=c.NOUN)
    manager.add_word(lemma="άνδρας", translations=["man", "person"], pos=c.NOUN)

    result = manager.get_words_by_english("person")

    assert len(result) == 2
    lemmas = {word.lemma for word in result}
    assert lemmas == {"άνθρωπος", "άνδρας"}

    # Both should have "person" in their translations
    for word in result:
        assert "person" in word.translations


def test_get_words_by_english_filters_by_pos():
    """Should filter results by part of speech when specified."""
    manager = Database()

    # Add a noun and verb with same English translation
    manager.add_word(lemma="άνθρωπος", translations=["person"], pos=c.NOUN)
    manager.add_word(lemma="τρώω", translations=["eat"], pos=c.VERB)

    # Search without POS filter
    result_all = manager.get_words_by_english("person")
    assert len(result_all) == 1
    assert isinstance(result_all[0], Noun)

    # Search with NOUN filter
    result_noun = manager.get_words_by_english("person", pos=c.NOUN)
    assert len(result_noun) == 1
    assert isinstance(result_noun[0], Noun)

    # Search with VERB filter (should find nothing)
    result_verb = manager.get_words_by_english("person", pos=c.VERB)
    assert len(result_verb) == 0


def test_get_words_by_english_handles_word_with_multiple_translations():
    """Should find word even when it has multiple English translations."""
    manager = Database()

    manager.add_word(
        lemma="άνθρωπος", translations=["person", "human", "man"], pos=c.NOUN
    )

    # Search by each translation
    for english in ["person", "human", "man"]:
        result = manager.get_words_by_english(english)
        assert len(result) == 1
        assert result[0].lemma == "άνθρωπος"
        assert set(result[0].translations) == {"person", "human", "man"}
