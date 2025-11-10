# Refactor: Enum to String Constants

**Date:** 2025-11-10
**Status:** Design Approved

## Overview

Refactor syntaxis from enum-based constants to string-based constants, establishing morpheus as a translation layer (DTO) between modern_greek_inflexion and the rest of syntaxis.

## Goals

1. **Simplify constant usage** - Replace heavy-handed enums with lightweight string constants
2. **Clear separation of concerns** - Isolate modern_greek_inflexion constants from syntaxis constants
3. **Establish morpheus as DTO** - Make morpheus the single translation point between libraries
4. **Complete isolation** - No syntaxis code outside morpheus should reference modern_greek_inflexion

## Design Decisions

### Constant Format

**Grammatical features:** Abbreviated strings
- Gender: `"masc"`, `"fem"`, `"neut"`
- Number: `"sg"`, `"pl"`
- Case: `"nom"`, `"acc"`, `"gen"`, `"voc"`
- Person: `"1"`, `"2"`, `"3"`
- Tense: `"pres"`, `"aor"`, `"imperf"`, `"fut"`, `"fut_s"`
- Voice: `"act"`, `"pass"`
- Mood: `"ind"`, `"imp"`
- Aspect: `"perf"`, `"imperf"`

**Part of speech:** Full words
- `"noun"`, `"verb"`, `"adjective"`, `"adverb"`, `"article"`, `"pronoun"`, `"numeral"`, `"preposition"`, `"conjunction"`

**Rationale:** Abbreviated grammatical terms match linguistic conventions while remaining readable. Full POS names improve clarity and match class names.

### Architecture

**Constants location:** `syntaxis/models/constants.py`
**Morpheus structure:** Package with flat organization
- `syntaxis/morpheus/__init__.py` - Exports
- `syntaxis/morpheus/api.py` - Main Morpheus class
- `syntaxis/morpheus/mappings.py` - Translation mappings
- `syntaxis/morpheus/translator.py` - Forms dictionary translation

**Translation strategy:** Full bidirectional translation
- Morpheus accepts syntaxis constants
- Morpheus translates to mgi for library calls
- Morpheus translates all results back to syntaxis constants
- Forms dictionaries use syntaxis constants as keys at all levels

**Migration strategy:** Big bang replacement
- Create new structure, update everything at once
- Remove enums entirely in single changeset
- Accept higher initial risk for cleaner end result

## Implementation Details

### 1. Constants Definition

**File:** `syntaxis/models/constants.py`

```python
# Part of speech
NOUN = "noun"
VERB = "verb"
ADJECTIVE = "adjective"
ADVERB = "adverb"
ARTICLE = "article"
PRONOUN = "pronoun"
NUMERAL = "numeral"
PREPOSITION = "preposition"
CONJUNCTION = "conjunction"

# Gender
MASCULINE = "masc"
FEMININE = "fem"
NEUTER = "neut"

# Number
SINGULAR = "sg"
PLURAL = "pl"

# Case
NOMINATIVE = "nom"
ACCUSATIVE = "acc"
GENITIVE = "gen"
VOCATIVE = "voc"

# Tense
PRESENT = "pres"
AORIST = "aor"
PARATATIKOS = "imperf"
FUTURE = "fut"
FUTURE_SIMPLE = "fut_s"

# Voice
ACTIVE = "act"
PASSIVE = "pass"

# Mood
INDICATIVE = "ind"
IMPERATIVE = "imp"

# Person
FIRST = "1"
SECOND = "2"
THIRD = "3"

# Aspect
PERFECT = "perf"
IMPERFECT = "imperf"
```

### 2. Translation Mappings

**File:** `syntaxis/morpheus/mappings.py`

```python
from modern_greek_inflexion import resources
from syntaxis.models import constants as c

SYNTAXIS_TO_MGI = {
    # Gender
    c.MASCULINE: resources.MASC,
    c.FEMININE: resources.FEM,
    c.NEUTER: resources.NEUT,
    # Number
    c.SINGULAR: resources.SG,
    c.PLURAL: resources.PL,
    # Case
    c.NOMINATIVE: resources.NOM,
    c.ACCUSATIVE: resources.ACC,
    c.GENITIVE: resources.GEN,
    c.VOCATIVE: resources.VOC,
    # Tense
    c.PRESENT: resources.PRESENT,
    c.AORIST: resources.AORIST,
    c.PARATATIKOS: resources.PARATATIKOS,
    # Voice
    c.ACTIVE: resources.ACTIVE,
    c.PASSIVE: resources.PASSIVE,
    # Mood
    c.INDICATIVE: resources.IND,
    c.IMPERATIVE: resources.IMP,
    # Person
    c.FIRST: resources.PRI,
    c.SECOND: resources.SEC,
    c.THIRD: resources.TER,
    # Aspect
    c.PERFECT: resources.PERF,
    c.IMPERFECT: resources.IMPERF,
}

MGI_TO_SYNTAXIS = {v: k for k, v in SYNTAXIS_TO_MGI.items()}
```

### 3. Forms Translation

**File:** `syntaxis/morpheus/translator.py`

```python
from syntaxis.morpheus.mappings import MGI_TO_SYNTAXIS

def translate_forms(forms: dict | set) -> dict | set:
    """Recursively translate mgi forms to syntaxis constants.

    Walks nested dictionary structure, replacing all mgi constant keys
    with syntaxis string constants. Preserves word form sets unchanged.
    """
    if isinstance(forms, set):
        return forms

    if isinstance(forms, dict):
        translated = {}
        for key, value in forms.items():
            new_key = MGI_TO_SYNTAXIS.get(key, key)
            translated[new_key] = translate_forms(value)
        return translated

    return forms
```

### 4. Morpheus API

**File:** `syntaxis/morpheus/api.py`

```python
from typing import TypeVar
import modern_greek_inflexion as mgi

from syntaxis.models import constants as c
from syntaxis.models.part_of_speech import (
    Adjective, Adverb, Article, Conjunction, Noun,
    Numberal, Preposition, Pronoun, Verb
)
from syntaxis.morpheus.translator import translate_forms

T = TypeVar("T", Adjective, Adverb, Article, Noun, Numberal, Pronoun, Verb, Preposition)

class Morpheus:
    """Translation layer between modern_greek_inflexion and syntaxis."""

    @staticmethod
    def create(lemma: str, pos: str) -> T:
        """Create POS instance from lemma using syntaxis constants."""
        method_map = {
            c.NOUN: Morpheus.noun,
            c.VERB: Morpheus.verb,
            c.ADJECTIVE: Morpheus.adjective,
            c.ARTICLE: Morpheus.article,
            c.PRONOUN: Morpheus.pronoun,
            c.ADVERB: Morpheus.adverb,
            c.NUMERAL: Morpheus.numeral,
            c.PREPOSITION: Morpheus.preposition,
            c.CONJUNCTION: Morpheus.conjunction,
        }
        return method_map[pos](lemma)

    @staticmethod
    def _get_inflected_forms(lemma: str, pos_class: type[T]) -> T:
        """Get forms from mgi and translate to syntaxis constants."""
        mgi_class = getattr(mgi, pos_class.__name__)
        mgi_forms = mgi_class(lemma).all()
        syntaxis_forms = translate_forms(mgi_forms)
        return pos_class(lemma, syntaxis_forms)

    # POS-specific methods
    @staticmethod
    def noun(lemma: str) -> Noun:
        return Morpheus._get_inflected_forms(lemma, Noun)

    # ... (similar for other inflecting POS)

    @staticmethod
    def preposition(lemma: str) -> Preposition:
        return Preposition(lemma, forms={"prep": {lemma}})

    @staticmethod
    def conjunction(lemma: str) -> Conjunction:
        return Conjunction(lemma, forms={"conj": {lemma}})
```

**File:** `syntaxis/morpheus/__init__.py`

```python
from syntaxis.morpheus.api import Morpheus

__all__ = ["Morpheus"]
```

### 5. Part of Speech Classes

**File:** `syntaxis/models/part_of_speech.py`

Key changes:
- All type hints change from enum types to `str`
- Default parameters use string constants: `case: str = c.NOMINATIVE`
- Remove enum attribute access (no more `.value`)
- Remove debug trace at line 83

```python
@dataclass
class Verb(PartOfSpeech[types.Verb]):
    def get_form(self, tense: str, voice: str, number: str, person: str,
                 case: str = c.NOMINATIVE, mood: str = c.INDICATIVE,
                 **extra) -> set[str]:
        return self.forms[tense][voice][mood][number][person]
```

### 6. Database Layer

**File:** `syntaxis/database/manager.py`

Changes:
- Remove `MORPHEUS_TO_ENUM` mapping (no longer needed)
- Remove `normalize_feature()` function
- Update method signatures to use `str` instead of enum types
- Update queries to use string constants directly
- No more `.value` calls on enums

```python
def get_random_word(self, pos: str, **features: str) -> PartOfSpeechBase | None:
    """Get random word using string constants."""
    # Uses string feature values directly in queries
```

### 7. Template Layer

**File:** `syntaxis/templates/models.py`

```python
from syntaxis.models import constants as c

@dataclass
class TokenFeatures:
    pos: str  # Changed from PartOfSpeech enum
    case: str | None = None
    gender: str | None = None
    number: str | None = None
    tense: str | None = None
    voice: str | None = None
    person: str | None = None

    def is_inflectable(self) -> bool:
        return self.pos in {c.NOUN, c.VERB, c.ADJECTIVE, c.ARTICLE, c.PRONOUN}

    def is_invariable(self) -> bool:
        return self.pos in {c.PREPOSITION, c.CONJUNCTION, c.ADVERB}
```

**File:** `syntaxis/templates/parser.py`

- Update to parse string constants instead of enums
- Update template parsing to return string values

## Files to Delete

- `syntaxis/models/enums.py` - Replaced by `constants.py`
- `syntaxis/morpheus.py` - Replaced by `syntaxis/morpheus/` package

## Files to Update

All files currently importing from `syntaxis.models.enums`:
- `syntaxis/database/manager.py`
- `syntaxis/database/bitmasks.py`
- `syntaxis/templates/models.py`
- `syntaxis/templates/parser.py`
- All test files
- All documentation files

## Migration Checklist

1. Create `syntaxis/models/constants.py`
2. Create `syntaxis/morpheus/` package structure
3. Implement translation mappings and logic
4. Update part of speech classes
5. Update database layer
6. Update template layer
7. Update all tests
8. Delete old enum-based code
9. Run full test suite
10. Update documentation

## Benefits

1. **Simpler API** - Direct string usage, no enum imports needed
2. **Better separation** - Clear boundary between syntaxis and mgi
3. **Easier testing** - String literals in tests more readable than enum construction
4. **Maintainability** - Single point (morpheus) to update when mgi changes
5. **Cleaner code** - No more `.value` calls scattered throughout

## Risks

1. **Type safety** - Lose compile-time checking of enum values
2. **Typos** - String typos won't be caught until runtime
3. **Big bang risk** - Large changeset, harder to debug if issues arise

## Mitigations

1. Use constants module - centralize strings, reduce typos
2. Comprehensive test coverage - catch string issues in tests
3. Type hints with Literal types (optional future enhancement)
