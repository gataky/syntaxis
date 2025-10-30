# Add Word Method Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `add_word()` method to LexicalManager for manual word insertion with automatic mask calculation and field inference.

**Architecture:** Single method that validates inputs, generates forms via Morpheus, calculates masks, infers POS-specific fields (gender, verb_group), and inserts into appropriate table with translations in a transaction.

**Tech Stack:** Python, SQLite3, pytest, existing Morpheus and mask_calculator modules

---

## Task 1: Test Empty Translations Validation

**Files:**
- Modify: `tests/database/test_manager.py:244` (append test)

**Step 1: Write the failing test**

Add to end of `tests/database/test_manager.py`:

```python


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_empty_translations -v
pytest tests/database/test_manager.py::test_add_word_raises_error_for_none_translations -v
```

Expected: FAIL with "AttributeError: 'LexicalManager' object has no attribute 'add_word'"

**Step 3: Write minimal implementation stub**

Add to `syntaxis/database/manager.py:223` (after `_create_word_from_row` method):

```python

    def add_word(
        self,
        lemma: str,
        translations: list[str],
        pos: PartOfSpeech
    ) -> PartOfSpeechBase:
        """Add a word to the lexicon with automatic mask calculation.

        Args:
            lemma: Greek word in its base form
            translations: List of English translations (at least one required)
            pos: Part of speech enum

        Returns:
            Complete PartOfSpeech object with forms and translations

        Raises:
            ValueError: If translations empty, lemma empty, word exists, or Morpheus fails
        """
        # Validate translations
        if not translations:
            raise ValueError("At least one translation required")

        # Stub - will implement rest later
        return None
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_empty_translations -v
pytest tests/database/test_manager.py::test_add_word_raises_error_for_none_translations -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/database/test_manager.py syntaxis/database/manager.py
git commit -m "test: add validation tests for empty translations in add_word"
```

---

## Task 2: Test Empty Lemma Validation

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the failing test**

Add to end of `tests/database/test_manager.py`:

```python


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_empty_lemma -v
```

Expected: FAIL (method returns None, doesn't raise error)

**Step 3: Add validation to implementation**

In `syntaxis/database/manager.py`, update `add_word` method after translations validation:

```python
        # Validate translations
        if not translations:
            raise ValueError("At least one translation required")

        # Validate lemma
        if not lemma:
            raise ValueError("Lemma cannot be empty")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_empty_lemma -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/database/test_manager.py syntaxis/database/manager.py
git commit -m "test: add validation for empty lemma in add_word"
```

---

## Task 3: Test Duplicate Word Detection

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the failing test**

Add to end of `tests/database/test_manager.py`:

```python


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_duplicate_lemma -v
```

Expected: FAIL (no duplicate check implemented yet)

**Step 3: Add duplicate check to implementation**

In `syntaxis/database/manager.py`, update `add_word` method after lemma validation:

```python
        # Validate lemma
        if not lemma:
            raise ValueError("Lemma cannot be empty")

        # Check for duplicates
        table = POS_TO_TABLE_MAP[pos]
        cursor = self._conn.cursor()
        existing = cursor.execute(
            f"SELECT id FROM {table} WHERE lemma = ?",
            (lemma,)
        ).fetchone()
        if existing:
            raise ValueError(f"Word '{lemma}' already exists as {pos.name}")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_duplicate_lemma -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/database/test_manager.py syntaxis/database/manager.py
git commit -m "test: add duplicate word detection in add_word"
```

---

## Task 4: Test Happy Path - Add Noun

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the failing test**

Add to end of `tests/database/test_manager.py`:

```python


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/database/test_manager.py::test_add_word_successfully_adds_noun_with_single_translation -v
```

Expected: FAIL (method still returns None)

**Step 3: Implement core add_word logic**

Replace the stub implementation in `syntaxis/database/manager.py` with full implementation:

```python
    def add_word(
        self,
        lemma: str,
        translations: list[str],
        pos: PartOfSpeech
    ) -> PartOfSpeechBase:
        """Add a word to the lexicon with automatic mask calculation.

        Args:
            lemma: Greek word in its base form
            translations: List of English translations (at least one required)
            pos: Part of speech enum

        Returns:
            Complete PartOfSpeech object with forms and translations

        Raises:
            ValueError: If translations empty, lemma empty, word exists, or Morpheus fails
        """
        from syntaxis.database.mask_calculator import calculate_masks_for_word

        # Validate translations
        if not translations:
            raise ValueError("At least one translation required")

        # Validate lemma
        if not lemma:
            raise ValueError("Lemma cannot be empty")

        # Check for duplicates
        table = POS_TO_TABLE_MAP[pos]
        cursor = self._conn.cursor()
        existing = cursor.execute(
            f"SELECT id FROM {table} WHERE lemma = ?",
            (lemma,)
        ).fetchone()
        if existing:
            raise ValueError(f"Word '{lemma}' already exists as {pos.name}")

        # Generate forms with Morpheus
        try:
            word = Morpheus.create(lemma, pos)
        except Exception as e:
            raise ValueError(f"Failed to generate forms for '{lemma}': {e}")

        if not word.forms:
            raise ValueError(f"Morpheus generated no forms for '{lemma}'")

        validation_status = "VALID"

        # Calculate masks
        masks = calculate_masks_for_word(lemma, pos)

        # Infer POS-specific fields
        pos_fields = {}

        if pos == PartOfSpeech.NOUN:
            # Infer gender from forms structure: forms[gender][number][case]
            # Map from mask_calculator's STRING_TO_ENUM
            from syntaxis.database.mask_calculator import STRING_TO_ENUM
            gender_key = next(iter(word.forms.keys()))
            gender_enum = STRING_TO_ENUM.get(gender_key)
            if gender_enum:
                pos_fields['gender'] = gender_enum.name
        elif pos == PartOfSpeech.VERB:
            # Check if word has verb_group attribute
            verb_group = getattr(word, 'verb_group', None)
            pos_fields['verb_group'] = verb_group

        # Insert into database (transactional)
        try:
            # Step 1: Insert Greek word
            if pos == PartOfSpeech.NOUN:
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, gender, number_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (lemma, pos_fields['gender'], masks.get('number_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos == PartOfSpeech.VERB:
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, verb_group, tense_mask, voice_mask, mood_mask,
                     number_mask, person_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (lemma, pos_fields.get('verb_group'), masks.get('tense_mask', 0),
                     masks.get('voice_mask', 0), masks.get('mood_mask', 0),
                     masks.get('number_mask', 0), masks.get('person_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos == PartOfSpeech.ADJECTIVE:
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, number_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (lemma, masks.get('number_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos in (PartOfSpeech.ARTICLE, PartOfSpeech.PRONOUN):
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, gender_mask, number_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (lemma, masks.get('gender_mask', 0), masks.get('number_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos in (PartOfSpeech.ADVERB, PartOfSpeech.PREPOSITION, PartOfSpeech.CONJUNCTION):
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, validation_status)
                    VALUES (?, ?)
                    """,
                    (lemma, validation_status)
                )

            greek_word_id = cursor.lastrowid

            # Step 2: Insert/retrieve English words
            english_word_ids = []
            for translation in translations:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO english_words (word, pos_type)
                    VALUES (?, ?)
                    """,
                    (translation, pos.name)
                )

                eng_id = cursor.execute(
                    """
                    SELECT id FROM english_words WHERE word = ? AND pos_type = ?
                    """,
                    (translation, pos.name)
                ).fetchone()[0]

                english_word_ids.append(eng_id)

            # Step 3: Create translation links
            for eng_id in english_word_ids:
                cursor.execute(
                    """
                    INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type)
                    VALUES (?, ?, ?)
                    """,
                    (eng_id, greek_word_id, pos.name)
                )

            self._conn.commit()

            # Step 4: Build and return Word object
            fake_row = sqlite3.Row(
                cursor,
                ['id', 'lemma', 'translations'],
                (greek_word_id, lemma, '|'.join(translations))
            )
            return self._create_word_from_row(fake_row, pos)

        except Exception as e:
            self._conn.rollback()
            raise
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_successfully_adds_noun_with_single_translation -v
```

Expected: PASS

**Step 5: Run all previous tests to ensure no regression**

```bash
pytest tests/database/test_manager.py -v
```

Expected: All PASS

**Step 6: Commit**

```bash
git add syntaxis/database/manager.py tests/database/test_manager.py
git commit -m "feat: implement add_word method with mask calculation and field inference"
```

---

## Task 5: Test Multiple Translations

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the test**

Add to end of `tests/database/test_manager.py`:

```python


def test_add_word_handles_multiple_translations():
    """Should link all translations to the Greek word."""
    manager = LexicalManager()

    result = manager.add_word(
        lemma="άνθρωπος",
        translations=["person", "human", "man"],
        pos=POSEnum.NOUN
    )

    assert set(result.translations) == {"person", "human", "man"}

    # Verify all English words inserted
    cursor = manager._conn.cursor()
    eng_count = cursor.execute(
        "SELECT COUNT(*) FROM english_words WHERE pos_type = ?",
        ("NOUN",)
    ).fetchone()[0]
    assert eng_count == 3

    # Verify all translation links created
    trans_count = cursor.execute(
        "SELECT COUNT(*) FROM translations WHERE greek_pos_type = ?",
        ("NOUN",)
    ).fetchone()[0]
    assert trans_count == 3
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_handles_multiple_translations -v
```

Expected: PASS (already implemented in Task 4)

**Step 3: Commit**

```bash
git add tests/database/test_manager.py
git commit -m "test: verify multiple translations handled correctly in add_word"
```

---

## Task 6: Test Verb Addition

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the test**

Add to end of `tests/database/test_manager.py`:

```python


def test_add_word_successfully_adds_verb():
    """Should add verb with appropriate mask columns."""
    manager = LexicalManager()

    result = manager.add_word(
        lemma="τρώω",
        translations=["eat", "consume"],
        pos=POSEnum.VERB
    )

    assert isinstance(result, Verb)
    assert result.lemma == "τρώω"
    assert set(result.translations) == {"eat", "consume"}

    # Verify verb-specific columns
    cursor = manager._conn.cursor()
    row = cursor.execute(
        """
        SELECT lemma, tense_mask, voice_mask, mood_mask,
               number_mask, person_mask, validation_status
        FROM greek_verbs WHERE lemma = ?
        """,
        ("τρώω",)
    ).fetchone()
    assert row is not None
    assert row[0] == "τρώω"
    assert row[1] > 0  # tense_mask
    assert row[2] > 0  # voice_mask
    assert row[3] > 0  # mood_mask
    assert row[4] > 0  # number_mask
    assert row[5] > 0  # person_mask
    assert row[6] == "VALID"
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_successfully_adds_verb -v
```

Expected: PASS (already implemented in Task 4)

**Step 3: Commit**

```bash
git add tests/database/test_manager.py
git commit -m "test: verify verb addition works correctly in add_word"
```

---

## Task 7: Test Morpheus Failure Handling

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the test**

Add to end of `tests/database/test_manager.py`:

```python


def test_add_word_raises_error_for_invalid_lemma():
    """Should raise ValueError when Morpheus cannot generate forms."""
    manager = LexicalManager()

    # Use a clearly invalid lemma (English word, not Greek)
    with pytest.raises(ValueError) as exc_info:
        manager.add_word(
            lemma="invalid123xyz",
            translations=["test"],
            pos=POSEnum.NOUN
        )

    assert "Failed to generate forms" in str(exc_info.value) or \
           "generated no forms" in str(exc_info.value)
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_raises_error_for_invalid_lemma -v
```

Expected: PASS (already implemented in Task 4)

**Step 3: Commit**

```bash
git add tests/database/test_manager.py
git commit -m "test: verify Morpheus failure handling in add_word"
```

---

## Task 8: Test Existing English Word Reuse

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write the test**

Add to end of `tests/database/test_manager.py`:

```python


def test_add_word_reuses_existing_english_words():
    """Should reuse existing English words rather than creating duplicates."""
    manager = LexicalManager()

    # Add first word with "person" translation
    manager.add_word(
        lemma="άνθρωπος",
        translations=["person"],
        pos=POSEnum.NOUN
    )

    # Add second word with same "person" translation
    manager.add_word(
        lemma="πρόσωπο",
        translations=["person", "face"],
        pos=POSEnum.NOUN
    )

    # Verify only one "person" entry in english_words
    cursor = manager._conn.cursor()
    person_count = cursor.execute(
        "SELECT COUNT(*) FROM english_words WHERE word = ? AND pos_type = ?",
        ("person", "NOUN")
    ).fetchone()[0]
    assert person_count == 1

    # Verify both Greek words linked to same English word
    person_id = cursor.execute(
        "SELECT id FROM english_words WHERE word = ? AND pos_type = ?",
        ("person", "NOUN")
    ).fetchone()[0]

    greek_word_count = cursor.execute(
        "SELECT COUNT(DISTINCT greek_word_id) FROM translations WHERE english_word_id = ?",
        (person_id,)
    ).fetchone()[0]
    assert greek_word_count == 2
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_reuses_existing_english_words -v
```

Expected: PASS (INSERT OR IGNORE + SELECT pattern handles this)

**Step 3: Commit**

```bash
git add tests/database/test_manager.py
git commit -m "test: verify English word reuse in add_word"
```

---

## Task 9: Fix sqlite3.Row Construction Issue

**Context:** The current implementation tries to construct a `sqlite3.Row` directly, which won't work as expected. We need to fix this.

**Files:**
- Modify: `syntaxis/database/manager.py` (around line in add_word where fake_row is created)

**Step 1: Run existing tests to identify the issue**

```bash
pytest tests/database/test_manager.py::test_add_word_successfully_adds_noun_with_single_translation -v
```

Expected: May fail or have issues with Row construction

**Step 2: Fix the Row construction**

In `syntaxis/database/manager.py`, replace the fake_row construction in add_word:

```python
            # Step 4: Build and return Word object
            # Query back the complete row to get proper sqlite3.Row
            row = cursor.execute(
                f"""
                SELECT
                    g.id,
                    g.lemma,
                    GROUP_CONCAT(e.word, '|') as translations
                FROM {table} g
                LEFT JOIN translations t ON t.greek_word_id = g.id
                    AND t.greek_pos_type = ?
                LEFT JOIN english_words e ON e.id = t.english_word_id
                WHERE g.id = ?
                GROUP BY g.id
                """,
                (pos.name, greek_word_id)
            ).fetchone()

            return self._create_word_from_row(row, pos)
```

**Step 3: Run tests to verify fix works**

```bash
pytest tests/database/test_manager.py -k "test_add_word" -v
```

Expected: All PASS

**Step 4: Commit**

```bash
git add syntaxis/database/manager.py
git commit -m "fix: properly construct sqlite3.Row in add_word return value"
```

---

## Task 10: Add Integration Test

**Files:**
- Modify: `tests/database/test_manager.py` (append test)

**Step 1: Write integration test**

Add to end of `tests/database/test_manager.py`:

```python


def test_add_word_integration_with_get_random_word():
    """Integration test: add word and verify it can be retrieved."""
    manager = LexicalManager()

    # Add a word
    added_word = manager.add_word(
        lemma="άνθρωπος",
        translations=["person", "human"],
        pos=POSEnum.NOUN
    )

    # Retrieve it with get_random_word
    retrieved_word = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)

    assert retrieved_word is not None
    assert retrieved_word.lemma == "άνθρωπος"
    assert set(retrieved_word.translations) == {"person", "human"}

    # Verify feature filtering works
    retrieved_with_case = manager.get_random_word(
        POSEnum.NOUN,
        number=Number.SINGULAR,
        case=Case.ACCUSATIVE
    )
    assert retrieved_with_case is not None
    assert retrieved_with_case.lemma == "άνθρωπος"
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/database/test_manager.py::test_add_word_integration_with_get_random_word -v
```

Expected: PASS

**Step 3: Commit**

```bash
git add tests/database/test_manager.py
git commit -m "test: add integration test for add_word with get_random_word"
```

---

## Task 11: Run Full Test Suite

**Step 1: Run all tests**

```bash
pytest tests/database/test_manager.py -v
```

Expected: All tests PASS

**Step 2: Run broader test suite to check for regressions**

```bash
pytest tests/database/ -v
```

Expected: All tests PASS

**Step 3: Run integration tests if they exist**

```bash
pytest tests/integration/ -v
```

Expected: All tests PASS (or skip if none exist)

---

## Task 12: Update Documentation

**Files:**
- Create: `docs/usage/add_word.md`

**Step 1: Write usage documentation**

Create `docs/usage/add_word.md`:

```markdown
# Adding Words to the Lexicon

The `add_word()` method allows manual insertion of Greek words into the lexical database with automatic feature mask calculation.

## Basic Usage

```python
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeech

manager = LexicalManager("vocab.db")

# Add a noun
word = manager.add_word(
    lemma="άνθρωπος",
    translations=["person", "human", "man"],
    pos=PartOfSpeech.NOUN
)

print(word.lemma)         # άνθρωπος
print(word.translations)  # ["person", "human", "man"]
print(word.forms)         # Dictionary of all inflected forms
```

## Features

- **Automatic mask calculation**: Feature masks are calculated by inspecting Morpheus-generated forms
- **Field inference**: POS-specific fields (gender, verb_group) are automatically inferred
- **Validation**: Input validation ensures data integrity
- **Transaction safety**: All database operations are wrapped in a transaction

## Parameters

- `lemma` (str): Greek word in its base/dictionary form
- `translations` (list[str]): List of English translations (at least one required)
- `pos` (PartOfSpeech): Part of speech enum

## Returns

Returns a complete PartOfSpeech object (Noun, Verb, Adjective, etc.) with:
- Lemma
- All inflected forms generated by Morpheus
- English translations

## Error Handling

The method raises `ValueError` in these cases:

```python
# Empty translations
manager.add_word("άνθρωπος", [], PartOfSpeech.NOUN)
# ❌ ValueError: At least one translation required

# Empty lemma
manager.add_word("", ["person"], PartOfSpeech.NOUN)
# ❌ ValueError: Lemma cannot be empty

# Duplicate word
manager.add_word("άνθρωπος", ["person"], PartOfSpeech.NOUN)
manager.add_word("άνθρωπος", ["person"], PartOfSpeech.NOUN)
# ❌ ValueError: Word 'άνθρωπος' already exists as NOUN

# Invalid lemma
manager.add_word("invalid123", ["test"], PartOfSpeech.NOUN)
# ❌ ValueError: Failed to generate forms for 'invalid123'
```

## Examples

### Adding Different Parts of Speech

```python
# Noun
noun = manager.add_word("γυναίκα", ["woman"], PartOfSpeech.NOUN)

# Verb
verb = manager.add_word("τρώω", ["eat", "consume"], PartOfSpeech.VERB)

# Adjective
adj = manager.add_word("καλός", ["good", "nice"], PartOfSpeech.ADJECTIVE)
```

### Integration with get_random_word

```python
# Add words
manager.add_word("άνθρωπος", ["person"], PartOfSpeech.NOUN)
manager.add_word("γυναίκα", ["woman"], PartOfSpeech.NOUN)

# Retrieve with feature filtering
word = manager.get_random_word(
    PartOfSpeech.NOUN,
    number=Number.SINGULAR,
    case=Case.NOMINATIVE
)

print(word.lemma)  # Randomly: άνθρωπος or γυναίκα
```

## Implementation Details

### Automatic Mask Calculation

Masks are calculated by:
1. Generating all forms using Morpheus
2. Inspecting the form structure to identify available features
3. Converting features to bitmasks using `calculate_masks_for_word()`

### Field Inference

**Nouns**: Gender is inferred from the forms dictionary structure (`forms[gender][...]`)

**Verbs**: `verb_group` attribute is extracted if present on the Morpheus word object

### Database Structure

Each added word results in:
1. One row in the appropriate POS table (greek_nouns, greek_verbs, etc.)
2. N rows in `english_words` (or reuses existing entries)
3. N rows in `translations` linking Greek to English words

### Validation Status

Words are marked with `validation_status = "VALID"` if Morpheus successfully generates forms, or `"INVALID"` if form generation fails (though this currently raises an error instead).
```

**Step 2: Commit documentation**

```bash
git add docs/usage/add_word.md
git commit -m "docs: add usage guide for add_word method"
```

---

## Completion Checklist

- [ ] All validation tests passing
- [ ] Happy path tests passing (noun, verb)
- [ ] Multiple translations handled
- [ ] Duplicate detection working
- [ ] Morpheus failure handling
- [ ] English word reuse working
- [ ] Integration test passing
- [ ] Full test suite passing
- [ ] Documentation written
- [ ] All changes committed

## Notes for Implementation

**Key Design Decisions:**
- Single monolithic method (~150 lines) for simplicity
- Transaction wrapping for data consistency
- INSERT OR IGNORE pattern for English word deduplication
- Query-back pattern for return value (proper sqlite3.Row)

**Testing Strategy:**
- TDD approach: test first, then implement
- Bite-sized commits after each test/implementation pair
- Integration test to verify end-to-end functionality

**Potential Issues:**
- sqlite3.Row construction requires actual query result
- Different POS types have different table schemas
- Morpheus may fail for invalid Greek text
- Gender inference depends on forms dictionary structure

**Future Enhancements:**
- Batch add_words() method for multiple words
- Update existing word functionality
- More sophisticated validation status logic
- Support for custom validation_status values
