# Enum to String Constants Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace enum-based constants with string-based constants and establish morpheus as translation layer between modern_greek_inflexion and syntaxis.

**Architecture:** Create constants.py for syntaxis strings, refactor morpheus into package with bidirectional translation, update all code to use string constants directly.

**Tech Stack:** Python 3.12+, modern-greek-inflexion, pytest

---

## Task 1: Create Constants Module

**Files:**
- Create: `syntaxis/models/constants.py`

**Step 1: Create constants.py with all string constants**

Create file `syntaxis/models/constants.py`:

```python
"""String constants for syntaxis grammatical features.

These constants define the canonical string representations used throughout
syntaxis. The morpheus module handles translation to/from modern_greek_inflexion.
"""

# Part of speech constants
NOUN = "noun"
VERB = "verb"
ADJECTIVE = "adjective"
ADVERB = "adverb"
ARTICLE = "article"
PRONOUN = "pronoun"
NUMERAL = "numeral"
PREPOSITION = "preposition"
CONJUNCTION = "conjunction"

# Gender constants
MASCULINE = "masc"
FEMININE = "fem"
NEUTER = "neut"

# Number constants
SINGULAR = "sg"
PLURAL = "pl"

# Case constants
NOMINATIVE = "nom"
ACCUSATIVE = "acc"
GENITIVE = "gen"
VOCATIVE = "voc"

# Tense constants
PRESENT = "pres"
AORIST = "aor"
PARATATIKOS = "imperf"
FUTURE = "fut"
FUTURE_SIMPLE = "fut_s"

# Voice constants
ACTIVE = "act"
PASSIVE = "pass"

# Mood constants
INDICATIVE = "ind"
IMPERATIVE = "imp"

# Person constants
FIRST = "1"
SECOND = "2"
THIRD = "3"

# Aspect constants
PERFECT = "perf"
IMPERFECT = "imperf"
```

**Step 2: Verify file was created correctly**

Run: `cat syntaxis/models/constants.py | head -20`
Expected: File exists and shows first 20 lines including docstring and constants

**Step 3: Commit constants module**

```bash
git add syntaxis/models/constants.py
git commit -m "feat: add string constants module

Replace enums with lightweight string constants.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Create Morpheus Package Structure

**Files:**
- Create: `syntaxis/morpheus/__init__.py`
- Create: `syntaxis/morpheus/mappings.py`
- Create: `syntaxis/morpheus/translator.py`
- Create: `syntaxis/morpheus/api.py`

**Step 1: Create morpheus directory**

Run: `mkdir -p syntaxis/morpheus`
Expected: Directory created

**Step 2: Create mappings.py with translation dictionaries**

Create file `syntaxis/morpheus/mappings.py`:

```python
"""Translation mappings between syntaxis and modern_greek_inflexion constants."""

from modern_greek_inflexion import resources
from syntaxis.models import constants as c

# Syntaxis -> modern_greek_inflexion mappings
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

# Reverse mapping for translating mgi results back to syntaxis
MGI_TO_SYNTAXIS = {v: k for k, v in SYNTAXIS_TO_MGI.items()}
```

**Step 3: Create translator.py with forms translation logic**

Create file `syntaxis/morpheus/translator.py`:

```python
"""Translation logic for forms dictionaries."""

from syntaxis.morpheus.mappings import MGI_TO_SYNTAXIS


def translate_forms(forms: dict | set) -> dict | set:
    """Recursively translate mgi forms dictionary to syntaxis constants.

    Args:
        forms: Nested dictionary or set from modern_greek_inflexion

    Returns:
        Translated structure with syntaxis constants as keys

    Examples:
        Input:  {resources.MASC: {resources.SG: {resources.NOM: {'άνθρωπος'}}}}
        Output: {'masc': {'sg': {'nom': {'άνθρωπος'}}}}
    """
    if isinstance(forms, set):
        return forms  # Terminal case: set of word forms

    if isinstance(forms, dict):
        translated = {}
        for key, value in forms.items():
            # Translate key if it's an mgi constant, otherwise keep as-is
            new_key = MGI_TO_SYNTAXIS.get(key, key)
            # Recursively translate nested structures
            translated[new_key] = translate_forms(value)
        return translated

    return forms  # Fallback for any other type
```

**Step 4: Create api.py with Morpheus class**

Create file `syntaxis/morpheus/api.py`:

```python
"""Morpheus: Translation layer between modern_greek_inflexion and syntaxis."""

from typing import TypeVar

import modern_greek_inflexion as mgi

from syntaxis.models import constants as c
from syntaxis.models.part_of_speech import (
    Adjective,
    Adverb,
    Article,
    Conjunction,
    Noun,
    Numberal,
    Preposition,
    Pronoun,
    Verb,
)
from syntaxis.morpheus.translator import translate_forms

T = TypeVar("T", Adjective, Adverb, Article, Noun, Numberal, Pronoun, Verb, Preposition)


class Morpheus:
    """Translation layer between modern_greek_inflexion and syntaxis.

    This class handles all interaction with modern_greek_inflexion,
    translating between mgi's constants and syntaxis's string constants.
    """

    @staticmethod
    def create(lemma: str, pos: str) -> T:
        """Generic method to create any POS type from lemma.

        Args:
            lemma: The base form of the word
            pos: Part of speech string constant (c.NOUN, c.VERB, etc.)

        Returns:
            Appropriate PartOfSpeech subclass with forms using syntaxis constants

        Raises:
            KeyError: If pos is not in the method map

        Examples:
            >>> Morpheus.create("άνθρωπος", c.NOUN)
            Noun(lemma="άνθρωπος", forms={...})
        """
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
        """Generic method to get inflected forms for any part of speech.

        Gets forms from modern_greek_inflexion and translates to syntaxis constants.
        """
        # Map our classes to the mgi classes
        mgi_class = getattr(mgi, pos_class.__name__)
        mgi_forms = mgi_class(lemma).all()
        syntaxis_forms = translate_forms(mgi_forms)
        return pos_class(lemma, syntaxis_forms)

    @staticmethod
    def adjective(lemma: str) -> Adjective:
        return Morpheus._get_inflected_forms(lemma, Adjective)

    @staticmethod
    def adverb(lemma: str) -> Adverb:
        return Morpheus._get_inflected_forms(lemma, Adverb)

    @staticmethod
    def article(lemma: str) -> Article:
        return Morpheus._get_inflected_forms(lemma, Article)

    @staticmethod
    def noun(lemma: str) -> Noun:
        return Morpheus._get_inflected_forms(lemma, Noun)

    @staticmethod
    def numeral(lemma: str) -> Numberal:
        return Morpheus._get_inflected_forms(lemma, Numberal)

    @staticmethod
    def pronoun(lemma: str) -> Pronoun:
        return Morpheus._get_inflected_forms(lemma, Pronoun)

    @staticmethod
    def verb(lemma: str) -> Verb:
        return Morpheus._get_inflected_forms(lemma, Verb)

    # The following POS don't exist in modern_greek_inflexion
    # because they don't inflect in any way. So we "inflect"
    # them ourselves by returning a forms like dict with the
    # lemma as the declined word.

    @staticmethod
    def preposition(lemma: str) -> Preposition:
        return Preposition(lemma, forms={"prep": {lemma}})

    @staticmethod
    def conjunction(lemma: str) -> Conjunction:
        return Conjunction(lemma, forms={"conj": {lemma}})
```

**Step 5: Create __init__.py to export Morpheus**

Create file `syntaxis/morpheus/__init__.py`:

```python
"""Morpheus package: Translation layer for modern_greek_inflexion."""

from syntaxis.morpheus.api import Morpheus

__all__ = ["Morpheus"]
```

**Step 6: Verify package structure**

Run: `ls -la syntaxis/morpheus/`
Expected: Shows __init__.py, api.py, mappings.py, translator.py

**Step 7: Commit morpheus package**

```bash
git add syntaxis/morpheus/
git commit -m "feat: create morpheus package with translation layer

Establish morpheus as DTO between modern_greek_inflexion and syntaxis.
Includes bidirectional translation of constants and forms dictionaries.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Update Part of Speech Models

**Files:**
- Modify: `syntaxis/models/part_of_speech.py`

**Step 1: Update imports to use constants instead of enums**

In `syntaxis/models/part_of_speech.py`, replace:

```python
from syntaxis.models import enums, types
```

With:

```python
from syntaxis.models import constants as c
from syntaxis.models import types
```

**Step 2: Update Adjective.get_form() signature**

Replace:

```python
def get_form(self, gender: enums.Gender, number: enums.Number, case: enums.Case, **extra) -> set[str]:
    return self.forms["adj"][number][gender][case]
```

With:

```python
def get_form(self, gender: str, number: str, case: str, **extra) -> set[str]:
    return self.forms["adj"][number][gender][case]
```

**Step 3: Update Adverb.get_form() signature**

Replace:

```python
def get_form(self, **extra) -> set[str]:
    return self.forms[enums.PartOfSpeech.ADVERB]
```

With:

```python
def get_form(self, **extra) -> set[str]:
    return self.forms[c.ADVERB]
```

**Step 4: Update Article.get_form() signature**

Replace:

```python
def get_form(
    self, number: enums.Number, gender: enums.Gender, case: enums.Case, **extra
) -> set[str]:
    return self.forms[number][gender][case]
```

With:

```python
def get_form(self, number: str, gender: str, case: str, **extra) -> set[str]:
    return self.forms[number][gender][case]
```

**Step 5: Update Noun.get_form() signature**

Replace:

```python
def get_form(
    self,
    gender: enums.Gender,
    number: enums.Number,
    case: enums.Case,
    **extra
) -> set[str]:
    return self.forms[gender][number][case]
```

With:

```python
def get_form(self, gender: str, number: str, case: str, **extra) -> set[str]:
    return self.forms[gender][number][case]
```

**Step 6: Update Numberal.get_form() signature**

Replace:

```python
def get_form(
    self, number: enums.Number, gender: enums.Gender, case: enums.Case, **extra
) -> set[str]:
    return self.forms[enums.PartOfSpeech.ADJECTIVE][number][gender][case]
```

With:

```python
def get_form(self, number: str, gender: str, case: str, **extra) -> set[str]:
    return self.forms[c.ADJECTIVE][number][gender][case]
```

**Step 7: Update Pronoun.get_form() signature**

Replace:

```python
def get_form(
    self, number: enums.Number, gender: enums.Gender, case: enums.Case, **extra
) -> set[str]:
    return self.forms[number][gender][case]
```

With:

```python
def get_form(self, number: str, gender: str, case: str, **extra) -> set[str]:
    return self.forms[number][gender][case]
```

**Step 8: Update Verb.get_form() signature and remove debug trace**

Replace:

```python
def get_form(
    self,
    tense: enums.Tense,
    voice: enums.Voice,
    number: enums.Number,
    person: enums.Person,
    case: enums.Case = enums.Case.NOMINATIVE.value,
    mood: enums.Mood = enums.Mood.INDICATIVE.value,
    **extra,
) -> set[str]:
    import pudb; pudb.set_trace()
    return self.forms[tense][voice][mood][number][person]
```

With:

```python
def get_form(
    self,
    tense: str,
    voice: str,
    number: str,
    person: str,
    case: str = c.NOMINATIVE,
    mood: str = c.INDICATIVE,
    **extra,
) -> set[str]:
    return self.forms[tense][voice][mood][number][person]
```

**Step 9: Verify changes**

Run: `cat syntaxis/models/part_of_speech.py`
Expected: No imports from enums, all signatures use str, no debug trace

**Step 10: Commit part of speech updates**

```bash
git add syntaxis/models/part_of_speech.py
git commit -m "refactor: update part of speech models to use string constants

Replace enum types with strings, remove debug trace from Verb.get_form.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Update Database Manager

**Files:**
- Modify: `syntaxis/database/manager.py`

**Step 1: Update imports**

Replace:

```python
from syntaxis.models.enums import PartOfSpeech
```

With:

```python
from syntaxis.models import constants as c
```

Remove the import of `PartOfSpeech` enum entirely.

**Step 2: Remove MORPHEUS_TO_ENUM mapping**

Delete the entire `MORPHEUS_TO_ENUM` dictionary (lines 10-44) and the `normalize_feature()` function (lines 47-58).

**Step 3: Update get_random_word() signature**

Find the `get_random_word()` method and replace:

```python
def get_random_word(
    self, pos: PartOfSpeech, **features: Any
) -> PartOfSpeechBase | None:
```

With:

```python
def get_random_word(self, pos: str, **features: Any) -> PartOfSpeechBase | None:
```

**Step 4: Update get_random_word() docstring**

Replace:

```python
"""Get a random word of the specified part of speech.

Args:
    pos: Part of speech enum (PartOfSpeech.NOUN, PartOfSpeech.VERB, etc.)
    **features: Feature filters as enum values
                (gender=Gender.MASCULINE, case_name=Case.NOMINATIVE, etc.)
```

With:

```python
"""Get a random word of the specified part of speech.

Args:
    pos: Part of speech string (c.NOUN, c.VERB, etc.)
    **features: Feature filters as string constants
                (gender=c.MASCULINE, case=c.NOMINATIVE, etc.)
```

**Step 5: Update add_word() signature**

Find the `add_word()` method and update its signature to use `str` instead of `PartOfSpeech` enum.

**Step 6: Update all references to pos.value**

Search for any `pos.value` or other enum `.value` calls and replace with direct `pos` usage.

**Step 7: Update POS_TO_TABLE_MAP references if needed**

Check `syntaxis/database/bitmasks.py` and update if it references the PartOfSpeech enum.

**Step 8: Verify changes**

Run: `grep -n "enums\." syntaxis/database/manager.py`
Expected: No matches (no more enum usage)

Run: `grep -n "\.value" syntaxis/database/manager.py`
Expected: No matches (no more .value calls)

**Step 9: Commit database updates**

```bash
git add syntaxis/database/manager.py
git commit -m "refactor: update database manager to use string constants

Remove MORPHEUS_TO_ENUM mapping and normalize_feature function.
Update signatures to accept strings instead of enums.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Update Template Models and Parser

**Files:**
- Modify: `syntaxis/templates/models.py`
- Modify: `syntaxis/templates/parser.py`

**Step 1: Update templates/models.py imports**

In `syntaxis/templates/models.py`, replace:

```python
from syntaxis.models.enums import (
    Case,
    Gender,
    Number,
    PartOfSpeech,
    Person,
    Tense,
    Voice,
)
```

With:

```python
from syntaxis.models import constants as c
```

**Step 2: Update TokenFeatures class**

Replace:

```python
@dataclass
class TokenFeatures:
    """Represents the grammatical features required for a token in a template.

    Attributes:
        pos: Part of speech (required for all tokens)
        case: Grammatical case (required for nouns, adjectives, articles)
        gender: Grammatical gender (required for nouns, adjectives, articles)
        number: Grammatical number (required for nouns, adjectives, articles, verbs)
        tense: Verb tense (required for verbs)
        voice: Verb voice (required for verbs)
        person: Grammatical person (required for verbs)
    """

    pos: PartOfSpeech
    case: Case | None = None
    gender: Gender | None = None
    number: Number | None = None
    tense: Tense | None = None
    voice: Voice | None = None
    person: Person | None = None
```

With:

```python
@dataclass
class TokenFeatures:
    """Represents the grammatical features required for a token in a template.

    Attributes:
        pos: Part of speech (required for all tokens)
        case: Grammatical case (required for nouns, adjectives, articles)
        gender: Grammatical gender (required for nouns, adjectives, articles)
        number: Grammatical number (required for nouns, adjectives, articles, verbs)
        tense: Verb tense (required for verbs)
        voice: Verb voice (required for verbs)
        person: Grammatical person (required for verbs)
    """

    pos: str
    case: str | None = None
    gender: str | None = None
    number: str | None = None
    tense: str | None = None
    voice: str | None = None
    person: str | None = None
```

**Step 3: Update is_inflectable() method**

Replace:

```python
def is_inflectable(self) -> bool:
    """Check if this token type requires inflection."""
    return self.pos in {
        PartOfSpeech.NOUN,
        PartOfSpeech.VERB,
        PartOfSpeech.ADJECTIVE,
        PartOfSpeech.ARTICLE,
        PartOfSpeech.PRONOUN,
    }
```

With:

```python
def is_inflectable(self) -> bool:
    """Check if this token type requires inflection."""
    return self.pos in {c.NOUN, c.VERB, c.ADJECTIVE, c.ARTICLE, c.PRONOUN}
```

**Step 4: Update is_invariable() method**

Replace:

```python
def is_invariable(self) -> bool:
    """Check if this token type is invariable (doesn't inflect)."""
    return self.pos in {
        PartOfSpeech.PREPOSITION,
        PartOfSpeech.CONJUNCTION,
        PartOfSpeech.ADVERB,
    }
```

With:

```python
def is_invariable(self) -> bool:
    """Check if this token type is invariable (doesn't inflect)."""
    return self.pos in {c.PREPOSITION, c.CONJUNCTION, c.ADVERB}
```

**Step 5: Update templates/parser.py**

In `syntaxis/templates/parser.py`, update all imports and usages of enums to use string constants from `syntaxis.models.constants`.

Search for patterns like:
- `PartOfSpeech.NOUN` → `c.NOUN`
- `Case.NOMINATIVE` → `c.NOMINATIVE`
- `Gender.MASCULINE` → `c.MASCULINE`
- etc.

**Step 6: Verify changes**

Run: `grep -n "from syntaxis.models.enums" syntaxis/templates/*.py`
Expected: No matches

**Step 7: Commit template updates**

```bash
git add syntaxis/templates/models.py syntaxis/templates/parser.py
git commit -m "refactor: update templates to use string constants

Replace enum types with string constants in TokenFeatures and parser.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Update All Tests

**Files:**
- Modify: `tests/test_morpheus.py`
- Modify: `tests/database/test_manager.py`
- Modify: `tests/templates/test_template_parser.py`

**Step 1: Update tests/test_morpheus.py imports**

Replace:

```python
from syntaxis.models.enums import PartOfSpeech as POSEnum
```

With:

```python
from syntaxis.models import constants as c
```

**Step 2: Update tests/test_morpheus.py test cases**

Replace all `POSEnum.NOUN` with `c.NOUN`, `POSEnum.VERB` with `c.VERB`, etc.

**Step 3: Update tests/database/test_manager.py imports**

Replace enum imports with:

```python
from syntaxis.models import constants as c
```

**Step 4: Update tests/database/test_manager.py test cases**

Replace all enum references like `PartOfSpeech.NOUN` with `c.NOUN`, `Gender.MASCULINE` with `c.MASCULINE`, etc.

**Step 5: Update tests/templates/test_template_parser.py imports**

Replace enum imports with:

```python
from syntaxis.models import constants as c
```

**Step 6: Update tests/templates/test_template_parser.py test cases**

Replace all enum references with string constants. For example:
- `PartOfSpeech.NOUN` → `c.NOUN`
- `Case.NOMINATIVE` → `c.NOMINATIVE`
- `Gender.MASCULINE` → `c.MASCULINE`
- etc.

**Step 7: Run all tests**

Run: `uv run pytest -v`
Expected: All 103 tests should pass

**Step 8: Commit test updates**

```bash
git add tests/
git commit -m "test: update tests to use string constants

Replace all enum usage in tests with string constants.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Delete Old Code

**Files:**
- Delete: `syntaxis/models/enums.py`
- Delete: `syntaxis/morpheus.py`

**Step 1: Verify no remaining references to enums.py**

Run: `grep -r "from syntaxis.models.enums" syntaxis/ tests/`
Expected: No matches

Run: `grep -r "import.*enums" syntaxis/ tests/`
Expected: No matches (except maybe comments)

**Step 2: Delete enums.py**

Run: `git rm syntaxis/models/enums.py`
Expected: File deleted

**Step 3: Delete old morpheus.py**

Run: `git rm syntaxis/morpheus.py`
Expected: File deleted

**Step 4: Verify no broken imports**

Run: `uv run python -c "import syntaxis.models.constants; import syntaxis.morpheus; print('OK')"`
Expected: "OK" printed with no errors

**Step 5: Run all tests again**

Run: `uv run pytest -v`
Expected: All 103 tests pass

**Step 6: Commit deletions**

```bash
git commit -m "refactor: remove old enum-based code

Delete enums.py and old morpheus.py module, replaced by constants
and morpheus package.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Update Documentation

**Files:**
- Modify: Any docs that reference enums or old morpheus API

**Step 1: Search for documentation references**

Run: `grep -r "PartOfSpeech\." docs/ --include="*.md"`
Expected: List of files that reference old enum syntax

Run: `grep -r "morpheus.py" docs/ --include="*.md"`
Expected: List of files that reference old module structure

**Step 2: Update each documentation file**

For each file found:
- Replace enum references with string constant references
- Update morpheus import examples from `from syntaxis.morpheus import Morpheus` to `from syntaxis.morpheus import Morpheus` (same, but note it's now a package)
- Update usage examples to show string constants

**Step 3: Verify documentation accuracy**

Review updated docs to ensure examples are correct and consistent with new API.

**Step 4: Commit documentation updates**

```bash
git add docs/
git commit -m "docs: update documentation for string constants

Update all examples to use string constants instead of enums.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Final Verification

**Step 1: Run full test suite**

Run: `uv run pytest -v --tb=short`
Expected: All 103 tests pass with no errors

**Step 2: Check for any remaining enum references**

Run: `grep -r "\.value" syntaxis/ --include="*.py" | grep -v "__pycache__"`
Expected: No matches (no more enum .value calls)

Run: `grep -r "from syntaxis.models.enums" . --include="*.py" | grep -v "__pycache__"`
Expected: No matches

**Step 3: Verify morpheus works correctly**

Run: `uv run python -c "from syntaxis.morpheus import Morpheus; from syntaxis.models import constants as c; n = Morpheus.create('άνθρωπος', c.NOUN); print(f'Noun created: {n.lemma}'); print('Forms keys:', list(n.forms.keys())[:3])"`
Expected: Output showing noun created with Greek keys from syntaxis constants

**Step 4: Check database bitmasks module**

Run: `grep -n "PartOfSpeech\." syntaxis/database/bitmasks.py`
Expected: Update if any enum references found (may need string constant mapping)

**Step 5: Final commit if any fixes needed**

If step 4 revealed issues:
```bash
git add syntaxis/database/bitmasks.py
git commit -m "fix: update bitmasks to use string constants

Final cleanup of enum references.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Step 6: Verify clean git status**

Run: `git status`
Expected: Clean working directory or only dictionary.csv, main.py changes from initial snapshot

---

## Completion Checklist

- [x] Constants module created and committed
- [x] Morpheus package created with translation layer
- [x] Part of speech models updated to strings
- [x] Database manager updated to strings
- [x] Template models and parser updated to strings
- [ ] All tests updated and passing (103 tests)
- [ ] Old enums.py and morpheus.py deleted
- [ ] Documentation updated
- [ ] No remaining enum references in codebase
- [ ] Full test suite passes

**When all tasks complete, use finishing-a-development-branch skill for merge/PR decision.**
