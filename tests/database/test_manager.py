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


def test_add_word_raises_error_for_empty_translations():
    """Should raise ValueError when translations list is empty."""
    manager = LexicalManager()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(
            lemma="άνθρωπος",
            translations=[],
            pos=POSEnum.NOUN
        )

    assert "At least one translation required" in str(exc_info.value)


def test_add_word_raises_error_for_none_translations():
    """Should raise ValueError when translations is None."""
    manager = LexicalManager()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(
            lemma="άνθρωπος",
            translations=None,
            pos=POSEnum.NOUN
        )

    assert "At least one translation required" in str(exc_info.value)


def test_add_word_raises_error_for_empty_lemma():
    """Should raise ValueError when lemma is empty string."""
    manager = LexicalManager()

    with pytest.raises(ValueError) as exc_info:
        manager.add_word(
            lemma="",
            translations=["person"],
            pos=POSEnum.NOUN
        )

    assert "Lemma cannot be empty" in str(exc_info.value)


def test_add_word_raises_error_for_duplicate_lemma():
    """Should raise ValueError when word already exists."""
    manager = LexicalManager()

    # Manually insert a word
    cursor = manager._conn.cursor()
    cursor.execute(
        "INSERT INTO greek_nouns (lemma, gender, validation_status) VALUES (?, ?, ?)",
        ("άνθρωπος", "MASCULINE", "VALID")
    )
    manager._conn.commit()

    # Try to add the same word
    with pytest.raises(ValueError) as exc_info:
        manager.add_word(
            lemma="άνθρωπος",
            translations=["person"],
            pos=POSEnum.NOUN
        )

    assert "already exists" in str(exc_info.value)
    assert "άνθρωπος" in str(exc_info.value)


def test_add_word_successfully_adds_noun_with_single_translation():
    """Should add noun with translation and return Word object."""
    manager = LexicalManager()

    result = manager.add_word(
        lemma="άνθρωπος",
        translations=["person"],
        pos=POSEnum.NOUN
    )

    # Verify return value
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]
    assert result.forms is not None  # Morpheus generated forms

    # Verify database state
    cursor = manager._conn.cursor()

    # Check Greek word inserted
    row = cursor.execute(
        "SELECT lemma, gender, number_mask, case_mask, validation_status FROM greek_nouns WHERE lemma = ?",
        ("άνθρωπος",)
    ).fetchone()
    assert row is not None
    assert row[0] == "άνθρωπος"
    assert row[1] == "MASCULINE"  # Inferred from forms
    assert row[2] > 0  # number_mask calculated
    assert row[3] > 0  # case_mask calculated
    assert row[4] == "VALID"

    # Check English word inserted
    eng_row = cursor.execute(
        "SELECT word, pos_type FROM english_words WHERE word = ?",
        ("person",)
    ).fetchone()
    assert eng_row is not None
    assert eng_row[0] == "person"
    assert eng_row[1] == "NOUN"

    # Check translation link created
    trans_row = cursor.execute(
        "SELECT * FROM translations WHERE greek_pos_type = ?",
        ("NOUN",)
    ).fetchone()
    assert trans_row is not None


def test_get_words_by_english_returns_empty_list_for_nonexistent_word():
    """Should return empty list when English word not found."""
    manager = LexicalManager()

    result = manager.get_words_by_english("nonexistent")

    assert result == []


def test_get_words_by_english_finds_single_noun():
    """Should find Greek noun by English translation."""
    manager = LexicalManager()

    # Add a word using add_word
    manager.add_word(
        lemma="άνθρωπος",
        translations=["person"],
        pos=POSEnum.NOUN
    )

    result = manager.get_words_by_english("person")

    assert len(result) == 1
    assert isinstance(result[0], Noun)
    assert result[0].lemma == "άνθρωπος"
    assert "person" in result[0].translations


def test_get_words_by_english_finds_multiple_greek_words():
    """Should find multiple Greek words that share same English translation."""
    manager = LexicalManager()

    # Add two different Greek words with the same English translation
    manager.add_word(
        lemma="άνθρωπος",
        translations=["person", "human"],
        pos=POSEnum.NOUN
    )
    manager.add_word(
        lemma="άνδρας",
        translations=["man", "person"],
        pos=POSEnum.NOUN
    )

    result = manager.get_words_by_english("person")

    assert len(result) == 2
    lemmas = {word.lemma for word in result}
    assert lemmas == {"άνθρωπος", "άνδρας"}

    # Both should have "person" in their translations
    for word in result:
        assert "person" in word.translations


def test_get_words_by_english_filters_by_pos():
    """Should filter results by part of speech when specified."""
    manager = LexicalManager()

    # Add a noun and verb with same English translation
    manager.add_word(
        lemma="άνθρωπος",
        translations=["person"],
        pos=POSEnum.NOUN
    )
    manager.add_word(
        lemma="τρώω",
        translations=["eat"],
        pos=POSEnum.VERB
    )

    # Search without POS filter
    result_all = manager.get_words_by_english("person")
    assert len(result_all) == 1
    assert isinstance(result_all[0], Noun)

    # Search with NOUN filter
    result_noun = manager.get_words_by_english("person", pos=POSEnum.NOUN)
    assert len(result_noun) == 1
    assert isinstance(result_noun[0], Noun)

    # Search with VERB filter (should find nothing)
    result_verb = manager.get_words_by_english("person", pos=POSEnum.VERB)
    assert len(result_verb) == 0


def test_get_words_by_english_handles_word_with_multiple_translations():
    """Should find word even when it has multiple English translations."""
    manager = LexicalManager()

    manager.add_word(
        lemma="άνθρωπος",
        translations=["person", "human", "man"],
        pos=POSEnum.NOUN
    )

    # Search by each translation
    for english in ["person", "human", "man"]:
        result = manager.get_words_by_english(english)
        assert len(result) == 1
        assert result[0].lemma == "άνθρωπος"
        assert set(result[0].translations) == {"person", "human", "man"}
