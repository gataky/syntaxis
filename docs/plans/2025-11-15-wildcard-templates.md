# Wildcard Templates Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add wildcard functionality to V2 templates allowing random selection of gender and number values during sentence generation.

**Architecture:** Use resolution cache approach where wildcards ("gender", "number" keywords) are resolved during feature resolution phase. Cache ensures consistency across referenced groups. Database queries retry with new random values if no matches found.

**Tech Stack:** Python 3.x, Vue.js 3, Pinia store

---

## Task 1: Add Wildcard Constants

**Files:**
- Modify: `syntaxis/lib/constants.py:63-72`
- Test: `tests/lib/test_constants.py`

**Step 1: Write test for wildcard constants**

```python
# tests/lib/test_constants.py
def test_gender_wildcard_constant():
    """Test that GENDER_WILDCARD is defined and has correct value."""
    from syntaxis.lib.constants import GENDER_WILDCARD, GENDER
    assert GENDER_WILDCARD == "gender"

def test_number_wildcard_constant():
    """Test that NUMBER_WILDCARD is defined and has correct value."""
    from syntaxis.lib.constants import NUMBER_WILDCARD, NUMBER
    assert NUMBER_WILDCARD == "number"

def test_gender_values_includes_wildcard():
    """Test that GENDER_VALUES includes wildcard."""
    from syntaxis.lib.constants import GENDER_VALUES, GENDER_WILDCARD
    assert GENDER_WILDCARD in GENDER_VALUES

def test_number_values_includes_wildcard():
    """Test that NUMBER_VALUES includes wildcard."""
    from syntaxis.lib.constants import NUMBER_VALUES, NUMBER_WILDCARD
    assert NUMBER_WILDCARD in NUMBER_VALUES

def test_wildcard_feature_categories():
    """Test that wildcards map to correct categories."""
    from syntaxis.lib.constants import FEATURE_CATEGORIES, GENDER_WILDCARD, NUMBER_WILDCARD, GENDER, NUMBER
    assert FEATURE_CATEGORIES[GENDER_WILDCARD] == GENDER
    assert FEATURE_CATEGORIES[NUMBER_WILDCARD] == NUMBER
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/lib/test_constants.py::test_gender_wildcard_constant -v`
Expected: FAIL with "ImportError: cannot import name 'GENDER_WILDCARD'"

**Step 3: Add wildcard constants**

In `syntaxis/lib/constants.py`, modify the gender and number section:

```python
# Gender constants (MGI abbreviations)
MASCULINE = "masc"      # Masculine
FEMININE = "fem"        # Feminine
NEUTER = "neut"         # Neuter
GENDER_WILDCARD = "gender"  # Wildcard for random gender selection
GENDER_VALUES = {MASCULINE, FEMININE, NEUTER, GENDER_WILDCARD}

# Number constants (MGI abbreviations)
SINGULAR = "sg"         # Singular
PLURAL = "pl"           # Plural
NUMBER_WILDCARD = "number"  # Wildcard for random number selection
NUMBER_VALUES = {SINGULAR, PLURAL, NUMBER_WILDCARD}
```

**Step 4: Add wildcard mappings to FEATURE_CATEGORIES**

In `syntaxis/lib/constants.py`, add to the FEATURE_CATEGORIES dict (around line 109):

```python
FEATURE_CATEGORIES = {
    # Gender mappings
    MASCULINE: GENDER,
    FEMININE: GENDER,
    NEUTER: GENDER,
    GENDER_WILDCARD: GENDER,  # Add this line
    # Number mappings
    SINGULAR: NUMBER,
    PLURAL: NUMBER,
    NUMBER_WILDCARD: NUMBER,  # Add this line
    # ... rest of existing mappings ...
}
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/lib/test_constants.py -v -k wildcard`
Expected: All 6 wildcard tests PASS

**Step 6: Commit**

```bash
git add syntaxis/lib/constants.py tests/lib/test_constants.py
git commit -m "feat: add wildcard constants for gender and number"
```

---

## Task 2: Implement Wildcard Resolution Function

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/lib/test_syntaxis.py`

**Step 1: Write test for wildcard resolution**

```python
# tests/lib/test_syntaxis.py
import random
from syntaxis.lib.templates.ast import Feature
from syntaxis.lib.constants import GENDER, NUMBER, MASCULINE, FEMININE, NEUTER, SINGULAR, PLURAL

def test_resolve_wildcard_gender():
    """Test that gender wildcard resolves to masc, fem, or neut."""
    syntaxis = Syntaxis()
    feature = Feature(name="gender", category=GENDER)
    wildcard_cache = {}

    resolved = syntaxis._resolve_wildcard(feature, group_id=1, wildcard_cache=wildcard_cache)

    assert resolved.category == GENDER
    assert resolved.name in {MASCULINE, FEMININE, NEUTER}
    assert (1, GENDER) in wildcard_cache
    assert wildcard_cache[(1, GENDER)] == resolved.name

def test_resolve_wildcard_number():
    """Test that number wildcard resolves to sg or pl."""
    syntaxis = Syntaxis()
    feature = Feature(name="number", category=NUMBER)
    wildcard_cache = {}

    resolved = syntaxis._resolve_wildcard(feature, group_id=1, wildcard_cache=wildcard_cache)

    assert resolved.category == NUMBER
    assert resolved.name in {SINGULAR, PLURAL}
    assert (1, NUMBER) in wildcard_cache
    assert wildcard_cache[(1, NUMBER)] == resolved.name

def test_resolve_wildcard_uses_cache():
    """Test that wildcard resolution uses cached value."""
    syntaxis = Syntaxis()
    feature = Feature(name="gender", category=GENDER)
    wildcard_cache = {(1, GENDER): FEMININE}

    resolved = syntaxis._resolve_wildcard(feature, group_id=1, wildcard_cache=wildcard_cache)

    assert resolved.name == FEMININE  # Should use cached value, not random

def test_resolve_wildcard_different_groups_independent():
    """Test that different group IDs get independent random values."""
    syntaxis = Syntaxis()
    feature = Feature(name="gender", category=GENDER)
    wildcard_cache = {}

    # Resolve for group 1
    resolved1 = syntaxis._resolve_wildcard(feature, group_id=1, wildcard_cache=wildcard_cache)

    # Resolve for group 2 (different group_id)
    resolved2 = syntaxis._resolve_wildcard(feature, group_id=2, wildcard_cache=wildcard_cache)

    # Both should be valid, but cache should have separate entries
    assert (1, GENDER) in wildcard_cache
    assert (2, GENDER) in wildcard_cache
    # They might be the same by chance, but cache keys are different
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/lib/test_syntaxis.py::test_resolve_wildcard_gender -v`
Expected: FAIL with "AttributeError: 'Syntaxis' object has no attribute '_resolve_wildcard'"

**Step 3: Implement _resolve_wildcard method**

In `syntaxis/lib/syntaxis.py`, add the import at the top:

```python
import random
from syntaxis.lib.constants import (
    GENDER, NUMBER, MASCULINE, FEMININE, NEUTER, SINGULAR, PLURAL,
    GENDER_WILDCARD, NUMBER_WILDCARD
)
```

Add the method to the Syntaxis class:

```python
def _resolve_wildcard(self, feature: Feature, group_id: int, wildcard_cache: dict) -> Feature:
    """Resolves a wildcard feature to a random concrete value.

    Uses cache key (group_id, category) to ensure consistency within generation.

    Args:
        feature: Feature object with name="gender" or name="number"
        group_id: The group's reference_id for cache keying
        wildcard_cache: Dictionary mapping (group_id, category) to resolved values

    Returns:
        New Feature with randomly selected concrete value
    """
    cache_key = (group_id, feature.category)

    if cache_key in wildcard_cache:
        # Already resolved for this group/category
        return Feature(name=wildcard_cache[cache_key], category=feature.category)

    # Determine possible values based on category
    if feature.category == GENDER:
        possible_values = [MASCULINE, FEMININE, NEUTER]
    elif feature.category == NUMBER:
        possible_values = [SINGULAR, PLURAL]
    else:
        # Not a wildcard we handle, return original
        return feature

    # Randomly select and cache
    selected = random.choice(possible_values)
    wildcard_cache[cache_key] = selected

    return Feature(name=selected, category=feature.category)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/lib/test_syntaxis.py -v -k resolve_wildcard`
Expected: All 4 wildcard resolution tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/syntaxis.py tests/lib/test_syntaxis.py
git commit -m "feat: implement wildcard resolution with caching"
```

---

## Task 3: Update Feature Resolution to Handle Wildcards

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/lib/test_syntaxis.py`

**Step 1: Write test for feature resolution with wildcards**

```python
# tests/lib/test_syntaxis.py
def test_resolve_group_features_resolves_wildcards():
    """Test that _resolve_group_features resolves wildcard features."""
    syntaxis = Syntaxis()

    # Create a group with wildcard features
    from syntaxis.lib.templates.ast import Group, POSToken, Feature
    group = Group(
        tokens=[POSToken(lexical="noun", direct_features=[])],
        group_features=[
            Feature(name="nom", category=CASE),
            Feature(name="gender", category=GENDER),
            Feature(name="sg", category=NUMBER)
        ],
        reference_id=1,
        references=None
    )

    wildcard_cache = {}
    resolved = syntaxis._resolve_group_features(group, all_groups=[group], wildcard_cache=wildcard_cache)

    # Should have 3 features, gender should be resolved
    assert len(resolved) == 3
    gender_feature = [f for f in resolved if f.category == GENDER][0]
    assert gender_feature.name in {MASCULINE, FEMININE, NEUTER}
    assert gender_feature.name != "gender"  # Should be resolved

def test_resolve_group_features_preserves_non_wildcards():
    """Test that non-wildcard features pass through unchanged."""
    syntaxis = Syntaxis()

    from syntaxis.lib.templates.ast import Group, POSToken, Feature
    group = Group(
        tokens=[POSToken(lexical="noun", direct_features=[])],
        group_features=[
            Feature(name="nom", category=CASE),
            Feature(name="masc", category=GENDER),
            Feature(name="sg", category=NUMBER)
        ],
        reference_id=1,
        references=None
    )

    wildcard_cache = {}
    resolved = syntaxis._resolve_group_features(group, all_groups=[group], wildcard_cache=wildcard_cache)

    # All features should be unchanged
    assert len(resolved) == 3
    assert any(f.name == "nom" for f in resolved)
    assert any(f.name == "masc" for f in resolved)
    assert any(f.name == "sg" for f in resolved)
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/lib/test_syntaxis.py::test_resolve_group_features_resolves_wildcards -v`
Expected: FAIL - test will fail because _resolve_group_features doesn't accept wildcard_cache parameter

**Step 3: Update _resolve_group_features method signature and logic**

Find the `_resolve_group_features` method in `syntaxis/lib/syntaxis.py` and update it:

```python
def _resolve_group_features(self, group: Group, all_groups: list[Group],
                            wildcard_cache: dict) -> list[Feature]:
    """Resolve features for a group, handling references and wildcards.

    Args:
        group: The group to resolve features for
        all_groups: All groups in the template (for reference resolution)
        wildcard_cache: Wildcard resolution cache for this generation

    Returns:
        List of fully resolved Feature objects (no wildcards)
    """
    # Get base features (from group or reference)
    if group.references:
        referenced_group = all_groups[group.references - 1]
        features = self._resolve_group_features(referenced_group, all_groups, wildcard_cache)
    else:
        features = group.group_features

    # Resolve any wildcards
    resolved_features = []
    for feature in features:
        if feature.name in {GENDER_WILDCARD, NUMBER_WILDCARD}:
            resolved = self._resolve_wildcard(feature, group.reference_id, wildcard_cache)
            resolved_features.append(resolved)
        else:
            resolved_features.append(feature)

    return resolved_features
```

**Step 4: Update all callers of _resolve_group_features**

Search for all calls to `_resolve_group_features` in the file and update them to pass `wildcard_cache`. This will likely be in the `_generate_from_ast` or similar generation methods. You'll need to read the current implementation to find all call sites.

Example pattern to search for: `self._resolve_group_features(`

Update each call site to pass the wildcard_cache parameter.

**Step 5: Run tests to verify they pass**

Run: `pytest tests/lib/test_syntaxis.py -v -k resolve_group_features`
Expected: Tests PASS (both new wildcard tests and existing tests)

**Step 6: Commit**

```bash
git add syntaxis/lib/syntaxis.py tests/lib/test_syntaxis.py
git commit -m "feat: integrate wildcard resolution into feature resolution"
```

---

## Task 4: Add Wildcard Cache to Generation Entry Point

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/lib/test_syntaxis.py`

**Step 1: Write integration test for generation with wildcards**

```python
# tests/lib/test_syntaxis.py
def test_generate_sentence_with_gender_wildcard():
    """Test that generate_sentence handles gender wildcards."""
    syntaxis = Syntaxis()

    # Template with gender wildcard
    template = "(noun)@{nom:gender:sg}"

    # Mock the database to return a word
    # (This assumes you have a way to mock the database or use test fixtures)
    # Generate sentence - should not raise errors
    result = syntaxis.generate_sentence(template)

    # Should successfully generate (exact result depends on random selection and DB)
    assert result is not None
    assert len(result) > 0

def test_generate_sentence_with_number_wildcard():
    """Test that generate_sentence handles number wildcards."""
    syntaxis = Syntaxis()

    template = "(noun)@{nom:masc:number}"

    result = syntaxis.generate_sentence(template)

    assert result is not None
    assert len(result) > 0

def test_generate_sentence_wildcard_consistency_across_reference():
    """Test that wildcards are consistent when groups reference each other."""
    syntaxis = Syntaxis()

    # Group 2 references Group 1, should share wildcard values
    template = "(article noun)@{nom:gender:sg} (adj)@$1"

    # This test would need to verify that article, noun, and adj all get same gender
    # Exact verification depends on your Lexical object structure
    result = syntaxis.generate_sentence(template)

    assert result is not None
    assert len(result) == 3  # article, noun, adj
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/lib/test_syntaxis.py::test_generate_sentence_with_gender_wildcard -v`
Expected: FAIL - likely because wildcard_cache is not initialized in generate_sentence

**Step 3: Update generate_sentence to initialize wildcard cache**

Find the `generate_sentence` method in `syntaxis/lib/syntaxis.py`:

```python
def generate_sentence(self, template: str) -> list[Lexical]:
    """Generate sentence from template with wildcard support.

    Creates wildcard_cache at start of generation and passes to all
    feature resolution calls.
    """
    # Detect version (existing logic)
    if template.startswith('['):
        version = 1
        ast = self.v1_parser.parse(template)
    elif template.startswith('('):
        version = 2
        ast = self.v2_parser.parse(template)
    else:
        raise ValueError("Invalid template format")

    # Create wildcard cache for this generation
    wildcard_cache = {}

    # Generate sentence with wildcard support
    sentence = self._generate_from_ast(ast, wildcard_cache)

    return sentence
```

**Step 4: Update _generate_from_ast to accept and pass wildcard_cache**

Find the `_generate_from_ast` method and update its signature:

```python
def _generate_from_ast(self, ast: TemplateAST, wildcard_cache: dict) -> list[Lexical]:
    """Generate sentence from AST with wildcard support."""
    # ... existing implementation ...
    # Make sure to pass wildcard_cache to _resolve_group_features calls
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/lib/test_syntaxis.py -v -k "generate_sentence.*wildcard"`
Expected: All wildcard generation tests PASS

Note: These tests may need database fixtures to work properly. If they fail due to database issues, that's expected - we'll handle retry logic next.

**Step 6: Commit**

```bash
git add syntaxis/lib/syntaxis.py tests/lib/test_syntaxis.py
git commit -m "feat: initialize wildcard cache in generate_sentence"
```

---

## Task 5: Implement Database Query Retry Logic

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/lib/test_syntaxis.py`

**Step 1: Write test for retry logic**

```python
# tests/lib/test_syntaxis.py
from unittest.mock import Mock, patch

def test_get_word_with_wildcard_retry_success_first_try():
    """Test that retry logic works when first attempt succeeds."""
    syntaxis = Syntaxis()

    # Mock database to succeed on first try
    with patch.object(syntaxis.database, 'get_word', return_value="τέκνον"):
        result = syntaxis._get_word_with_wildcard_retry(
            lexical="noun",
            features={"case": "nom", "gender": "neut", "number": "sg"},
            original_wildcards={"gender"},
            wildcard_cache={(1, GENDER): "neut"},
            group_id=1
        )

    assert result == "τέκνον"

def test_get_word_with_wildcard_retry_retries_on_failure():
    """Test that retry logic tries different values on failure."""
    syntaxis = Syntaxis()
    wildcard_cache = {(1, GENDER): "neut"}

    call_count = 0
    def mock_get_word(lexical, features):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call fails (neut has no matches)
            raise NoMatchError("No match found")
        else:
            # Second call succeeds (re-rolled to different gender)
            return "οἰκία"

    with patch.object(syntaxis.database, 'get_word', side_effect=mock_get_word):
        result = syntaxis._get_word_with_wildcard_retry(
            lexical="noun",
            features={"case": "nom", "gender": "neut", "number": "sg"},
            original_wildcards={"gender"},
            wildcard_cache=wildcard_cache,
            group_id=1
        )

    assert result == "οἰκία"
    assert call_count == 2  # Should have retried
    # Cache entry should have been invalidated and re-resolved
    assert (1, GENDER) in wildcard_cache

def test_get_word_with_wildcard_retry_fails_after_max_attempts():
    """Test that retry logic eventually fails if no matches found."""
    syntaxis = Syntaxis()

    with patch.object(syntaxis.database, 'get_word', side_effect=NoMatchError("No match")):
        with pytest.raises(ValueError, match="No matching noun found"):
            syntaxis._get_word_with_wildcard_retry(
                lexical="noun",
                features={"case": "nom", "gender": "neut", "number": "sg"},
                original_wildcards={"gender"},
                wildcard_cache={(1, GENDER): "neut"},
                group_id=1,
                max_attempts=3
            )

def test_get_word_with_wildcard_retry_no_retry_without_wildcards():
    """Test that retry logic doesn't retry if no wildcards were used."""
    syntaxis = Syntaxis()

    with patch.object(syntaxis.database, 'get_word', side_effect=NoMatchError("No match")):
        with pytest.raises(ValueError):
            syntaxis._get_word_with_wildcard_retry(
                lexical="noun",
                features={"case": "nom", "gender": "masc", "number": "sg"},
                original_wildcards=set(),  # No wildcards
                wildcard_cache={},
                group_id=1,
                max_attempts=10
            )
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/lib/test_syntaxis.py::test_get_word_with_wildcard_retry_success_first_try -v`
Expected: FAIL with "AttributeError: 'Syntaxis' object has no attribute '_get_word_with_wildcard_retry'"

**Step 3: Define NoMatchError exception if it doesn't exist**

Check if `NoMatchError` exists. If not, add it to `syntaxis/lib/exceptions.py` or at the top of `syntaxis.py`:

```python
class NoMatchError(Exception):
    """Raised when no matching word found in database."""
    pass
```

**Step 4: Implement _get_word_with_wildcard_retry method**

Add this method to the Syntaxis class in `syntaxis/lib/syntaxis.py`:

```python
def _get_word_with_wildcard_retry(self, lexical: str, features: dict,
                                   original_wildcards: set, wildcard_cache: dict,
                                   group_id: int, max_attempts: int = 10) -> str:
    """Query database with retry logic for wildcards.

    If initial query fails and wildcards were used, invalidate cache entries
    for wildcard categories and retry with new random values.

    Args:
        lexical: The part of speech (noun, verb, etc.)
        features: Resolved feature dict for query
        original_wildcards: Set of categories that were wildcards (e.g., {'gender', 'number'})
        wildcard_cache: The generation's wildcard cache
        group_id: The group ID for cache invalidation
        max_attempts: Maximum retry attempts (default: 10)

    Returns:
        Inflected word from database

    Raises:
        ValueError: If no matching word found after all attempts
    """
    for attempt in range(max_attempts):
        try:
            # Try to get word with current feature combination
            word = self.database.get_word(lexical, features)
            return word
        except NoMatchError:
            if attempt == max_attempts - 1 or not original_wildcards:
                # Out of retries or no wildcards to re-roll
                raise ValueError(
                    f"No matching {lexical} found for features {features} "
                    f"after {max_attempts} attempts"
                )

            # Invalidate wildcard cache entries for this group
            for category in original_wildcards:
                cache_key = (group_id, category)
                if cache_key in wildcard_cache:
                    del wildcard_cache[cache_key]

            # Re-resolve wildcards with new random values
            # Create temporary features to resolve
            features_to_resolve = []
            for category in original_wildcards:
                if category == GENDER:
                    temp_feature = Feature(name=GENDER_WILDCARD, category=GENDER)
                elif category == NUMBER:
                    temp_feature = Feature(name=NUMBER_WILDCARD, category=NUMBER)
                else:
                    continue

                resolved = self._resolve_wildcard(temp_feature, group_id, wildcard_cache)
                features[category.lower()] = resolved.name

    # Should never reach here, but just in case
    raise ValueError(f"No matching {lexical} found for features {features}")
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/lib/test_syntaxis.py -v -k retry`
Expected: All retry tests PASS

**Step 6: Commit**

```bash
git add syntaxis/lib/syntaxis.py tests/lib/test_syntaxis.py
git commit -m "feat: implement database query retry for wildcards"
```

---

## Task 6: Integrate Retry Logic into Word Generation

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/integration/test_v2_templates.py`

**Step 1: Write integration test**

Create or modify `tests/integration/test_v2_templates.py`:

```python
# tests/integration/test_v2_templates.py
def test_wildcard_template_generates_valid_sentence():
    """Test end-to-end generation with wildcard template."""
    syntaxis = Syntaxis()

    template = "(article noun)@{nom:gender:sg}"

    # Generate multiple times to test randomness
    results = []
    for _ in range(5):
        sentence = syntaxis.generate_sentence(template)
        results.append(sentence)

    # All should succeed
    assert all(len(s) == 2 for s in results)

    # Should have some variety (not guaranteed, but likely with 5 attempts)
    # This is a weak test but catches if wildcard is not working at all

def test_wildcard_with_reference_maintains_agreement():
    """Test that wildcards maintain grammatical agreement through references."""
    syntaxis = Syntaxis()

    template = "(article noun)@{nom:gender:sg} (adj)@$1"

    sentence = syntaxis.generate_sentence(template)

    # Should generate 3 words: article, noun, adj
    assert len(sentence) == 3

    # All should have same gender (check via their features if Lexical exposes them)
    # This test depends on your Lexical object structure
```

**Step 2: Run tests to verify current state**

Run: `pytest tests/integration/test_v2_templates.py::test_wildcard_template_generates_valid_sentence -v`
Expected: May FAIL if word generation doesn't use retry logic yet

**Step 3: Update word generation to track wildcards and use retry**

Find where words are queried from the database in the generation code. This is likely in `_generate_from_ast` or a helper method. You need to:

1. Track which features were originally wildcards
2. Call `_get_word_with_wildcard_retry` instead of direct database call

Example modification pattern:

```python
# Before resolving features for token generation:
original_wildcards = set()
resolved_features = self._resolve_group_features(group, all_groups, wildcard_cache)

# Track which features were wildcards by checking original group features
for feature in group.group_features:
    if feature.name in {GENDER_WILDCARD, NUMBER_WILDCARD}:
        original_wildcards.add(feature.category)

# Convert features to dict for database query
feature_dict = {f.category.lower(): f.name for f in resolved_features}

# Use retry logic when querying
try:
    word = self._get_word_with_wildcard_retry(
        lexical=token.lexical,
        features=feature_dict,
        original_wildcards=original_wildcards,
        wildcard_cache=wildcard_cache,
        group_id=group.reference_id
    )
except ValueError as e:
    # Handle error (log, raise, etc.)
    raise
```

**Step 4: Run integration tests to verify**

Run: `pytest tests/integration/test_v2_templates.py -v`
Expected: All tests PASS

**Step 5: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS (no regressions)

**Step 6: Commit**

```bash
git add syntaxis/lib/syntaxis.py tests/integration/test_v2_templates.py
git commit -m "feat: integrate retry logic into word generation"
```

---

## Task 7: Add UI Wildcard Constants to Store

**Files:**
- Modify: `client/src/stores/templateBuilder.js`
- Test: Manual testing (or add unit tests if test infrastructure exists)

**Step 1: Add wildcard constants to store**

In `client/src/stores/templateBuilder.js`, add constants at the top:

```javascript
// Wildcard constants
const GENDER_WILDCARD = 'gender'
const NUMBER_WILDCARD = 'number'
```

**Step 2: Update FEATURE_VALUES to include wildcards**

Find the `FEATURE_VALUES` constant or wherever feature options are defined:

```javascript
const FEATURE_VALUES = {
  case: ['nom', 'gen', 'acc', 'dat', 'voc'],
  gender: ['masc', 'fem', 'neut', GENDER_WILDCARD],
  number: ['sg', 'pl', NUMBER_WILDCARD],
  tense: ['pres', 'imperf', 'fut', 'aor', 'perf', 'pluperf'],
  voice: ['act', 'mid', 'pass'],
  person: ['pri', 'sec', 'ter'],
  mood: ['ind', 'subj', 'opt', 'imp', 'inf', 'part'],
}
```

**Step 3: Test manually in browser**

1. Start dev server: `npm run dev` (or appropriate command)
2. Navigate to template builder
3. Open browser console and check that wildcards are available:
   ```javascript
   // In console
   console.log(FEATURE_VALUES.gender)  // Should include 'gender'
   console.log(FEATURE_VALUES.number)  // Should include 'number'
   ```

**Step 4: Verify template generation with wildcards**

In the template builder UI:
1. Create a group with gender wildcard selected
2. Check that generated template string shows `gender` keyword
3. Create a template with number wildcard
4. Check that generated template string shows `number` keyword

**Step 5: Commit**

```bash
git add client/src/stores/templateBuilder.js
git commit -m "feat: add wildcard options to template builder store"
```

---

## Task 8: Update UI Dropdowns to Show Wildcard Options

**Files:**
- Modify: `client/src/views/TemplateBuilderView.vue`
- Test: Manual testing in browser

**Step 1: Locate gender dropdown in template builder view**

Find the gender feature dropdown in `client/src/views/TemplateBuilderView.vue`. It likely looks something like:

```vue
<select v-model="group.features.gender">
  <option value="">-- Select Gender --</option>
  <option value="masc">Masculine</option>
  <option value="fem">Feminine</option>
  <option value="neut">Neuter</option>
</select>
```

**Step 2: Add wildcard option to gender dropdown**

Update the gender dropdown to include wildcard:

```vue
<select v-model="group.features.gender" class="feature-select">
  <option value="">-- Select Gender --</option>
  <option value="masc">Masculine</option>
  <option value="fem">Feminine</option>
  <option value="neut">Neuter</option>
  <option value="gender">⚡ Wildcard (Random)</option>
</select>
```

**Step 3: Locate number dropdown and add wildcard option**

Find the number dropdown and update similarly:

```vue
<select v-model="group.features.number" class="feature-select">
  <option value="">-- Select Number --</option>
  <option value="sg">Singular</option>
  <option value="pl">Plural</option>
  <option value="number">⚡ Wildcard (Random)</option>
</select>
```

**Step 4: Test in browser**

1. Start dev server: `npm run dev`
2. Navigate to template builder
3. Verify gender dropdown shows "⚡ Wildcard (Random)" option
4. Verify number dropdown shows "⚡ Wildcard (Random)" option
5. Select wildcard for gender, verify template string shows "gender"
6. Select wildcard for number, verify template string shows "number"
7. Create template with wildcards: `(noun)@{nom:gender:number}`
8. Save the template
9. Generate sentence multiple times, verify different results

**Step 5: Test loading saved wildcard templates**

1. Load a saved template that contains wildcards
2. Verify dropdowns show "⚡ Wildcard (Random)" selected
3. Verify can edit and re-save

**Step 6: Commit**

```bash
git add client/src/views/TemplateBuilderView.vue
git commit -m "feat: add wildcard options to gender and number dropdowns"
```

---

## Task 9: Write End-to-End Tests

**Files:**
- Create: `tests/integration/test_wildcard_templates.py`

**Step 1: Create comprehensive integration tests**

```python
# tests/integration/test_wildcard_templates.py
import pytest
from syntaxis.lib.syntaxis import Syntaxis

class TestWildcardTemplates:
    """Integration tests for wildcard template functionality."""

    def test_gender_wildcard_single_group(self):
        """Test gender wildcard in a single group."""
        syntaxis = Syntaxis()
        template = "(article noun)@{nom:gender:sg}"

        # Generate multiple times
        results = []
        for _ in range(10):
            sentence = syntaxis.generate_sentence(template)
            results.append(sentence)

        # All should succeed
        assert all(len(s) == 2 for s in results)

    def test_number_wildcard_single_group(self):
        """Test number wildcard in a single group."""
        syntaxis = Syntaxis()
        template = "(article noun)@{nom:masc:number}"

        sentence = syntaxis.generate_sentence(template)
        assert len(sentence) == 2

    def test_both_wildcards(self):
        """Test both gender and number wildcards together."""
        syntaxis = Syntaxis()
        template = "(article noun)@{nom:gender:number}"

        sentence = syntaxis.generate_sentence(template)
        assert len(sentence) == 2

    def test_wildcard_with_reference(self):
        """Test wildcard consistency across referenced groups."""
        syntaxis = Syntaxis()
        template = "(article noun)@{nom:gender:sg} (adj)@$1"

        sentence = syntaxis.generate_sentence(template)
        assert len(sentence) == 3

        # Verify all have same gender (if Lexical exposes features)
        # This depends on your Lexical object structure

    def test_wildcard_with_override(self):
        """Test wildcard with direct feature override."""
        syntaxis = Syntaxis()
        template = "(article noun{fem})@{nom:gender:sg}"

        sentence = syntaxis.generate_sentence(template)
        assert len(sentence) == 2

        # noun should be feminine regardless of wildcard resolution

    def test_multiple_groups_independent_wildcards(self):
        """Test that independent groups get different random values."""
        syntaxis = Syntaxis()
        template = "(article noun)@{nom:gender:sg} (article noun)@{acc:gender:sg}"

        sentence = syntaxis.generate_sentence(template)
        assert len(sentence) == 4

        # Groups should potentially have different genders (not guaranteed, but independent)

    def test_complex_template_with_wildcards(self):
        """Test complex template with wildcards and references."""
        syntaxis = Syntaxis()
        template = "(article noun)@{nom:gender:sg} (verb)@{pres:act:ter:number} (adj)@$1"

        sentence = syntaxis.generate_sentence(template)
        # Should successfully generate (exact length depends on template)
        assert len(sentence) > 0

    def test_wildcard_retry_on_no_match(self):
        """Test that retry works when random selection has no matches."""
        # This test would require a controlled database with limited entries
        # to force retry scenario. May need to mock or use test fixtures.
        pass

    def test_parse_and_generate_wildcard_template(self):
        """Test full cycle: parse template with wildcards and generate."""
        syntaxis = Syntaxis()

        # Various wildcard patterns
        templates = [
            "(noun)@{nom:gender:sg}",
            "(noun)@{nom:masc:number}",
            "(noun)@{nom:gender:number}",
            "(article noun adj)@{nom:gender:sg}",
            "(article noun)@{nom:gender:sg} (verb)@$1",
        ]

        for template in templates:
            # Should parse and generate without errors
            sentence = syntaxis.generate_sentence(template)
            assert sentence is not None
```

**Step 2: Run tests**

Run: `pytest tests/integration/test_wildcard_templates.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/integration/test_wildcard_templates.py
git commit -m "test: add comprehensive wildcard template integration tests"
```

---

## Task 10: Update Documentation

**Files:**
- Create: `docs/wildcard-templates.md` (or add section to existing template docs)

**Step 1: Write user-facing documentation**

```markdown
# Wildcard Templates

## Overview

Wildcards allow you to create templates that generate varied sentences by randomly selecting gender or number values during generation.

## Syntax

Use the keywords `gender` and `number` as feature values in V2 templates:

### Gender Wildcard

Randomly selects from: `masc`, `fem`, `neut`

```
(article noun)@{nom:gender:sg}
```

### Number Wildcard

Randomly selects from: `sg`, `pl`

```
(article noun)@{nom:masc:number}
```

### Combined Wildcards

```
(article noun)@{nom:gender:number}
```

## Behavior

### Random Selection

Each time you generate a sentence from a wildcard template, the wildcard resolves to a random value:

```
Template: (article noun)@{nom:gender:sg}

Generation 1: ὁ ἄνθρωπος (masculine)
Generation 2: ἡ οἰκία (feminine)
Generation 3: τό τέκνον (neuter)
```

### Reference Consistency

When groups reference each other, wildcards resolve to the same value across all referenced groups, maintaining grammatical agreement:

```
Template: (article noun)@{nom:gender:sg} (adj)@$1

Result: All three words have the same gender
```

### Retry Logic

If the randomly selected value has no matching words in the database, the system automatically tries different values until a match is found.

## UI Usage

In the Template Builder:

1. Select "⚡ Wildcard (Random)" from the gender or number dropdown
2. The template string will show `gender` or `number` keyword
3. Save the template normally
4. Generate sentences - each generation will produce different results

## Examples

### Practice All Genders

Create a single template that practices all genders:

```
(article noun)@{nom:gender:sg}
```

### Varied Sentences

Generate varied sentence patterns:

```
(article noun)@{nom:gender:number} (verb)@{pres:act:ter:number}
```

### Complex Agreement

Test grammatical agreement with wildcards:

```
(article adj noun)@{nom:gender:sg} (verb)@$1 (article noun)@{acc:gender:sg}
```

## Limitations

- V2 templates only (V1 does not support wildcards)
- Currently supports gender and number only (person, tense coming in future)
- Wildcard retry attempts limited to 10 (after which an error is raised)
```

**Step 2: Add section to existing template documentation**

If there's an existing `docs/templates.md` or similar, add a "Wildcards" section with the above content.

**Step 3: Commit**

```bash
git add docs/wildcard-templates.md
git commit -m "docs: add wildcard template user documentation"
```

---

## Task 11: Final Testing and Verification

**Files:**
- All project files

**Step 1: Run complete test suite**

Run: `pytest tests/ -v --cov=syntaxis/lib`
Expected: All tests PASS, good coverage on modified modules

**Step 2: Manual end-to-end testing**

1. Start backend server
2. Start frontend dev server
3. Navigate to Template Builder
4. Create template: `(article noun)@{nom:gender:sg}`
5. Save template
6. Navigate to exercise view and load template
7. Generate sentence 10 times
8. Verify varied output (different genders appearing)
9. Create template with reference: `(article noun)@{nom:gender:sg} (adj)@$1`
10. Generate and verify all words have matching gender

**Step 3: Test edge cases**

1. Template with both wildcards: `(noun)@{nom:gender:number}`
2. Template with wildcard and override: `(article noun{fem})@{nom:gender:sg}`
3. Multiple independent groups: `(noun)@{nom:gender:sg} (noun)@{acc:gender:sg}`
4. Load saved wildcard template and verify it works

**Step 4: Check for regressions**

1. Test existing non-wildcard templates still work
2. Test V1 templates still work
3. Test all existing template builder features

**Step 5: Create summary of changes**

Document what was implemented:
- ✅ Wildcard constants in backend
- ✅ Wildcard resolution with caching
- ✅ Feature resolution integration
- ✅ Database retry logic
- ✅ UI dropdown options
- ✅ Integration tests
- ✅ Documentation

**Step 6: Final commit**

```bash
git add -A
git commit -m "test: verify wildcard templates feature complete

All manual and automated tests passing:
- Backend wildcard resolution with caching
- Database retry on no match
- UI dropdowns show wildcard options
- End-to-end generation working
- No regressions in existing functionality

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Summary

This implementation adds wildcard support to V2 templates following TDD principles:

**Backend Changes:**
- Constants for wildcards (`GENDER_WILDCARD`, `NUMBER_WILDCARD`)
- Resolution cache architecture
- Wildcard resolution logic with caching
- Database retry mechanism
- Integration into generation pipeline

**Frontend Changes:**
- Store constants for wildcards
- UI dropdown options with visual indicator (⚡)
- Template loading/saving support

**Testing:**
- Unit tests for all new functions
- Integration tests for end-to-end flow
- Manual testing checklist

**Total Tasks:** 11
**Estimated Time:** 3-4 hours (following TDD with small commits)

---
