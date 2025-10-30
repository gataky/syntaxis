# Code Audit and Improvement Suggestions

This document outlines suggestions for improving the codebase, focusing on readability, maintainability, and performance.

## 1. `syntaxis.database.manager.LexicalManager`

The `LexicalManager` class is generally well-structured, but some methods can be refactored for better clarity and efficiency.

### 1.1. Refactor `add_word` to Reduce Code Duplication

The `add_word` method uses a large `if/elif` block to handle different parts of speech. This can be made more data-driven.

**Suggestion:**

Create a configuration dictionary that maps each part of speech to its table name and relevant fields. This will allow you to build the `INSERT` query dynamically and reduce the repetitive code.

**Example:**

```python
# In LexicalManager or a separate config file
POS_CONFIG = {
    POSEnum.NOUN: {
        "table": "greek_nouns",
        "fields": ["lemma", "gender", "number_mask", "case_mask", "validation_status"],
    },
    POSEnum.VERB: {
        "table": "greek_verbs",
        "fields": ["lemma", "verb_group", "tense_mask", "voice_mask", "mood_mask", "number_mask", "person_mask", "case_mask", "validation_status"],
    },
    # ... other POS types
}

def add_word(self, lemma: str, translations: list[str], pos: POSEnum) -> PartOfSpeechBase:
    # ... (validation logic)

    config = POS_CONFIG[pos]
    table = config["table"]
    fields = config["fields"]

    # ... (generate forms and masks)

    values = {
        "lemma": lemma,
        "validation_status": "VALID",
        # ... other fields from masks and inferred properties
    }

    # Ensure all fields in the config are present in the values dict
    for field in fields:
        if field not in values:
            values[field] = masks.get(f"{field}_mask", 0) # Or some other default

    columns = ", ".join(fields)
    placeholders = ", ".join(["?"] * len(fields))
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    cursor.execute(sql, [values[field] for field in fields])

    # ... (the rest of the method)
```

### 1.2. Optimize `get_words_by_english`

The `get_words_by_english` method currently performs multiple queries in a loop (an N+1 problem). This can be optimized into a single query using `JOIN`.

**Suggestion:**

Rewrite the method to use a single query that joins the `english_words`, `translations`, and the appropriate Greek word table.

**Example:**

```python
def get_words_by_english(self, english_word: str, pos: POSEnum | None = None) -> list:
    results = []
    pos_to_check = [pos] if pos else list(POS_TO_TABLE_MAP.keys())

    for pos_enum in pos_to_check:
        table = POS_TO_TABLE_MAP[pos_enum]
        query = f"""
            SELECT
                g.id,
                g.lemma,
                GROUP_CONCAT(e_all.word, '|') as translations
            FROM {table} g
            JOIN translations t ON t.greek_word_id = g.id AND t.greek_pos_type = ?
            JOIN english_words e ON e.id = t.english_word_id
            LEFT JOIN translations t_all ON t_all.greek_word_id = g.id AND t_all.greek_pos_type = ?
            LEFT JOIN english_words e_all ON e_all.id = t_all.english_word_id
            WHERE e.word = ?
            GROUP BY g.id, g.lemma
        """
        cursor = self._conn.cursor()
        rows = cursor.execute(query, (pos_enum.name, pos_enum.name, english_word)).fetchall()
        for row in rows:
            results.append(self._create_word_from_row(row, pos_enum))

    return results
```

### 1.3. Add Comments to `get_random_word`

The `get_random_word` method is complex. Adding comments to explain the query construction would be beneficial.

**Suggestion:**

Add comments to explain the dynamic `WHERE` clause construction and the `GROUP_CONCAT` usage.

## 2. `syntaxis.database.mask_calculator.py`

The `calculate_masks_for_word` function can be refactored to improve readability and reduce code duplication.

**Suggestion:**

The nested structure for traversing the `forms` dictionary is different for each POS. We can define a "path" for each feature for each POS, and then have a generic function that traverses the `forms` dictionary.

**Example:**

```python
# In mask_calculator.py
FEATURE_PATHS = {
    POSEnum.NOUN: {
        "number": (1,), # Path to the number key in the forms dict
        "case": (1, 1), # Path to the case key
    },
    POSEnum.VERB: {
        "tense": (0,),
        "voice": (0, 0),
        "mood": (0, 0, 0),
        "number": (0, 0, 0, 0),
        "person": (0, 0, 0, 0, 0),
    },
    # ... other POS types
}

def _traverse_forms(forms: dict, path: tuple) -> set:
    """Helper to traverse the nested forms dictionary."""
    keys = set()
    # ... logic to traverse the dictionary based on the path
    return keys

def calculate_masks_for_word(lemma: str, pos: POSEnum) -> dict[str, int]:
    word = Morpheus.create(lemma, pos)
    masks = {}
    if pos in FEATURE_PATHS:
        for feature, path in FEATURE_PATHS[pos].items():
            available_enums = {STRING_TO_ENUM[key] for key in _traverse_forms(word.forms, path) if key in STRING_TO_ENUM}
            masks[f"{feature}_mask"] = build_mask(available_enums)
    return masks
```
This is a conceptual example. The actual implementation of `_traverse_forms` would need to be carefully written to handle the different dictionary structures.

## 3. Schema Design (Long-Term Suggestion)

The current schema with a separate table for each part of speech is workable, but it leads to more complex and repetitive code in the `LexicalManager`.

**Suggestion:**

For a future major version, consider migrating to a single `words` table. This table would have a `pos` column, and features could be stored in a JSON column.

**Example Schema:**

```sql
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    pos TEXT NOT NULL,
    features TEXT, -- JSON object
    translations TEXT, -- JSON array of strings
    validation_status TEXT NOT NULL,
    UNIQUE(lemma, pos)
);
```

This would simplify queries and the `LexicalManager` code significantly. However, this is a large change and should be considered carefully.
