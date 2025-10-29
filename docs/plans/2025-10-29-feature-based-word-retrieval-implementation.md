# Feature-Based Word Retrieval Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement `get_random_word()` method with bitmask-based feature filtering for efficient word retrieval.

**Architecture:** Use separate INTEGER bitmask columns per feature dimension in database tables. Each bit represents availability of a specific feature value. Query using bitwise AND operations. Single JOIN query retrieves lemma and translations together.

**Tech Stack:** SQLite (bitmasks), modern_greek_inflexion (via Morpheus), Python 3.12+

---

## Task 1: Create Bitmask Helper Module

**Files:**
- Create: `syntaxis/database/bitmasks.py`

**Step 1: Write failing test for enum_to_bit function**

Create: `tests/database/test_bitmasks.py`

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_bitmasks.py::test_enum_to_bit_converts_first_enum_to_one -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'syntaxis.database.bitmasks'"

**Step 3: Create directory and implement enum_to_bit**

```bash
mkdir -p tests/database
touch tests/database/__init__.py
```

Create: `syntaxis/database/bitmasks.py`

```python
"""Bitmask utilities for feature-based word filtering."""

from enum import Enum
from typing import Iterable


def enum_to_bit(enum_value: Enum) -> int:
    """Convert enum to its bit position (1, 2, 4, 8, ...).

    Args:
        enum_value: Enum member to convert

    Returns:
        Power of 2 corresponding to enum's position (1 << position)

    Examples:
        >>> enum_to_bit(Number.SINGULAR)  # First member
        1
        >>> enum_to_bit(Number.PLURAL)  # Second member
        2
        >>> enum_to_bit(Case.ACCUSATIVE)  # Third member
        4
    """
    members = list(type(enum_value).__members__.values())
    position = members.index(enum_value)
    return 1 << position
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_bitmasks.py -v
```

Expected: 3 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/database/bitmasks.py tests/database/test_bitmasks.py tests/database/__init__.py
git commit -m "feat: add enum_to_bit function for bitmask conversion"
```

---

## Task 2: Implement build_mask Function

**Files:**
- Modify: `syntaxis/database/bitmasks.py`
- Modify: `tests/database/test_bitmasks.py`

**Step 1: Write failing test for build_mask**

Add to `tests/database/test_bitmasks.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_bitmasks.py::test_build_mask_combines_single_value -v
```

Expected: FAIL with "NameError: name 'build_mask' is not defined"

**Step 3: Implement build_mask**

Add to `syntaxis/database/bitmasks.py`:

```python
def build_mask(enum_values: Iterable[Enum]) -> int:
    """Combine multiple enum values into a bitmask.

    Args:
        enum_values: Iterable of enum members to combine

    Returns:
        Integer bitmask with bits set for each enum value

    Examples:
        >>> build_mask([Number.SINGULAR, Number.PLURAL])
        3  # 1 | 2
        >>> build_mask([Case.NOMINATIVE, Case.ACCUSATIVE])
        5  # 1 | 4
    """
    mask = 0
    for value in enum_values:
        mask |= enum_to_bit(value)
    return mask
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_bitmasks.py -v
```

Expected: 7 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/database/bitmasks.py tests/database/test_bitmasks.py
git commit -m "feat: add build_mask function to combine enum values"
```

---

## Task 3: Implement has_feature Function and Feature Maps

**Files:**
- Modify: `syntaxis/database/bitmasks.py`
- Modify: `tests/database/test_bitmasks.py`

**Step 1: Write failing test for has_feature**

Add to `tests/database/test_bitmasks.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_bitmasks.py::test_has_feature_returns_true_when_present -v
```

Expected: FAIL with "NameError: name 'has_feature' is not defined"

**Step 3: Implement has_feature and add feature maps**

Add to `syntaxis/database/bitmasks.py`:

```python
from syntaxis.models.enums import PartOfSpeech as POSEnum


def has_feature(mask: int, feature: Enum) -> bool:
    """Check if a bitmask contains a specific feature.

    Args:
        mask: Integer bitmask to check
        feature: Enum member to look for

    Returns:
        True if the feature's bit is set in the mask, False otherwise

    Examples:
        >>> has_feature(3, Number.SINGULAR)  # 3 = SINGULAR | PLURAL
        True
        >>> has_feature(1, Number.PLURAL)  # 1 = only SINGULAR
        False
    """
    return (mask & enum_to_bit(feature)) != 0


# Maps POS to its valid feature names
VALID_FEATURES: dict[POSEnum, set[str]] = {
    POSEnum.NOUN: {"gender", "number", "case"},
    POSEnum.VERB: {"tense", "voice", "mood", "number", "person", "case"},
    POSEnum.ADJECTIVE: {"number", "case"},
    POSEnum.ARTICLE: {"gender", "number", "case"},
    POSEnum.PRONOUN: {"gender", "number", "case"},
    POSEnum.ADVERB: set(),
    POSEnum.PREPOSITION: set(),
    POSEnum.CONJUNCTION: set(),
}

# Maps POS enum to database table name
POS_TO_TABLE_MAP: dict[POSEnum, str] = {
    POSEnum.NOUN: "greek_nouns",
    POSEnum.VERB: "greek_verbs",
    POSEnum.ADJECTIVE: "greek_adjectives",
    POSEnum.ARTICLE: "greek_articles",
    POSEnum.PRONOUN: "greek_pronouns",
    POSEnum.ADVERB: "greek_adverbs",
    POSEnum.PREPOSITION: "greek_prepositions",
    POSEnum.CONJUNCTION: "greek_conjunctions",
}
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_bitmasks.py -v
```

Expected: 10 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/database/bitmasks.py tests/database/test_bitmasks.py
git commit -m "feat: add has_feature function and POS feature maps"
```

---

## Task 4: Update Database Schema with Bitmask Columns

**Files:**
- Modify: `syntaxis/database/schema.py:25-113`

**Step 1: Write test for schema including bitmask columns**

Create: `tests/database/test_schema.py`

```python
import sqlite3
import pytest
from syntaxis.database.schema import create_schema


def test_schema_creates_greek_nouns_with_bitmask_columns():
    """greek_nouns table should have number_mask and case_mask columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_nouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "number_mask" in columns
    assert columns["number_mask"] == "INTEGER"
    assert "case_mask" in columns
    assert columns["case_mask"] == "INTEGER"
    assert "gender" in columns  # Existing column
    assert "lemma" in columns


def test_schema_creates_greek_verbs_with_bitmask_columns():
    """greek_verbs table should have all verb feature mask columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_verbs)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "tense_mask" in columns
    assert "voice_mask" in columns
    assert "mood_mask" in columns
    assert "number_mask" in columns
    assert "person_mask" in columns
    assert "case_mask" in columns
    for col in ["tense_mask", "voice_mask", "mood_mask", "number_mask", "person_mask", "case_mask"]:
        assert columns[col] == "INTEGER"


def test_schema_creates_greek_adjectives_with_bitmask_columns():
    """greek_adjectives table should have number_mask and case_mask."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_adjectives)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "number_mask" in columns
    assert "case_mask" in columns


def test_schema_creates_greek_articles_with_bitmask_columns():
    """greek_articles table should have gender_mask, number_mask, case_mask."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_articles)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender_mask" in columns
    assert "number_mask" in columns
    assert "case_mask" in columns


def test_schema_creates_greek_pronouns_with_bitmask_columns():
    """greek_pronouns table should have gender_mask, number_mask, case_mask."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_pronouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender_mask" in columns
    assert "number_mask" in columns
    assert "case_mask" in columns
    assert "person" in columns  # Existing column
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_schema.py::test_schema_creates_greek_nouns_with_bitmask_columns -v
```

Expected: FAIL with "AssertionError: assert 'number_mask' in {...}"

**Step 3: Update schema with bitmask columns**

Modify `syntaxis/database/schema.py`, updating the table creation statements:

```python
    # Greek nouns table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_nouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            gender TEXT NOT NULL,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek verbs table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_verbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            verb_group TEXT,
            tense_mask INTEGER,
            voice_mask INTEGER,
            mood_mask INTEGER,
            number_mask INTEGER,
            person_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek adjectives table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_adjectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek articles table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            gender_mask INTEGER,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek pronouns table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_pronouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            person TEXT,
            gender_mask INTEGER,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_schema.py -v
```

Expected: 5 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/database/schema.py tests/database/test_schema.py
git commit -m "feat: add bitmask columns to database schema"
```

---

## Task 5: Add Generic create() Method to Morpheus

**Files:**
- Modify: `syntaxis/morpheus.py:19-56`

**Step 1: Write failing test for Morpheus.create()**

Create: `tests/test_morpheus.py`

```python
import pytest
from syntaxis.morpheus import Morpheus
from syntaxis.models.enums import PartOfSpeech as POSEnum
from syntaxis.models.part_of_speech import Noun, Verb, Adjective, Article


def test_morpheus_create_returns_noun_for_noun_pos():
    """create() with NOUN pos should return Noun instance."""
    result = Morpheus.create("άνθρωπος", POSEnum.NOUN)
    assert isinstance(result, Noun)
    assert result.lemma == "άνθρωπος"


def test_morpheus_create_returns_verb_for_verb_pos():
    """create() with VERB pos should return Verb instance."""
    result = Morpheus.create("τρώω", POSEnum.VERB)
    assert isinstance(result, Verb)
    assert result.lemma == "τρώω"


def test_morpheus_create_returns_adjective_for_adjective_pos():
    """create() with ADJECTIVE pos should return Adjective instance."""
    result = Morpheus.create("καλός", POSEnum.ADJECTIVE)
    assert isinstance(result, Adjective)
    assert result.lemma == "καλός"


def test_morpheus_create_returns_article_for_article_pos():
    """create() with ARTICLE pos should return Article instance."""
    result = Morpheus.create("ο", POSEnum.ARTICLE)
    assert isinstance(result, Article)
    assert result.lemma == "ο"


def test_morpheus_create_populates_forms():
    """create() should populate forms dictionary."""
    result = Morpheus.create("άνθρωπος", POSEnum.NOUN)
    assert result.forms is not None
    assert len(result.forms) > 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_morpheus.py::test_morpheus_create_returns_noun_for_noun_pos -v
```

Expected: FAIL with "AttributeError: type object 'Morpheus' has no attribute 'create'"

**Step 3: Implement Morpheus.create()**

Add to `syntaxis/morpheus.py` (after the imports, before the existing methods):

```python
from syntaxis.models.enums import PartOfSpeech as POSEnum


class Morpheus:

    @staticmethod
    def create(lemma: str, pos: POSEnum) -> T:
        """Generic method to create any POS type from lemma.

        Args:
            lemma: The base form of the word
            pos: Part of speech enum value

        Returns:
            Appropriate PartOfSpeech subclass instance with forms populated

        Raises:
            KeyError: If pos is not in the method map

        Examples:
            >>> Morpheus.create("άνθρωπος", POSEnum.NOUN)
            Noun(lemma="άνθρωπος", forms={...})
        """
        method_map = {
            POSEnum.NOUN: Morpheus.noun,
            POSEnum.VERB: Morpheus.verb,
            POSEnum.ADJECTIVE: Morpheus.adjective,
            POSEnum.ARTICLE: Morpheus.article,
            POSEnum.PRONOUN: Morpheus.pronoun,
            POSEnum.ADVERB: Morpheus.adverb,
            POSEnum.NUMERAL: Morpheus.numeral,
        }
        return method_map[pos](lemma)

    @staticmethod
    def _get_inflected_forms(lemma: str, pos_class: Type[T]) -> T:
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_morpheus.py -v
```

Expected: 5 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/morpheus.py tests/test_morpheus.py
git commit -m "feat: add generic create() method to Morpheus"
```

---

## Task 6: Implement _create_word_from_row Helper Method

**Files:**
- Modify: `syntaxis/database/manager.py:119-131`

**Step 1: Write failing test for _create_word_from_row**

Create: `tests/database/test_manager.py`

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_manager.py::test_create_word_from_row_creates_noun_with_translations -v
```

Expected: FAIL with error about _create_word_from_row returning None or not working correctly

**Step 3: Implement _create_word_from_row**

Modify `syntaxis/database/manager.py`, replacing the existing `_create_word_from_row` method:

```python
from syntaxis.morpheus import Morpheus
from syntaxis.models.part_of_speech import PartOfSpeech as PartOfSpeechBase


def _create_word_from_row(
    self,
    row: sqlite3.Row,
    pos: PartOfSpeech
) -> PartOfSpeechBase:
    """Create PartOfSpeech object with translations from query result.

    Args:
        row: Database row with id, lemma, and translations columns
        pos: Part of speech enum

    Returns:
        Complete PartOfSpeech object with forms and translations
    """
    lemma = row["lemma"]
    translations_str = row["translations"]

    # Parse translations (GROUP_CONCAT returns pipe-delimited string)
    translations = translations_str.split("|") if translations_str else None

    # Create word with inflected forms using Morpheus
    word = Morpheus.create(lemma, pos)
    word.translations = translations

    return word
```

Also update the manager's __init__ to enable Row factory:

```python
def __init__(self, db_path: str | None = None):
    """Initialize the lexical manager with SQLite backend.

    Args:
        db_path: Path to SQLite database file. If None, creates in-memory database.
    """
    self._db_path = db_path

    if db_path is None:
        self._conn = sqlite3.connect(":memory:")
    else:
        self._conn = sqlite3.connect(db_path)

    self._conn.row_factory = sqlite3.Row  # Enable column access by name
    create_schema(self._conn)
    self._morphology_adapter = None
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_manager.py -v
```

Expected: 3 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/database/manager.py tests/database/test_manager.py
git commit -m "feat: implement _create_word_from_row helper method"
```

---

## Task 7: Implement get_random_word Method

**Files:**
- Modify: `syntaxis/database/manager.py:33-43`

**Step 1: Write failing test for get_random_word without features**

Add to `tests/database/test_manager.py`:

```python
from syntaxis.models.enums import Number, Case, Gender


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_manager.py::test_get_random_word_returns_noun_without_features -v
```

Expected: FAIL - current implementation returns None

**Step 3: Implement get_random_word**

Modify `syntaxis/database/manager.py`, replacing the existing `get_random_word` method:

```python
from typing import Any
from syntaxis.database.bitmasks import (
    enum_to_bit,
    VALID_FEATURES,
    POS_TO_TABLE_MAP,
)


def get_random_word(
    self,
    pos: PartOfSpeech,
    **features: Any
) -> PartOfSpeechBase | None:
    """Get a random word of the specified part of speech.

    Args:
        pos: Part of speech enum (PartOfSpeech.NOUN, PartOfSpeech.VERB, etc.)
        **features: Feature filters as enum values
                    (gender=Gender.MASCULINE, case=Case.NOMINATIVE, etc.)

    Returns:
        Instance of appropriate PartOfSpeech subclass with forms and
        translations, or None if no matches

    Raises:
        ValueError: If invalid features provided for the POS type

    Examples:
        >>> manager.get_random_word(PartOfSpeech.NOUN, number=Number.SINGULAR)
        Noun(lemma="άνθρωπος", ...)
    """
    # Validate features
    valid_features = VALID_FEATURES.get(pos, set())
    invalid_features = set(features.keys()) - valid_features

    if invalid_features:
        raise ValueError(
            f"Invalid features {invalid_features} for {pos.name}. "
            f"Valid features are: {valid_features}"
        )

    cursor = self._conn.cursor()
    table = POS_TO_TABLE_MAP[pos]

    # Build WHERE conditions for bitmask features
    conditions = []
    params = [pos.name]  # For JOIN condition

    for feature_name, feature_value in features.items():
        bit = enum_to_bit(feature_value)
        conditions.append(f"(g.{feature_name}_mask & ?) != 0")
        params.append(bit)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Single query with JOIN to get lemma and translations
    query = f"""
        SELECT
            g.id,
            g.lemma,
            GROUP_CONCAT(e.word, '|') as translations
        FROM {table} g
        LEFT JOIN translations t ON t.greek_word_id = g.id
            AND t.greek_pos_type = ?
        LEFT JOIN english_words e ON e.id = t.english_word_id
        WHERE {where_clause}
        GROUP BY g.id
        ORDER BY RANDOM()
        LIMIT 1
    """

    row = cursor.execute(query, params).fetchone()
    if not row:
        return None

    return self._create_word_from_row(row, pos)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_manager.py -v
```

Expected: 8 tests PASS (3 from Task 6 + 5 new tests)

**Step 5: Commit**

```bash
git add syntaxis/database/manager.py tests/database/test_manager.py
git commit -m "feat: implement get_random_word with feature filtering"
```

---

## Task 8: Implement _calculate_masks_for_word Helper Method

**Files:**
- Create: `syntaxis/database/mask_calculator.py`

**Step 1: Write failing test for mask calculation**

Create: `tests/database/test_mask_calculator.py`

```python
import pytest
from syntaxis.database.mask_calculator import calculate_masks_for_word
from syntaxis.models.enums import PartOfSpeech as POSEnum, Number, Case


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
        "tense_mask", "voice_mask", "mood_mask",
        "number_mask", "person_mask", "case_mask"
    }
    assert set(masks.keys()) == expected_keys

    # All masks should have at least one bit set
    for key, value in masks.items():
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_mask_calculator.py::test_calculate_masks_for_noun -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'syntaxis.database.mask_calculator'"

**Step 3: Implement calculate_masks_for_word**

Create: `syntaxis/database/mask_calculator.py`

```python
"""Calculate bitmasks for word features by inspecting generated forms."""

from syntaxis.models.enums import PartOfSpeech as POSEnum
from syntaxis.morpheus import Morpheus
from syntaxis.database.bitmasks import build_mask


def calculate_masks_for_word(lemma: str, pos: POSEnum) -> dict[str, int]:
    """Calculate bitmask values by inspecting word's available forms.

    Args:
        lemma: The word's base form
        pos: Part of speech

    Returns:
        Dictionary mapping mask column names to integer bitmask values
        (e.g., {'number_mask': 3, 'case_mask': 15})
    """
    # Generate forms using Morpheus
    word = Morpheus.create(lemma, pos)

    masks = {}

    if pos == POSEnum.NOUN:
        # forms[gender][number][case]
        available_numbers = set()
        available_cases = set()

        for gender_dict in word.forms.values():
            for number_key, number_dict in gender_dict.items():
                available_numbers.add(number_key)
                for case_key in number_dict.keys():
                    available_cases.add(case_key)

        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.VERB:
        # forms[tense][voice][mood][number][person][case]
        available_tenses = set()
        available_voices = set()
        available_moods = set()
        available_numbers = set()
        available_persons = set()
        available_cases = set()

        for tense_key, tense_dict in word.forms.items():
            available_tenses.add(tense_key)
            for voice_key, voice_dict in tense_dict.items():
                available_voices.add(voice_key)
                for mood_key, mood_dict in voice_dict.items():
                    available_moods.add(mood_key)
                    for number_key, number_dict in mood_dict.items():
                        available_numbers.add(number_key)
                        for person_key, person_dict in number_dict.items():
                            available_persons.add(person_key)
                            for case_key in person_dict.keys():
                                available_cases.add(case_key)

        masks["tense_mask"] = build_mask(available_tenses)
        masks["voice_mask"] = build_mask(available_voices)
        masks["mood_mask"] = build_mask(available_moods)
        masks["number_mask"] = build_mask(available_numbers)
        masks["person_mask"] = build_mask(available_persons)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.ADJECTIVE:
        # forms[pos_type][number][case]
        available_numbers = set()
        available_cases = set()

        for pos_dict in word.forms.values():
            for number_key, number_dict in pos_dict.items():
                available_numbers.add(number_key)
                for case_key in number_dict.keys():
                    available_cases.add(case_key)

        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.ARTICLE:
        # forms[number][gender][case]
        available_numbers = set()
        available_genders = set()
        available_cases = set()

        for number_key, number_dict in word.forms.items():
            available_numbers.add(number_key)
            for gender_key, gender_dict in number_dict.items():
                available_genders.add(gender_key)
                for case_key in gender_dict.keys():
                    available_cases.add(case_key)

        masks["gender_mask"] = build_mask(available_genders)
        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.PRONOUN:
        # forms[number][gender][case]
        available_numbers = set()
        available_genders = set()
        available_cases = set()

        for number_key, number_dict in word.forms.items():
            available_numbers.add(number_key)
            for gender_key, gender_dict in number_dict.items():
                available_genders.add(gender_key)
                for case_key in gender_dict.keys():
                    available_cases.add(case_key)

        masks["gender_mask"] = build_mask(available_genders)
        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    # ADVERB, PREPOSITION, CONJUNCTION have no features
    # Return empty dict

    return masks
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_mask_calculator.py -v
```

Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/database/mask_calculator.py tests/database/test_mask_calculator.py
git commit -m "feat: implement calculate_masks_for_word helper function"
```

---

## Task 9: Integration Test and Documentation

**Files:**
- Create: `tests/integration/test_get_random_word_integration.py`
- Modify: `README.md` (if exists) or create usage documentation

**Step 1: Write integration test**

Create: `tests/integration/test_get_random_word_integration.py`

```python
"""Integration tests for get_random_word with real Greek words."""

import pytest
from syntaxis.database.manager import LexicalManager
from syntaxis.database.mask_calculator import calculate_masks_for_word
from syntaxis.models.enums import (
    PartOfSpeech as POSEnum,
    Number,
    Case,
    Gender,
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
        (lemma, "MASCULINE", masks["number_mask"], masks["case_mask"], "validated")
    )

    # Add English translation
    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)",
        ("person", "NOUN")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (1, 1, "NOUN")
    )
    conn.commit()

    # Retrieve with features
    result = manager.get_random_word(
        POSEnum.NOUN,
        number=Number.SINGULAR,
        case=Case.NOMINATIVE
    )

    assert result is not None
    assert result.lemma == "άνθρωπος"
    assert result.translations == ["person"]

    # Verify we can get a specific form
    form = result.get_form(Gender.MASCULINE, Number.SINGULAR, Case.NOMINATIVE)
    assert "άνθρωπος" in form or "ο άνθρωπος" in str(form)


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
            "validated"
        )
    )

    cursor.execute(
        "INSERT INTO english_words (word, pos_type) VALUES (?, ?)",
        ("eat", "VERB")
    )
    cursor.execute(
        "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
        (1, 1, "VERB")
    )
    conn.commit()

    # Retrieve with verb features
    result = manager.get_random_word(
        POSEnum.VERB,
        tense=Tense.PRESENT,
        voice=Voice.ACTIVE
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
        (lemma, "NEUTER", 2, 15, "validated")  # number_mask=2 is only PLURAL
    )
    conn.commit()

    # Request SINGULAR - should return None
    result = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)

    assert result is None
```

**Step 2: Run integration tests**

```bash
mkdir -p tests/integration
touch tests/integration/__init__.py
pytest tests/integration/test_get_random_word_integration.py -v
```

Expected: 3 tests PASS

**Step 3: Create usage documentation**

Create: `docs/usage/get_random_word.md`

```markdown
# Using get_random_word()

## Overview

The `get_random_word()` method retrieves a random Greek word from the lexicon, optionally filtered by grammatical features.

## Basic Usage

```python
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeech as POSEnum

manager = LexicalManager("greek.db")

# Get any random noun
word = manager.get_random_word(POSEnum.NOUN)
print(word.lemma)  # e.g., "άνθρωπος"
print(word.translations)  # e.g., ["person", "human"]
```

## Filtering by Features

### Nouns

Valid features: `gender`, `number`, `case`

```python
from syntaxis.models.enums import Number, Case, Gender

# Get singular nominative masculine noun
word = manager.get_random_word(
    POSEnum.NOUN,
    number=Number.SINGULAR,
    case=Case.NOMINATIVE,
    gender=Gender.MASCULINE
)
```

### Verbs

Valid features: `tense`, `voice`, `mood`, `number`, `person`, `case`

```python
from syntaxis.models.enums import Tense, Voice, Mood

# Get present tense active voice verb
word = manager.get_random_word(
    POSEnum.VERB,
    tense=Tense.PRESENT,
    voice=Voice.ACTIVE
)
```

### Adjectives

Valid features: `number`, `case`

```python
# Get plural genitive adjective
word = manager.get_random_word(
    POSEnum.ADJECTIVE,
    number=Number.PLURAL,
    case=Case.GENITIVE
)
```

## Adding Words with Masks

When adding words to the database, calculate and store bitmasks:

```python
from syntaxis.database.mask_calculator import calculate_masks_for_word

lemma = "άνθρωπος"
masks = calculate_masks_for_word(lemma, POSEnum.NOUN)

cursor.execute(
    """
    INSERT INTO greek_nouns
    (lemma, gender, number_mask, case_mask, validation_status)
    VALUES (?, ?, ?, ?, ?)
    """,
    (lemma, "MASCULINE", masks["number_mask"], masks["case_mask"], "validated")
)
```

## Error Handling

```python
# Invalid feature for POS type raises ValueError
try:
    word = manager.get_random_word(POSEnum.NOUN, tense=Tense.PRESENT)
except ValueError as e:
    print(e)  # "Invalid features {'tense'} for NOUN. Valid features are: {'gender', 'number', 'case'}"

# No matching words returns None
word = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)
if word is None:
    print("No words match the criteria")
```
```

**Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add tests/integration/ docs/usage/get_random_word.md
git commit -m "test: add integration tests and usage documentation"
```

---

## Final Verification

**Step 1: Run complete test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: All tests PASS

**Step 2: Verify imports work**

```bash
python -c "from syntaxis.database.manager import LexicalManager; from syntaxis.database.bitmasks import enum_to_bit; print('Imports successful')"
```

Expected: "Imports successful"

**Step 3: Manual smoke test**

```bash
python -c "
from syntaxis.database.manager import LexicalManager
from syntaxis.database.mask_calculator import calculate_masks_for_word
from syntaxis.models.enums import PartOfSpeech as POSEnum, Number

manager = LexicalManager()
masks = calculate_masks_for_word('άνθρωπος', POSEnum.NOUN)
print(f'Masks calculated: {masks}')

cursor = manager._conn.cursor()
cursor.execute(
    'INSERT INTO greek_nouns (lemma, gender, number_mask, case_mask, validation_status) VALUES (?, ?, ?, ?, ?)',
    ('άνθρωπος', 'MASCULINE', masks['number_mask'], masks['case_mask'], 'validated')
)
manager._conn.commit()

word = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)
print(f'Retrieved word: {word.lemma if word else None}')
"
```

Expected: Output showing masks and retrieved word

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete feature-based word retrieval implementation

Implements get_random_word() with bitmask-based feature filtering:
- Bitmask helper utilities (enum_to_bit, build_mask, has_feature)
- Updated database schema with mask columns
- Generic Morpheus.create() method
- Single-query word retrieval with translations
- Mask calculation from word forms
- Comprehensive tests and documentation"
```

---

## Implementation Complete

All tasks finished. The feature-based word retrieval system is ready for use.

**Key Files Modified/Created:**
- `syntaxis/database/bitmasks.py` - Bitmask utilities
- `syntaxis/database/schema.py` - Updated schema with mask columns
- `syntaxis/database/manager.py` - get_random_word() implementation
- `syntaxis/database/mask_calculator.py` - Mask calculation from forms
- `syntaxis/morpheus.py` - Generic create() method
- Comprehensive test suite
- Usage documentation
