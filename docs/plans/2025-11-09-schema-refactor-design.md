# Schema Refactoring: From Bitmasks to Feature Columns

**Date:** 2025-11-09
**Status:** Approved

## Overview

Refactor the database schema from bitmask-based feature storage to explicit feature columns. This change addresses three primary pain points: code readability, query complexity, and extensibility.

## Problem Statement

The current bitmask system creates challenges across the codebase:
- **Hard to understand and debug:** Bitmask operations obscure the actual data model
- **Difficult to query and filter:** SQL queries require complex bitwise operations
- **Hard to add new features:** New grammatical features require updating bitmask logic throughout

## Requirements

- **Query pattern:** Support finding words with specific feature combinations (e.g., "masculine singular nominative noun")
- **Table structure:** Keep separate tables per part of speech (greek_nouns, greek_verbs, etc.)
- **Row strategy:** Multiple rows per lemma (one row per valid feature combination)
- **Migration:** Start fresh database (no migration from old schema needed)

## Architecture: Direct Feature Rows

Each database row represents one lemma with one valid feature combination. Features are stored as explicit TEXT columns instead of bitmasks.

### Design Rationale

**Why multiple rows per lemma?**
- Simplifies queries (direct column comparison vs bitmask operations)
- Makes data model transparent and debuggable
- Each row clearly shows one valid grammatical form

**Why keep separate tables?**
- Each POS has different relevant features
- Avoids nullable column proliferation in a unified table
- Maintains logical separation matching linguistic structure

## Schema Structure

### Complex POS Tables (with inflections)

**greek_nouns:**
```sql
CREATE TABLE greek_nouns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    gender TEXT NOT NULL,        -- 'M', 'F', 'N'
    number TEXT NOT NULL,         -- 'SINGULAR', 'PLURAL'
    case_name TEXT NOT NULL,      -- 'NOMINATIVE', 'GENITIVE', 'ACCUSATIVE', 'VOCATIVE'
    validation_status TEXT NOT NULL,
    UNIQUE(lemma, gender, number, case_name)
)
```

**greek_verbs:**
```sql
CREATE TABLE greek_verbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    verb_group TEXT,
    tense TEXT,
    voice TEXT,
    mood TEXT,
    number TEXT,
    person TEXT,
    case_name TEXT,              -- For participles
    validation_status TEXT NOT NULL,
    UNIQUE(lemma, verb_group, tense, voice, mood, number, person, case_name)
)
```

**greek_adjectives:**
```sql
CREATE TABLE greek_adjectives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    gender TEXT,
    number TEXT,
    case_name TEXT,
    validation_status TEXT NOT NULL,
    UNIQUE(lemma, gender, number, case_name)
)
```

**greek_articles:**
```sql
CREATE TABLE greek_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    gender TEXT,
    number TEXT,
    case_name TEXT,
    validation_status TEXT NOT NULL,
    UNIQUE(lemma, gender, number, case_name)
)
```

**greek_pronouns:**
```sql
CREATE TABLE greek_pronouns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    type TEXT NOT NULL,          -- 'personal_strong', 'personal_weak', 'demonstrative', etc.
    person TEXT,
    gender TEXT,
    number TEXT,
    case_name TEXT,
    validation_status TEXT NOT NULL,
    UNIQUE(lemma, type, person, gender, number, case_name)
)
```

### Simple POS Tables (no inflections)

**greek_adverbs, greek_prepositions, greek_conjunctions:**
```sql
CREATE TABLE greek_[pos_type] (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL UNIQUE,
    validation_status TEXT NOT NULL
)
```

### Translations Table (Updated)

```sql
CREATE TABLE translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    english_word_id INTEGER NOT NULL,
    greek_lemma TEXT NOT NULL,
    greek_pos_type TEXT NOT NULL,
    FOREIGN KEY (english_word_id) REFERENCES english_words(id),
    UNIQUE(english_word_id, greek_lemma, greek_pos_type)
)
```

**Key change:** Links to `greek_lemma` (TEXT) instead of `greek_word_id` (INTEGER). This means one translation entry per lemma regardless of how many feature rows exist.

### English Words Table (Unchanged)

```sql
CREATE TABLE english_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    pos_type TEXT NOT NULL
)
```

## Data Flow

### Adding Words (add_word)

1. Validate inputs (lemma non-empty, translations provided)
2. Check if lemma already exists (query for any row with that lemma)
3. Call `Morpheus.create(lemma, pos)` to generate all inflected forms
4. Extract feature combinations by iterating through Morpheus forms structure
5. Insert one row per valid feature combination
6. Insert/link English translations (one entry per lemma in translations table)

**Example:** Adding "άνθρωπος" (man, masculine noun)
- Morpheus generates: `{"M": {"SINGULAR": {"NOMINATIVE": "άνθρωπος", "GENITIVE": "ανθρώπου", ...}, "PLURAL": {...}}}`
- Extract 8 feature combinations (4 cases × 2 numbers)
- Insert 8 rows into greek_nouns, each with same lemma but different features
- Insert 1 entry into translations linking lemma to "man"

### Querying Words (get_random_word)

```sql
SELECT DISTINCT g.lemma, GROUP_CONCAT(e.word, '|') as translations
FROM greek_nouns g
LEFT JOIN translations t ON t.greek_lemma = g.lemma AND t.greek_pos_type = ?
LEFT JOIN english_words e ON e.id = t.english_word_id
WHERE g.number = 'SINGULAR' AND g.case_name = 'NOMINATIVE'
GROUP BY g.lemma
ORDER BY RANDOM()
LIMIT 1
```

**Key simplification:** Direct column comparisons (`g.number = 'SINGULAR'`) instead of bitmask operations (`(g.number_mask & ?) != 0`).

## Component Changes

### Files to Modify

**1. syntaxis/database/schema.py**
- Replace all `*_mask` columns with explicit TEXT feature columns
- Update translations table to use `greek_lemma TEXT` instead of `greek_word_id INTEGER`
- Add UNIQUE constraints for feature combinations

**2. syntaxis/database/manager.py**
- **add_word():** Extract features from Morpheus forms, insert multiple rows per lemma
- **get_random_word():** Simplify queries to use direct column comparisons
- **_create_word_from_row():** Handle multiple rows with same lemma (use DISTINCT on lemma)
- **POS_CONFIG:** Update to reflect new column names (remove `*_mask` fields)

**3. syntaxis/database/seed_pronouns.py**
- Update to insert multiple rows per pronoun (one per valid feature combination)
- Update to use new translations table structure (lemma-based linking)

### Files to Delete

**1. syntaxis/database/bitmasks.py**
- No longer needed (no bitmask operations)
- May keep `POS_TO_TABLE_MAP` and `VALID_FEATURES` if useful for validation

**2. syntaxis/database/mask_calculator.py**
- No longer needed (Morpheus directly provides feature combinations)

## Error Handling

### Validation During add_word()
1. Check if lemma already exists before processing
2. Validate Morpheus returns forms successfully
3. Verify forms structure before inserting
4. Use transaction to ensure atomicity (all feature rows inserted or none)

### Edge Cases
- **Morpheus failure:** Raise ValueError with descriptive message
- **Duplicate lemma:** Detect early and raise clear error
- **No forms returned:** Validate and fail fast
- **Translation duplicates:** Use `INSERT OR IGNORE` for english_words

### Query Validation
- Keep existing feature validation against `VALID_FEATURES`
- Remove bitmask conversion logic
- SQL errors will be clearer with direct column comparisons

## Testing Strategy

1. Test add_word() with various POS types:
   - Nouns (multiple genders)
   - Verbs (complex feature combinations)
   - Pronouns (with new type column)
   - Adverbs (simple, no features)

2. Test get_random_word() with different filters:
   - Single feature filter
   - Multiple feature filters
   - Non-existent feature combinations

3. Verify Morpheus integration:
   - Forms generated correctly
   - Features extracted properly
   - All valid combinations stored

4. Test translation linking:
   - Lemma-based links work correctly
   - Translations retrieved for all feature variations
   - No duplicate translation entries

## Success Criteria

- All SQL queries use direct column comparisons (no bitmask operations)
- Code is readable and debuggable
- Adding new grammatical features requires only schema changes
- All existing functionality preserved (word addition, querying, translations)
- Tests pass for all POS types
