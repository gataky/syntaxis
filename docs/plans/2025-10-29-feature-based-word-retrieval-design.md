# Feature-Based Word Retrieval Design

**Date:** 2025-10-29
**Status:** Approved

## Overview

This design extends the `LexicalManager.get_random_word()` method to support efficient feature-based filtering using bitmask columns in the database. Words can be retrieved by part of speech with optional grammatical feature filters (gender, case, number, tense, etc.).

## Goals

1. Implement `get_random_word(pos: POSEnum, **features)` to retrieve random words matching specified grammatical features
2. Use bitmask columns for efficient database-level feature filtering
3. Return fully-formed PartOfSpeech objects with inflected forms and translations
4. Validate features are appropriate for each part of speech type

## Database Schema Updates

### Bitmask Columns by Table

Each table will add INTEGER columns for bitmask storage of available features:

**greek_nouns:**
- `number_mask` INTEGER (SINGULAR=1, PLURAL=2)
- `case_mask` INTEGER (NOMINATIVE=1, VOCATIVE=2, ACCUSATIVE=4, GENITIVE=8)
- Keep existing `gender` TEXT column (intrinsic property)

**greek_verbs:**
- `tense_mask` INTEGER (AORIST=1, PARATATIKOS=2, PRESENT=4, FUTURE=8, FUTURE_SIMPLE=16)
- `voice_mask` INTEGER (ACTIVE=1, PASSIVE=2)
- `mood_mask` INTEGER (INDICATIVE=1, IMPERATIVE=2)
- `number_mask` INTEGER (SINGULAR=1, PLURAL=2)
- `person_mask` INTEGER (FIRST=1, SECOND=2, THIRD=4)
- `case_mask` INTEGER (NOMINATIVE=1, VOCATIVE=2, ACCUSATIVE=4, GENITIVE=8)

**greek_adjectives:**
- `number_mask` INTEGER (SINGULAR=1, PLURAL=2)
- `case_mask` INTEGER (NOMINATIVE=1, VOCATIVE=2, ACCUSATIVE=4, GENITIVE=8)

**greek_articles:**
- `gender_mask` INTEGER (MASCULINE=1, FEMININE=2, NEUTER=4)
- `number_mask` INTEGER (SINGULAR=1, PLURAL=2)
- `case_mask` INTEGER (NOMINATIVE=1, VOCATIVE=2, ACCUSATIVE=4, GENITIVE=8)

**greek_pronouns:**
- `gender_mask` INTEGER (MASCULINE=1, FEMININE=2, NEUTER=4)
- `number_mask` INTEGER (SINGULAR=1, PLURAL=2)
- `case_mask` INTEGER (NOMINATIVE=1, VOCATIVE=2, ACCUSATIVE=4, GENITIVE=8)
- Keep existing `person` TEXT column (intrinsic property)

**greek_adverbs, greek_prepositions, greek_conjunctions:**
- No changes (no variable features)

### Bitmask Design

- Each feature dimension gets its own INTEGER column
- Enum values map to bit positions: first member = 1, second = 2, third = 4, etc.
- Multiple available values combine with bitwise OR
- Queries use bitwise AND to check feature availability

**Example:** A noun with SINGULAR and PLURAL forms has `number_mask = 3` (1 | 2)

## Implementation Components

### 1. Bitmask Helper Module (`syntaxis/database/bitmasks.py`)

```python
from enum import Enum
from typing import Iterable

def enum_to_bit(enum_value: Enum) -> int:
    """Convert enum to its bit position (1, 2, 4, 8, ...)"""
    members = list(type(enum_value).__members__.values())
    position = members.index(enum_value)
    return 1 << position

def build_mask(enum_values: Iterable[Enum]) -> int:
    """Combine multiple enum values into a bitmask"""
    mask = 0
    for value in enum_values:
        mask |= enum_to_bit(value)
    return mask

def has_feature(mask: int, feature: Enum) -> bool:
    """Check if a bitmask contains a specific feature"""
    return (mask & enum_to_bit(feature)) != 0

# Maps POS to its valid feature names
VALID_FEATURES: dict[POSEnum, set[str]] = {
    POSEnum.NOUN: {'gender', 'number', 'case'},
    POSEnum.VERB: {'tense', 'voice', 'mood', 'number', 'person', 'case'},
    POSEnum.ADJECTIVE: {'number', 'case'},
    POSEnum.ARTICLE: {'gender', 'number', 'case'},
    POSEnum.PRONOUN: {'gender', 'number', 'case'},
    POSEnum.ADVERB: set(),
    POSEnum.PREPOSITION: set(),
    POSEnum.CONJUNCTION: set(),
}

# Maps POS enum to database table name
POS_TO_TABLE_MAP: dict[POSEnum, str] = {
    POSEnum.NOUN: 'greek_nouns',
    POSEnum.VERB: 'greek_verbs',
    POSEnum.ADJECTIVE: 'greek_adjectives',
    POSEnum.ARTICLE: 'greek_articles',
    POSEnum.PRONOUN: 'greek_pronouns',
    POSEnum.ADVERB: 'greek_adverbs',
    POSEnum.PREPOSITION: 'greek_prepositions',
    POSEnum.CONJUNCTION: 'greek_conjunctions',
}
```

### 2. Enhanced Morpheus (`syntaxis/morpheus.py`)

Add a generic method to Morpheus for creating any POS type:

```python
@staticmethod
def create(lemma: str, pos: POSEnum) -> PartOfSpeechBase:
    """Generic method to create any POS type from lemma."""
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
```

### 3. LexicalManager Methods

#### `get_random_word()`

```python
def get_random_word(
    self,
    pos: POSEnum,
    **features: Any
) -> PartOfSpeechBase | None:
    """Get a random word of the specified part of speech.

    Args:
        pos: Part of speech enum (POSEnum.NOUN, POSEnum.VERB, etc.)
        **features: Feature filters as enum values
                    (gender=Gender.MASCULINE, case=Case.NOMINATIVE, etc.)

    Returns:
        Instance of appropriate PartOfSpeech subclass with forms and
        translations, or None if no matches

    Raises:
        ValueError: If invalid features provided for the POS type
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

#### `_create_word_from_row()`

```python
def _create_word_from_row(
    self,
    row: sqlite3.Row,
    pos: POSEnum
) -> PartOfSpeechBase:
    """Create PartOfSpeech object with translations from query result.

    Args:
        row: Database row with id, lemma, and translations
        pos: Part of speech enum

    Returns:
        Complete PartOfSpeech object with forms and translations
    """
    lemma = row['lemma']
    translations_str = row['translations']

    # Parse translations (GROUP_CONCAT returns pipe-delimited string)
    translations = translations_str.split('|') if translations_str else None

    # Create word with inflected forms using Morpheus
    word = Morpheus.create(lemma, pos)
    word.translations = translations

    return word
```

#### `_calculate_masks_for_word()`

```python
def _calculate_masks_for_word(
    self,
    lemma: str,
    pos: POSEnum
) -> dict[str, int]:
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

    # Inspect forms dictionary structure based on POS type
    # Example for Noun: forms[gender][number][case]
    if pos == POSEnum.NOUN:
        available_numbers = set()
        available_cases = set()

        for gender_dict in word.forms.values():
            for number_key, number_dict in gender_dict.items():
                available_numbers.add(number_key)
                for case_key in number_dict.keys():
                    available_cases.add(case_key)

        masks['number_mask'] = build_mask(available_numbers)
        masks['case_mask'] = build_mask(available_cases)

    elif pos == POSEnum.VERB:
        # Similar inspection for verb forms
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

        masks['tense_mask'] = build_mask(available_tenses)
        masks['voice_mask'] = build_mask(available_voices)
        masks['mood_mask'] = build_mask(available_moods)
        masks['number_mask'] = build_mask(available_numbers)
        masks['person_mask'] = build_mask(available_persons)
        masks['case_mask'] = build_mask(available_cases)

    # Similar logic for other POS types...

    return masks
```

## Schema Migration

The schema will need to be updated to add bitmask columns. This will be handled by:

1. Updating `create_schema()` in `syntaxis/database/schema.py` to include mask columns
2. For existing databases, providing a migration script to add columns and populate them
3. When inserting new words, calling `_calculate_masks_for_word()` to populate mask values

## Error Handling

- **Invalid features for POS**: Raise `ValueError` with clear message showing valid features
- **No matching words**: Return `None` (normal case, not an error)
- **Empty database**: Return `None`

## Usage Examples

```python
# Get a random noun in singular nominative case with masculine gender
manager = LexicalManager("greek.db")
word = manager.get_random_word(
    POSEnum.NOUN,
    number=Number.SINGULAR,
    case=Case.NOMINATIVE,
    gender=Gender.MASCULINE
)

# Get any verb in present tense, active voice
word = manager.get_random_word(
    POSEnum.VERB,
    tense=Tense.PRESENT,
    voice=Voice.ACTIVE
)

# Get any adjective (no feature filters)
word = manager.get_random_word(POSEnum.ADJECTIVE)
```

## Testing Considerations

1. Test feature validation for each POS type
2. Test bitmask calculation for words with various form availability
3. Test query correctness with multiple feature filters
4. Test translation retrieval in single query
5. Test edge cases (no matches, no translations, etc.)

## Performance Notes

- Bitmask operations `(column & value) != 0` are fast integer operations
- Single query design minimizes database round trips
- `ORDER BY RANDOM() LIMIT 1` is efficient for random selection in SQLite
- Indexes on mask columns may improve performance for large datasets
