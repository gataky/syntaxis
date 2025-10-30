# Add Word Method Design

## Overview

Add a method to `LexicalManager` that allows manual insertion of Greek words into the database with automatic mask calculation and field inference.

## Requirements

- Accept: lemma (Greek word), translations (list of English strings), part of speech
- Calculate feature masks automatically using `calculate_masks_for_word()`
- Infer POS-specific fields (e.g., gender for nouns) from Morpheus-generated forms
- Insert into appropriate Greek word table with translations
- Validate inputs and handle duplicates

## Method Signature

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
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| POS-specific fields | Infer from Morpheus | Gender, verb_group extracted automatically from generated forms |
| Validation status | Based on Morpheus success | VALID if forms generated successfully, INVALID otherwise |
| Duplicate handling | Raise exception | Fail-fast with clear error - caller should check existence first |
| Return value | Word object | Return complete PartOfSpeech instance for immediate use |
| Translation requirement | At least one required | Every word must be translatable to be useful |
| Architecture | Single monolithic method | Keep all logic in one place for simplicity (~50-70 lines) |

## Implementation Flow

### 1. Input Validation

```python
# Validate inputs
if not translations:
    raise ValueError("At least one translation required")
if not lemma:
    raise ValueError("Lemma cannot be empty")

# Check for duplicates
table = POS_TO_TABLE_MAP[pos]
cursor = self._conn.cursor()
existing = cursor.execute(f"SELECT id FROM {table} WHERE lemma = ?", (lemma,)).fetchone()
if existing:
    raise ValueError(f"Word '{lemma}' already exists as {pos.name}")
```

### 2. Morpheus Validation and Mask Calculation

```python
# Generate forms with Morpheus
try:
    word = Morpheus.create(lemma, pos)
except Exception as e:
    raise ValueError(f"Failed to generate forms for '{lemma}': {e}")

if not word.forms:
    raise ValueError(f"Morpheus generated no forms for '{lemma}'")

validation_status = "VALID"

# Calculate masks
from syntaxis.database.mask_calculator import calculate_masks_for_word
masks = calculate_masks_for_word(lemma, pos)
```

### 3. Field Inference

**For nouns:**
```python
# Infer gender from forms structure: forms[gender][number][case]
gender_key = next(iter(word.forms.keys()))
gender_enum = STRING_TO_ENUM[gender_key]  # Use mapping from mask_calculator
gender_value = gender_enum.name  # Store as TEXT in DB
```

**For verbs:**
```python
# Check if word has verb_group attribute
verb_group = getattr(word, 'verb_group', None)
```

**For other POS types:**
- No additional fields needed

### 4. Database Insertion (Transactional)

```python
try:
    cursor = self._conn.cursor()

    # Step 1: Insert Greek word
    table = POS_TO_TABLE_MAP[pos]

    if pos == PartOfSpeech.NOUN:
        cursor.execute(f"""
            INSERT INTO {table} (lemma, gender, number_mask, case_mask, validation_status)
            VALUES (?, ?, ?, ?, ?)
        """, (lemma, gender_value, masks['number_mask'], masks['case_mask'], validation_status))
    elif pos == PartOfSpeech.VERB:
        cursor.execute(f"""
            INSERT INTO {table} (lemma, verb_group, tense_mask, voice_mask, mood_mask,
                                number_mask, person_mask, case_mask, validation_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lemma, verb_group, masks.get('tense_mask', 0), masks.get('voice_mask', 0),
              masks.get('mood_mask', 0), masks.get('number_mask', 0),
              masks.get('person_mask', 0), masks.get('case_mask', 0), validation_status))
    # ... similar for other POS types

    greek_word_id = cursor.lastrowid

    # Step 2: Insert/retrieve English words
    english_word_ids = []
    for translation in translations:
        cursor.execute("""
            INSERT OR IGNORE INTO english_words (word, pos_type)
            VALUES (?, ?)
        """, (translation, pos.name))

        eng_id = cursor.execute("""
            SELECT id FROM english_words WHERE word = ? AND pos_type = ?
        """, (translation, pos.name)).fetchone()[0]

        english_word_ids.append(eng_id)

    # Step 3: Create translation links
    for eng_id in english_word_ids:
        cursor.execute("""
            INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type)
            VALUES (?, ?, ?)
        """, (eng_id, greek_word_id, pos.name))

    self._conn.commit()

    # Step 4: Build and return Word object
    fake_row = {
        'id': greek_word_id,
        'lemma': lemma,
        'translations': '|'.join(translations)
    }
    return self._create_word_from_row(sqlite3.Row(fake_row), pos)

except Exception as e:
    self._conn.rollback()
    raise
```

## Error Handling

| Error Type | Handling | Exception |
|------------|----------|-----------|
| Empty translations | Validate early | `ValueError("At least one translation required")` |
| Empty lemma | Validate early | `ValueError("Lemma cannot be empty")` |
| Duplicate lemma | Check before insert | `ValueError(f"Word '{lemma}' already exists")` |
| Morpheus failure | Catch and wrap | `ValueError(f"Failed to generate forms: {error}")` |
| No forms generated | Check after Morpheus | `ValueError("Morpheus generated no forms")` |
| Database errors | Rollback transaction | Let `sqlite3.Error` propagate |

## Testing Strategy

1. **Happy path**: Add valid noun/verb/adjective with translations
2. **Duplicate detection**: Attempt to add existing word
3. **Empty inputs**: Test validation of empty lemma/translations
4. **Morpheus failures**: Test with invalid lemma that Morpheus can't handle
5. **Transaction rollback**: Simulate DB error mid-transaction
6. **Field inference**: Verify gender/verb_group correctly extracted
7. **Multiple translations**: Verify all translations linked correctly

## Example Usage

```python
manager = LexicalManager("vocab.db")

# Add a noun
word = manager.add_word(
    lemma="άνθρωπος",
    translations=["person", "human", "man"],
    pos=PartOfSpeech.NOUN
)
print(word.lemma)  # άνθρωπος
print(word.translations)  # ["person", "human", "man"]

# Try to add duplicate - raises ValueError
manager.add_word("άνθρωπος", ["person"], PartOfSpeech.NOUN)  # ❌ ValueError
```

## Related Code

- `syntaxis/database/manager.py` - Location for new method
- `syntaxis/database/mask_calculator.py` - Mask calculation logic
- `syntaxis/morpheus.py` - Form generation
- `syntaxis/database/schema.py` - Table structures
- `syntaxis/database/bitmasks.py` - POS_TO_TABLE_MAP mapping
