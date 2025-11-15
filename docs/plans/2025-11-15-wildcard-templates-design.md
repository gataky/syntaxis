# Wildcard Template Feature Design

**Date:** 2025-11-15
**Feature:** Template Wildcards for Gender and Number
**Version:** V2 Templates Only
**Status:** Design Complete

## Overview

Add wildcard functionality to V2 templates that allows random selection of gender and number values during sentence generation. Wildcards use the keywords `gender` and `number` as feature values, which are resolved to random concrete values (`masc`/`fem`/`neut` for gender, `sg`/`pl` for number) at generation time.

## Requirements

### Functional Requirements

1. **Wildcard Syntax**: Use `gender` and `number` as feature keywords in V2 templates
2. **Random Resolution**: Each generation randomly selects concrete values for wildcards
3. **Reference Consistency**: When Group 2 references Group 1, wildcards resolve to the same value across both groups
4. **Retry on No Match**: If a random selection yields no database matches, retry with different random values
5. **UI Support**: Template builder provides wildcard as a dropdown option for gender/number features
6. **Scope**: V2 templates only (V1 not affected)

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Wildcard keywords | `gender` and `number` | Clear, self-documenting; avoids ambiguity of `*` with unordered features |
| Random behavior | Randomly pick from available options | Generates varied sentences for practice/testing |
| Reference behavior | Shared - resolve once and propagate | Maintains grammatical agreement across groups |
| No match handling | Retry with different random value | Maximizes success rate; fails only if no valid combinations exist |
| Template versions | V2 only | V2 is current focus; V1 maintenance mode |
| UI enhancement | Add wildcard dropdown option | Improves discoverability and usability |

## Architecture

### Resolution Cache Approach

Wildcards are resolved during the feature resolution phase using a per-generation cache. The cache ensures:
- Wildcards resolve consistently within a generation
- Referenced groups share the same resolved values
- Independent groups can have different random values

**Cache Key Structure**: `(group_id, category)` tuple
- `group_id`: The group's reference_id (1, 2, 3, ...)
- `category`: The feature category ("gender" or "number")

**Cache Lifecycle**:
1. Created at start of `generate_sentence()`
2. Populated on-demand as wildcards are encountered
3. Entries invalidated on query failure for retry
4. Discarded after generation completes

### Data Flow

```
Template String
    ↓
V2 Parser (wildcards treated as normal features)
    ↓
AST with Feature(name="gender", category=GENDER)
    ↓
Feature Resolution (detect wildcards, consult cache)
    ↓
Wildcard Resolution (random selection, cache result)
    ↓
Database Query (with retry if no match)
    ↓
Generated Sentence
```

## Implementation Details

### 1. Constants (syntaxis/lib/constants.py)

Add wildcard keywords to existing constant sets:

```python
# Wildcard constants
GENDER_WILDCARD = "gender"
NUMBER_WILDCARD = "number"

# Update value sets to include wildcards
GENDER_VALUES = {MASCULINE, FEMININE, NEUTER, GENDER_WILDCARD}
NUMBER_VALUES = {SINGULAR, PLURAL, NUMBER_WILDCARD}

# Map wildcards to their category (for FeatureMapper)
FEATURE_CATEGORIES = {
    # ... existing mappings ...
    GENDER_WILDCARD: GENDER,
    NUMBER_WILDCARD: NUMBER,
}
```

### 2. Wildcard Resolution (syntaxis/lib/syntaxis.py)

**New Method**: `_resolve_wildcard()`

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
        # Shouldn't happen for gender/number wildcards
        return feature

    # Randomly select and cache
    selected = random.choice(possible_values)
    wildcard_cache[cache_key] = selected

    return Feature(name=selected, category=feature.category)
```

**Modified Method**: `_resolve_group_features()`

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

**Modified Method**: `generate_sentence()`

```python
def generate_sentence(self, template: str) -> list[Lexical]:
    """Generate sentence from template with wildcard support.

    Creates wildcard_cache at start of generation and passes to all
    feature resolution calls.
    """
    # ... existing version detection and parsing ...

    # Create wildcard cache for this generation
    wildcard_cache = {}

    # Generate sentence with wildcard support
    sentence = self._generate_from_ast(ast, wildcard_cache)

    return sentence
```

### 3. Database Query Retry (syntaxis/lib/syntaxis.py)

**New Method**: `_get_word_with_wildcard_retry()`

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
            features = self._re_resolve_wildcards(
                original_wildcards, group_id, wildcard_cache, features
            )
```

**Modified Method**: Token generation logic

Track which features were originally wildcards so retry logic knows which to re-roll:

```python
# When generating tokens, track original wildcards
original_wildcards = set()
for feature in resolved_features:
    if is_wildcard_category(feature.category):
        original_wildcards.add(feature.category)

# Pass to query retry logic
word = self._get_word_with_wildcard_retry(
    lexical=token.lexical,
    features=feature_dict,
    original_wildcards=original_wildcards,
    wildcard_cache=wildcard_cache,
    group_id=group.reference_id
)
```

### 4. Parser Changes (syntaxis/lib/templates/v2_parser.py)

**No changes required** to parsing logic. The parser already:
- Uses `FeatureMapper` to map feature strings to categories
- Creates `Feature` objects with name and category
- Validates features against lexical requirements

With updated constants, `FeatureMapper` will automatically recognize:
- `"gender"` → `Feature(name="gender", category=GENDER)`
- `"number"` → `Feature(name="number", category=NUMBER)`

### 5. UI Changes

#### Template Builder Store (client/src/stores/templateBuilder.js)

```javascript
// Add wildcard constants
const GENDER_WILDCARD = 'gender'
const NUMBER_WILDCARD = 'number'

// Update feature value arrays
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

**No other store changes needed**: `loadTemplate()` already parses arbitrary feature strings, so it will correctly load wildcards from saved templates.

#### Template Builder View (client/src/views/TemplateBuilderView.vue)

Update dropdown rendering to show wildcard option with visual indicator:

```vue
<!-- Gender dropdown -->
<select v-model="group.features.gender" class="feature-select">
  <option value="">-- Select Gender --</option>
  <option value="masc">Masculine</option>
  <option value="fem">Feminine</option>
  <option value="neut">Neuter</option>
  <option value="gender">⚡ Wildcard (Random)</option>
</select>

<!-- Number dropdown -->
<select v-model="group.features.number" class="feature-select">
  <option value="">-- Select Number --</option>
  <option value="sg">Singular</option>
  <option value="pl">Plural</option>
  <option value="number">⚡ Wildcard (Random)</option>
</select>
```

**Visual Design**: The ⚡ emoji and "(Random)" label clearly indicate that this option produces different values each generation.

## Examples

### Template Examples

```
# Random gender and number for article+noun
(article noun)@{nom:gender:number}

# Random gender, specific number
(article adj noun)@{nom:gender:sg}

# Wildcard with reference - both groups share same random gender
(article noun)@{nom:gender:sg} (verb)@$1

# Mixed: wildcard in one group, concrete in another
(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:number}

# Override with wildcard: article uses fem, noun uses random gender
(article{fem} noun)@{nom:gender:sg}

# Multiple wildcards with complex references
(article noun)@{nom:gender:number} (verb)@$1 (adj)@$1
# All three groups share the same random gender and number
```

### Generation Examples

Given template: `(article noun)@{nom:gender:sg}`

**Generation 1**: Wildcard resolves to `fem`
- Query: `article` with `{case: nom, gender: fem, number: sg}` → "ἡ"
- Query: `noun` with `{case: nom, gender: fem, number: sg}` → "οἰκία"
- Result: "ἡ οἰκία" (the house - feminine)

**Generation 2**: Wildcard resolves to `masc`
- Query: `article` with `{case: nom, gender: masc, number: sg}` → "ὁ"
- Query: `noun` with `{case: nom, gender: masc, number: sg}` → "ἄνθρωπος"
- Result: "ὁ ἄνθρωπος" (the man - masculine)

**Generation 3**: Wildcard resolves to `neut`
- Query: `article` with `{case: nom, gender: neut, number: sg}` → "τό"
- Query: `noun` with `{case: nom, gender: neut, number: sg}` → "τέκνον"
- Result: "τό τέκνον" (the child - neuter)

### Retry Example

Given template: `(article noun)@{nom:gender:sg}`

**Attempt 1**: Wildcard resolves to `neut`
- Query: `article` with `{case: nom, gender: neut, number: sg}` → Success
- Query: `noun` with `{case: nom, gender: neut, number: sg}` → **NoMatchError** (no neuter nouns in DB)

**Attempt 2**: Wildcard re-resolves to `fem`
- Invalidate cache for `(1, gender)`
- New random selection: `fem`
- Query: `article` with `{case: nom, gender: fem, number: sg}` → Success
- Query: `noun` with `{case: nom, gender: fem, number: sg}` → Success
- Result: "ἡ οἰκία"

## Testing Strategy

### Unit Tests

**Constants** (test_constants.py):
- Verify `GENDER_WILDCARD` and `NUMBER_WILDCARD` are in `GENDER_VALUES` and `NUMBER_VALUES`
- Verify wildcards map to correct categories in `FEATURE_CATEGORIES`

**Wildcard Resolution** (test_syntaxis.py):
- Test `_resolve_wildcard()` returns random values from correct set
- Test cache consistency: same (group_id, category) returns same value
- Test cache independence: different group_ids get independent random values

**Feature Resolution** (test_syntaxis.py):
- Test wildcard features are resolved to concrete values
- Test non-wildcard features pass through unchanged
- Test references share wildcard resolution with referenced group

**Database Retry** (test_syntaxis.py):
- Test retry logic invalidates cache and tries new random values
- Test max attempts limit
- Test failure when no wildcards exist (should not retry)

### Integration Tests

**V2 Template Parsing** (test_v2_parser.py):
- Parse templates with `gender` and `number` keywords
- Verify Feature objects created correctly

**End-to-End Generation** (test_integration.py):
- Generate multiple sentences from same wildcard template, verify different results
- Test wildcard with references, verify agreement
- Test wildcard with overrides
- Test retry behavior with limited database (mock to force retries)

### UI Tests

**Template Builder Store** (templateBuilder.spec.js):
- Test wildcard values in FEATURE_VALUES arrays
- Test template generation with wildcard features
- Test loading templates with wildcards

**Manual UI Testing**:
- Select wildcard from dropdown, verify template string shows "gender" / "number"
- Generate sentence multiple times, verify varied output
- Save and load template with wildcards, verify preservation

## Migration and Compatibility

### Backward Compatibility

**V1 Templates**: Unaffected, continue to work as before

**V2 Templates**: Existing templates without wildcards continue to work identically

**Database**: No schema changes required

**API**: No endpoint changes required

### Forward Compatibility

**Future Extensions**:
- Person wildcards: `person` keyword resolving to `pri`/`sec`/`ter`
- Tense wildcards: `tense` keyword resolving to tense values
- Custom wildcard sets: `gender:masc:fem` (exclude neuter from random pool)

The cache-based architecture supports these extensions by:
- Adding new wildcard constants
- Mapping to appropriate categories
- Adding resolution logic for new categories

## Open Questions

None - design is complete and validated.

## References

- V2 Template Design: `docs/plans/2025-11-11-template-v2-design.md`
- V2 Template Implementation: `docs/plans/2025-11-11-template-v2-implementation.md`
- Template Builder Design: `docs/plans/2025-11-12-v2-template-builder-design.md`
- Feature Constants: `syntaxis/lib/constants.py`
- V2 Parser: `syntaxis/lib/templates/v2_parser.py`
- Generation Logic: `syntaxis/lib/syntaxis.py`
