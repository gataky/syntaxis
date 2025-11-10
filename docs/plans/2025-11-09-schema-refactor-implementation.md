# Schema Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace bitmask-based feature storage with explicit feature columns for improved readability and queryability.

**Architecture:** Direct feature rows approach - each database row represents one lemma with one valid feature combination. Features stored as TEXT columns instead of INTEGER bitmasks. Translation links updated to reference lemmas instead of row IDs.

**Tech Stack:** SQLite, Python 3.12+, modern-greek-inflexion (Morpheus)

**Testing Strategy:** Implementation first, tests added later or when they make sense (not TDD).

---

## Task 1: Update Schema - Replace Bitmasks with Feature Columns

**Files:**
- Modify: `syntaxis/database/schema.py`

**Step 1: Update greek_nouns table**

Replace the current table definition:

```python
# OLD (lines 25-37)
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_nouns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL UNIQUE,
        gender_mask TEXT NOT NULL,
        number_mask INTEGER,
        case_mask INTEGER,
        validation_status TEXT NOT NULL
    )
"""
)
```

With the new feature-column based definition:

```python
# NEW
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_nouns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        gender TEXT NOT NULL,
        number TEXT NOT NULL,
        case_name TEXT NOT NULL,
        validation_status TEXT NOT NULL,
        UNIQUE(lemma, gender, number, case_name)
    )
"""
)
```

**Step 2: Update greek_verbs table**

Replace the current table definition:

```python
# OLD (lines 39-55)
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
```

With:

```python
# NEW
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_verbs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        verb_group TEXT,
        tense TEXT,
        voice TEXT,
        mood TEXT,
        number TEXT,
        person TEXT,
        case_name TEXT,
        validation_status TEXT NOT NULL,
        UNIQUE(lemma, verb_group, tense, voice, mood, number, person, case_name)
    )
"""
)
```

**Step 3: Update greek_adjectives table**

Replace:

```python
# OLD (lines 57-69)
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_adjectives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL UNIQUE,
        gender_mask INTEGER,
        number_mask INTEGER,
        case_mask INTEGER,
        validation_status TEXT NOT NULL
    )
"""
)
```

With:

```python
# NEW
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_adjectives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        gender TEXT,
        number TEXT,
        case_name TEXT,
        validation_status TEXT NOT NULL,
        UNIQUE(lemma, gender, number, case_name)
    )
"""
)
```

**Step 4: Update greek_articles table**

Replace:

```python
# OLD (lines 71-83)
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
```

With:

```python
# NEW
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        gender TEXT,
        number TEXT,
        case_name TEXT,
        validation_status TEXT NOT NULL,
        UNIQUE(lemma, gender, number, case_name)
    )
"""
)
```

**Step 5: Update greek_pronouns table**

Replace:

```python
# OLD (lines 85-99)
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_pronouns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        person TEXT,
        gender_mask INTEGER,
        number_mask INTEGER,
        case_mask INTEGER,
        validation_status TEXT NOT NULL
    )
"""
)
```

With:

```python
# NEW
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS greek_pronouns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL,
        type TEXT NOT NULL,
        person TEXT,
        gender TEXT,
        number TEXT,
        case_name TEXT,
        validation_status TEXT NOT NULL,
        UNIQUE(lemma, type, person, gender, number, case_name)
    )
"""
)
```

**Step 6: Update translations table**

Replace:

```python
# OLD (lines 133-145)
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        english_word_id INTEGER NOT NULL,
        greek_word_id INTEGER NOT NULL,
        greek_pos_type TEXT NOT NULL,
        FOREIGN KEY (english_word_id) REFERENCES english_words(id),
        UNIQUE(english_word_id, greek_word_id, greek_pos_type)
    )
"""
)
```

With:

```python
# NEW
_ = cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        english_word_id INTEGER NOT NULL,
        greek_lemma TEXT NOT NULL,
        greek_pos_type TEXT NOT NULL,
        FOREIGN KEY (english_word_id) REFERENCES english_words(id),
        UNIQUE(english_word_id, greek_lemma, greek_pos_type)
    )
"""
)
```

**Step 7: Commit schema changes**

```bash
git add syntaxis/database/schema.py
git commit -m "refactor: replace bitmask columns with explicit feature columns

Update all POS tables to use TEXT columns for features instead of
INTEGER bitmasks. Update translations table to link to lemmas instead
of row IDs. Add UNIQUE constraints for feature combinations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Update LexicalManager - Simplify get_random_word Queries

**Files:**
- Modify: `syntaxis/database/manager.py:43-114`

**Step 1: Remove bitmask imports**

At the top of `manager.py`, remove the bitmask-related imports:

```python
# REMOVE these lines (around lines 4-8)
from syntaxis.database.bitmasks import (
    POS_TO_TABLE_MAP,
    VALID_FEATURES,
    enum_to_bit,
)
from syntaxis.database.mask_calculator import STRING_TO_ENUM, calculate_masks_for_word
```

Keep only:

```python
from syntaxis.database.bitmasks import POS_TO_TABLE_MAP, VALID_FEATURES
```

**Step 2: Update get_random_word method**

Replace the current implementation (lines 43-114) with:

```python
def get_random_word(
    self, pos: PartOfSpeech, **features: Any
) -> PartOfSpeechBase | None:
    """Get a random word of the specified part of speech.

    Args:
        pos: Part of speech enum (PartOfSpeech.NOUN, PartOfSpeech.VERB, etc.)
        **features: Feature filters as enum values
                    (gender=Gender.MASCULINE, case_name=Case.NOMINATIVE, etc.)

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
            + f"Valid features are: {valid_features}"
        )

    cursor = self._conn.cursor()
    table = POS_TO_TABLE_MAP[pos]

    # Build WHERE conditions using direct column comparisons
    conditions = []
    params: list[str] = [pos.name]  # For JOIN condition

    for feature_name, feature_value in features.items():
        # Convert enum to string (e.g., Number.SINGULAR -> "SINGULAR")
        feature_str = feature_value.name
        conditions.append(f"g.{feature_name} = ?")
        params.append(feature_str)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Query with DISTINCT to handle multiple rows per lemma
    query = f"""
        SELECT DISTINCT
            g.lemma,
            GROUP_CONCAT(e.word, '|') as translations
        FROM {table} g
        LEFT JOIN translations t ON t.greek_lemma = g.lemma
            AND t.greek_pos_type = ?
        LEFT JOIN english_words e ON e.id = t.english_word_id
        WHERE {where_clause}
        GROUP BY g.lemma
        ORDER BY RANDOM()
        LIMIT 1
    """

    row = cursor.execute(query, params).fetchone()
    if not row:
        return None

    word = self._create_word_from_row(row, pos)
    return word
```

**Step 3: Commit query simplification**

```bash
git add syntaxis/database/manager.py
git commit -m "refactor: simplify get_random_word to use direct column comparisons

Replace bitmask operations with straightforward WHERE clauses using
feature column equality. Use DISTINCT and GROUP BY lemma to handle
multiple rows per lemma.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Update LexicalManager - Refactor add_word for Multiple Rows

**Files:**
- Modify: `syntaxis/database/manager.py:238-431`

**Step 1: Create feature extraction helper**

Add a new method after `_create_word_from_row` (around line 237):

```python
def _extract_features_from_morpheus(
    self, word: PartOfSpeechBase, pos: PartOfSpeech
) -> list[dict[str, str | None]]:
    """Extract all valid feature combinations from Morpheus-generated forms.

    Args:
        word: PartOfSpeech object with forms generated by Morpheus
        pos: Part of speech type

    Returns:
        List of feature dictionaries, one per valid combination

    Examples:
        For a noun: [
            {"gender": "M", "number": "SINGULAR", "case_name": "NOMINATIVE"},
            {"gender": "M", "number": "SINGULAR", "case_name": "GENITIVE"},
            ...
        ]
    """
    features_list = []

    if pos == PartOfSpeech.NOUN:
        # Forms structure: {gender: {number: {case: form}}}
        for gender, number_dict in word.forms.items():
            for number, case_dict in number_dict.items():
                for case_name, form in case_dict.items():
                    if form:  # Only if form exists
                        features_list.append({
                            "gender": gender,
                            "number": number,
                            "case_name": case_name,
                        })

    elif pos == PartOfSpeech.VERB:
        # Forms structure: {tense: {voice: {mood: {number: {person: form}}}}}
        # Or for participles: {...: {case: form}}
        verb_group = getattr(word, "verb_group", None)
        for tense, voice_dict in word.forms.items():
            for voice, mood_dict in voice_dict.items():
                for mood, number_dict in mood_dict.items():
                    for number, person_or_case_dict in number_dict.items():
                        for person_or_case, form in person_or_case_dict.items():
                            if form:
                                # Check if this is a participle (has case) or regular verb (has person)
                                if mood == "PARTICIPLE":
                                    features_list.append({
                                        "verb_group": verb_group,
                                        "tense": tense,
                                        "voice": voice,
                                        "mood": mood,
                                        "number": number,
                                        "person": None,
                                        "case_name": person_or_case,
                                    })
                                else:
                                    features_list.append({
                                        "verb_group": verb_group,
                                        "tense": tense,
                                        "voice": voice,
                                        "mood": mood,
                                        "number": number,
                                        "person": person_or_case,
                                        "case_name": None,
                                    })

    elif pos in [PartOfSpeech.ADJECTIVE, PartOfSpeech.ARTICLE]:
        # Forms structure: {gender: {number: {case: form}}}
        for gender, number_dict in word.forms.items():
            for number, case_dict in number_dict.items():
                for case_name, form in case_dict.items():
                    if form:
                        features_list.append({
                            "gender": gender,
                            "number": number,
                            "case_name": case_name,
                        })

    elif pos == PartOfSpeech.PRONOUN:
        # Pronouns are complex - for now, store minimal info
        # Will be populated by seed file with proper type/person/gender/number/case
        features_list.append({
            "type": "personal_strong",  # Default, will be overridden by seed
            "person": None,
            "gender": None,
            "number": None,
            "case_name": None,
        })

    elif pos in [PartOfSpeech.ADVERB, PartOfSpeech.PREPOSITION, PartOfSpeech.CONJUNCTION]:
        # Simple POS - just one entry
        features_list.append({})

    return features_list
```

**Step 2: Update POS_CONFIG**

Replace the POS_CONFIG dictionary (around lines 238-299) with:

```python
POS_CONFIG = {
    PartOfSpeech.NOUN: {
        "table": "greek_nouns",
        "fields": ["lemma", "gender", "number", "case_name", "validation_status"],
    },
    PartOfSpeech.VERB: {
        "table": "greek_verbs",
        "fields": [
            "lemma",
            "verb_group",
            "tense",
            "voice",
            "mood",
            "number",
            "person",
            "case_name",
            "validation_status",
        ],
    },
    PartOfSpeech.ADJECTIVE: {
        "table": "greek_adjectives",
        "fields": ["lemma", "gender", "number", "case_name", "validation_status"],
    },
    PartOfSpeech.ARTICLE: {
        "table": "greek_articles",
        "fields": ["lemma", "gender", "number", "case_name", "validation_status"],
    },
    PartOfSpeech.PRONOUN: {
        "table": "greek_pronouns",
        "fields": [
            "lemma",
            "type",
            "person",
            "gender",
            "number",
            "case_name",
            "validation_status",
        ],
    },
    PartOfSpeech.ADVERB: {
        "table": "greek_adverbs",
        "fields": ["lemma", "validation_status"],
    },
    PartOfSpeech.PREPOSITION: {
        "table": "greek_prepositions",
        "fields": ["lemma", "validation_status"],
    },
    PartOfSpeech.CONJUNCTION: {
        "table": "greek_conjunctions",
        "fields": ["lemma", "validation_status"],
    },
}
```

**Step 3: Update _prepare_database_values**

Replace `_prepare_database_values` method (around lines 328-355) with:

```python
def _prepare_database_values(
    self, lemma: str, pos: PartOfSpeech, word: PartOfSpeechBase, features: dict[str, str | None]
) -> dict[str, str | int | None]:
    """Prepare values for one database row (one feature combination).

    Args:
        lemma: Greek word lemma
        pos: Part of speech
        word: Morpheus-generated word object
        features: Feature dictionary for this specific row

    Returns:
        Dictionary mapping field names to values for INSERT
    """
    config = self.POS_CONFIG[pos]
    fields = config["fields"]

    values: dict[str, str | int | None] = {
        "lemma": lemma,
        "validation_status": "VALID",
    }

    # Add all features from the dictionary
    for key, value in features.items():
        if key in fields:
            values[key] = value

    # Ensure all fields have a value (None for missing ones)
    for field in fields:
        if field not in values:
            values[field] = None

    return values
```

**Step 4: Update _execute_add_word_transaction**

Replace `_execute_add_word_transaction` method (around lines 357-404) with:

```python
def _execute_add_word_transaction(
    self, pos: PartOfSpeech, lemma: str, values_list: list[dict[str, Any]], translations: list[str]
) -> None:
    """Execute database transaction to add word with multiple feature rows.

    Args:
        pos: Part of speech
        lemma: Greek word lemma
        values_list: List of value dictionaries (one per feature combination)
        translations: English translations
    """
    table = POS_TO_TABLE_MAP[pos]
    config = self.POS_CONFIG[pos]
    fields = config["fields"]
    cursor = self._conn.cursor()

    try:
        # Step 1: Insert all Greek word rows (one per feature combination)
        columns = ", ".join(fields)
        placeholders = ", ".join(["?"] * len(fields))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        for values in values_list:
            cursor.execute(sql, [values.get(field) for field in fields])

        # Step 2: Insert/retrieve English words
        english_word_ids = []
        for translation in translations:
            translation = translation.strip()
            cursor.execute(
                "INSERT OR IGNORE INTO english_words (word, pos_type) VALUES (?, ?)",
                (translation, pos.name),
            )
            eng_id_row = cursor.execute(
                "SELECT id FROM english_words WHERE word = ? AND pos_type = ?",
                (translation, pos.name),
            ).fetchone()
            if eng_id_row:
                english_word_ids.append(eng_id_row[0])

        # Step 3: Create translation links (one per lemma, not per row)
        for eng_id in english_word_ids:
            cursor.execute(
                "INSERT OR IGNORE INTO translations (english_word_id, greek_lemma, greek_pos_type) VALUES (?, ?, ?)",
                (eng_id, lemma, pos.name),
            )

        self._conn.commit()

    except Exception:
        self._conn.rollback()
        raise
```

**Step 5: Update add_word method**

Replace the `add_word` method (around lines 406-431) with:

```python
def add_word(
    self, lemma: str, translations: list[str], pos: PartOfSpeech
) -> PartOfSpeechBase:
    """Add a word to the lexicon with automatic feature extraction.

    Args:
        lemma: Greek word in its base form
        translations: List of English translations (at least one required)
        pos: Part of speech enum

    Returns:
        Complete PartOfSpeech object with forms and translations

    Raises:
        ValueError: If translations empty, lemma empty, word exists, or Morpheus fails
    """
    # Validate inputs
    word = self._validate_and_prepare_lemma(lemma, pos, translations)

    # Extract all valid feature combinations from Morpheus forms
    features_list = self._extract_features_from_morpheus(word, pos)

    if not features_list:
        raise ValueError(f"No valid feature combinations found for '{lemma}'")

    # Prepare database values for each feature combination
    values_list = [
        self._prepare_database_values(lemma, pos, word, features)
        for features in features_list
    ]

    # Execute transaction to insert all rows
    self._execute_add_word_transaction(pos, lemma, values_list, translations)

    # Retrieve and return the word
    new_word = self._get_word_by_lemma(lemma, pos)
    if not new_word:
        raise RuntimeError(f"Failed to retrieve newly added word '{lemma}'")
    return new_word
```

**Step 6: Add _get_word_by_lemma helper**

Add this new method after `_get_word_by_id` (around line 212):

```python
def _get_word_by_lemma(self, lemma: str, pos: PartOfSpeech):
    """Helper to retrieve a word by its lemma and POS.

    Args:
        lemma: Greek word lemma
        pos: Part of speech

    Returns:
        Word object or None if not found
    """
    cursor = self._conn.cursor()
    table = POS_TO_TABLE_MAP[pos]

    # Query with JOIN to get lemma and translations
    query = f"""
        SELECT DISTINCT
            g.lemma,
            GROUP_CONCAT(e.word, '|') as translations
        FROM {table} g
        LEFT JOIN translations t ON t.greek_lemma = g.lemma
            AND t.greek_pos_type = ?
        LEFT JOIN english_words e ON e.id = t.english_word_id
        WHERE g.lemma = ?
        GROUP BY g.lemma
    """

    row = cursor.execute(query, (pos.name, lemma)).fetchone()
    if not row:
        return None

    return self._create_word_from_row(row, pos)
```

**Step 7: Commit add_word refactoring**

```bash
git add syntaxis/database/manager.py
git commit -m "refactor: update add_word to insert multiple feature rows

Extract feature combinations from Morpheus forms and insert one row
per valid combination. Update translation links to reference lemmas.
Add helper methods for feature extraction and lemma-based retrieval.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Update get_words_by_english Query

**Files:**
- Modify: `syntaxis/database/manager.py:138-178`

**Step 1: Update get_words_by_english method**

Replace the method (lines 138-178) with:

```python
def get_words_by_english(
    self, english_word: str, pos: PartOfSpeech | None = None
) -> list:
    """Find all Greek words that translate to the given English word.

    Args:
        english_word: English word to search for
        pos: Optional filter by part of speech

    Returns:
        List of Word objects (mixed types) with english_translations populated
    """
    results = []
    pos_to_check = [pos] if pos else list(POS_TO_TABLE_MAP.keys())

    for pos_enum in pos_to_check:
        if pos_enum not in POS_TO_TABLE_MAP:
            continue

        table = POS_TO_TABLE_MAP[pos_enum]
        query = f"""
            SELECT DISTINCT
                g.lemma,
                GROUP_CONCAT(e_all.word, '|') as translations
            FROM {table} g
            JOIN translations t ON t.greek_lemma = g.lemma AND t.greek_pos_type = ?
            JOIN english_words e ON e.id = t.english_word_id
            LEFT JOIN translations t_all ON t_all.greek_lemma = g.lemma AND t_all.greek_pos_type = ?
            LEFT JOIN english_words e_all ON e_all.id = t_all.english_word_id
            WHERE e.word = ?
            GROUP BY g.lemma
        """
        cursor = self._conn.cursor()
        rows = cursor.execute(
            query, (pos_enum.name, pos_enum.name, english_word)
        ).fetchall()
        for row in rows:
            results.append(self._create_word_from_row(row, pos_enum))

    return results
```

**Step 2: Commit query update**

```bash
git add syntaxis/database/manager.py
git commit -m "refactor: update get_words_by_english to use lemma-based links

Update query to join on greek_lemma instead of greek_word_id.
Add DISTINCT to handle multiple rows per lemma.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Update Seed File for New Schema

**Files:**
- Modify: `syntaxis/database/seed_pronouns.py`

**Step 1: Update seed_pronouns to insert feature rows**

Replace the entire `seed_pronouns` function with:

```python
def seed_pronouns(conn: sqlite3.Connection) -> None:
    """Populate greek_pronouns table with Modern Greek pronouns.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Define pronouns by type with explicit feature combinations
    # Format: (lemma, type, person, gender, number, case_name, validation_status)
    pronouns = [
        # Personal Strong Pronouns - Nominative
        ("εγώ",   "personal_strong", "1", None, "SINGULAR", "NOMINATIVE", "validated"),
        ("εσύ",   "personal_strong", "2", None, "SINGULAR", "NOMINATIVE", "validated"),
        ("αυτός", "personal_strong", "3", "M",  "SINGULAR", "NOMINATIVE", "validated"),
        ("αυτή",  "personal_strong", "3", "F",  "SINGULAR", "NOMINATIVE", "validated"),
        ("αυτό",  "personal_strong", "3", "N",  "SINGULAR", "NOMINATIVE", "validated"),
        ("εμείς", "personal_strong", "1", None, "PLURAL",   "NOMINATIVE", "validated"),
        ("εσείς", "personal_strong", "2", None, "PLURAL",   "NOMINATIVE", "validated"),
        ("αυτοί", "personal_strong", "3", "M",  "PLURAL",   "NOMINATIVE", "validated"),
        ("αυτές", "personal_strong", "3", "F",  "PLURAL",   "NOMINATIVE", "validated"),
        ("αυτά",  "personal_strong", "3", "N",  "PLURAL",   "NOMINATIVE", "validated"),

        # Personal Weak Pronouns - Genitive
        ("μου",  "personal_weak", "1", None, "SINGULAR", "GENITIVE", "validated"),
        ("σου",  "personal_weak", "2", None, "SINGULAR", "GENITIVE", "validated"),
        ("του",  "personal_weak", "3", "M",  "SINGULAR", "GENITIVE", "validated"),
        ("της",  "personal_weak", "3", "F",  "SINGULAR", "GENITIVE", "validated"),
        ("μας",  "personal_weak", "1", None, "PLURAL",   "GENITIVE", "validated"),
        ("σας",  "personal_weak", "2", None, "PLURAL",   "GENITIVE", "validated"),
        ("τους", "personal_weak", "3", None, "PLURAL",   "GENITIVE", "validated"),

        # Personal Weak Pronouns - Accusative
        ("με",  "personal_weak", "1", None, "SINGULAR", "ACCUSATIVE", "validated"),
        ("σε",  "personal_weak", "2", None, "SINGULAR", "ACCUSATIVE", "validated"),
        ("τον", "personal_weak", "3", "M",  "SINGULAR", "ACCUSATIVE", "validated"),
        ("την", "personal_weak", "3", "F",  "SINGULAR", "ACCUSATIVE", "validated"),
        ("το",  "personal_weak", "3", "N",  "SINGULAR", "ACCUSATIVE", "validated"),
        ("μας", "personal_weak", "1", None, "PLURAL",   "ACCUSATIVE", "validated"),
        ("σας", "personal_weak", "2", None, "PLURAL",   "ACCUSATIVE", "validated"),
        ("τους","personal_weak", "3", "M",  "PLURAL",   "ACCUSATIVE", "validated"),
        ("τις", "personal_weak", "3", "F",  "PLURAL",   "ACCUSATIVE", "validated"),
        ("τα",  "personal_weak", "3", "N",  "PLURAL",   "ACCUSATIVE", "validated"),

        # Demonstrative Pronouns - sample forms
        ("τούτος",  "demonstrative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("τούτη",   "demonstrative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("τούτο",   "demonstrative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("εκείνος", "demonstrative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("εκείνη",  "demonstrative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("εκείνο",  "demonstrative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),

        # Interrogative Pronouns
        ("ποιος", "interrogative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("ποια",  "interrogative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("ποιο",  "interrogative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("τι",    "interrogative", None, None, None, None, "validated"),
        ("πόσος", "interrogative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("πόση",  "interrogative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("πόσο",  "interrogative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),

        # Possessive Pronouns
        ("δικός", "possessive", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("δική",  "possessive", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("δικό",  "possessive", None, "N", "SINGULAR", "NOMINATIVE", "validated"),

        # Indefinite Pronouns
        ("κάποιος", "indefinite", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("κάποια",  "indefinite", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("κάποιο",  "indefinite", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("κανείς",  "indefinite", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("καμία",   "indefinite", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("κανένα",  "indefinite", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("κάθε",    "indefinite", None, None, None, None, "validated"),
        ("όλος",    "indefinite", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("όλη",     "indefinite", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("όλο",     "indefinite", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("μερικοί", "indefinite", None, "M", "PLURAL", "NOMINATIVE", "validated"),
        ("μερικές", "indefinite", None, "F", "PLURAL", "NOMINATIVE", "validated"),
        ("μερικά",  "indefinite", None, "N", "PLURAL", "NOMINATIVE", "validated"),
        ("κάτι",    "indefinite", None, None, None, None, "validated"),
        ("τίποτα",  "indefinite", None, None, None, None, "validated"),

        # Relative Pronouns
        ("που",    "relative", None, None, None, None, "validated"),
        ("οποίος", "relative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("οποία",  "relative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("οποίο",  "relative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("όποιος", "relative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("όποια",  "relative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("όποιο",  "relative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
    ]

    # Insert pronouns
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_pronouns
        (lemma, type, person, gender, number, case_name, validation_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        pronouns
    )

    conn.commit()
    print(f"Seeded {cursor.rowcount} pronoun forms into greek_pronouns table")
```

**Step 2: Commit seed file update**

```bash
git add syntaxis/database/seed_pronouns.py
git commit -m "refactor: update seed_pronouns for new schema structure

Insert feature rows with explicit gender/number/case values instead
of bitmasks. Each pronoun form is one row with specific features.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Clean Up Obsolete Files

**Files:**
- Delete: `syntaxis/database/mask_calculator.py`
- Modify: `syntaxis/database/bitmasks.py` (keep only useful parts)

**Step 1: Delete mask_calculator.py**

```bash
git rm syntaxis/database/mask_calculator.py
```

**Step 2: Simplify bitmasks.py**

Keep only the mapping constants. Replace entire file contents with:

```python
"""Mapping constants for database tables and valid features."""

from syntaxis.models.enums import PartOfSpeech as POSEnum

# Maps POS to its valid feature names
VALID_FEATURES: dict[POSEnum, set[str]] = {
    POSEnum.NOUN: {"gender", "number", "case_name"},
    POSEnum.VERB: {"tense", "voice", "mood", "number", "person", "case_name"},
    POSEnum.ADJECTIVE: {"gender", "number", "case_name"},
    POSEnum.ARTICLE: {"gender", "number", "case_name"},
    POSEnum.PRONOUN: {"gender", "number", "case_name", "person", "type"},
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

**Step 3: Commit cleanup**

```bash
git add syntaxis/database/bitmasks.py
git commit -m "refactor: remove bitmask logic, keep only mapping constants

Delete mask_calculator.py entirely. Simplify bitmasks.py to only
contain POS_TO_TABLE_MAP and VALID_FEATURES mappings.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Test Basic Functionality

**Files:**
- Create: `test_refactor.py` (temporary test script)

**Step 1: Create manual test script**

Create `test_refactor.py` in project root:

```python
"""Manual test script for schema refactor."""

import sqlite3
from syntaxis.database.schema import create_schema
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeech, Number, Case

def test_schema_creation():
    """Test that new schema creates successfully."""
    print("Testing schema creation...")
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()

    # Check that tables exist and have correct columns
    tables_to_check = [
        ("greek_nouns", ["lemma", "gender", "number", "case_name", "validation_status"]),
        ("greek_verbs", ["lemma", "verb_group", "tense", "voice", "mood", "number", "person", "case_name", "validation_status"]),
        ("translations", ["english_word_id", "greek_lemma", "greek_pos_type"]),
    ]

    for table, expected_columns in tables_to_check:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        for col in expected_columns:
            assert col in columns, f"Column {col} missing from {table}"
        print(f"  ✓ {table} has correct columns")

    conn.close()
    print("✓ Schema creation successful\n")

def test_add_word():
    """Test adding a word with new schema."""
    print("Testing add_word...")
    manager = LexicalManager()

    # Add a simple noun
    word = manager.add_word("άνθρωπος", ["man", "person"], PartOfSpeech.NOUN)
    assert word is not None
    assert word.lemma == "άνθρωπος"
    assert "man" in word.translations
    print(f"  ✓ Added word: {word.lemma}")
    print(f"  ✓ Translations: {word.translations}")

    # Check database has multiple rows
    cursor = manager._conn.cursor()
    rows = cursor.execute(
        "SELECT lemma, gender, number, case_name FROM greek_nouns WHERE lemma = ?",
        ("άνθρωπος",)
    ).fetchall()
    print(f"  ✓ Created {len(rows)} feature rows")
    for row in rows[:3]:  # Show first 3
        print(f"    - {row}")

    print("✓ add_word successful\n")

def test_get_random_word():
    """Test querying with new schema."""
    print("Testing get_random_word...")
    manager = LexicalManager()

    # Add some words
    manager.add_word("άνθρωπος", ["man"], PartOfSpeech.NOUN)
    manager.add_word("γυναίκα", ["woman"], PartOfSpeech.NOUN)

    # Query with features
    word = manager.get_random_word(
        PartOfSpeech.NOUN,
        number=Number.SINGULAR,
        case_name=Case.NOMINATIVE
    )

    assert word is not None
    print(f"  ✓ Found word: {word.lemma}")
    print(f"  ✓ Translations: {word.translations}")
    print("✓ get_random_word successful\n")

if __name__ == "__main__":
    test_schema_creation()
    test_add_word()
    test_get_random_word()
    print("✅ All manual tests passed!")
```

**Step 2: Run test script**

```bash
uv run python test_refactor.py
```

Expected output:
```
Testing schema creation...
  ✓ greek_nouns has correct columns
  ✓ greek_verbs has correct columns
  ✓ translations has correct columns
✓ Schema creation successful

Testing add_word...
  ✓ Added word: άνθρωπος
  ✓ Translations: ['man', 'person']
  ✓ Created 8 feature rows
    - ('άνθρωπος', 'M', 'SINGULAR', 'NOMINATIVE')
    - ('άνθρωπος', 'M', 'SINGULAR', 'GENITIVE')
    - ('άνθρωπος', 'M', 'SINGULAR', 'ACCUSATIVE')
✓ add_word successful

Testing get_random_word...
  ✓ Found word: άνθρωπος
  ✓ Translations: ['man']
✓ get_random_word successful

✅ All manual tests passed!
```

**Step 3: Commit test verification**

```bash
git add test_refactor.py
git commit -m "test: add manual verification script for schema refactor

Create temporary test script to verify basic functionality:
- Schema creation with new columns
- add_word creates multiple feature rows
- get_random_word queries with direct comparisons

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Update or Fix Failing Tests (Optional - When Makes Sense)

**Note:** Tests will be updated later or when they make sense. This task is optional for now.

**Files that will need test updates eventually:**
- `tests/database/test_manager.py` - Update to expect feature columns
- `tests/database/test_schema.py` - Update to verify new schema
- `tests/database/test_bitmasks.py` - Delete or repurpose
- `tests/database/test_mask_calculator.py` - Delete

**When ready to fix tests, focus on:**
1. Updating assertions to expect feature column names instead of bitmasks
2. Removing bitmask-related test utilities
3. Adding tests for multiple-row-per-lemma behavior
4. Verifying lemma-based translation links

---

## Summary

After completing this plan, the system will:
- ✅ Use explicit TEXT feature columns instead of INTEGER bitmasks
- ✅ Store multiple rows per lemma (one per valid feature combination)
- ✅ Link translations to lemmas instead of row IDs
- ✅ Support simple, readable SQL queries with direct column comparisons
- ✅ Remove obsolete bitmask calculation code
- ✅ Maintain all existing functionality with improved clarity

**Next steps after implementation:**
1. Delete `test_refactor.py` temporary script
2. Update existing tests when needed
3. Add comprehensive tests for new feature extraction logic
4. Consider adding database migration utility for future schema changes
