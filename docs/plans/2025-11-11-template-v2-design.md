# Template V2 Design

**Date:** 2025-11-11
**Status:** Approved

## Overview

This design introduces a V2 template syntax that reduces verbosity by allowing grouping of parts of speech with shared features, reference groups, and selective feature overrides. The V1 syntax remains fully supported through a versioned parser architecture.

## Problem Statement

The current V1 template syntax requires repeating identical features across multiple lexicals:

```
[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:ter:sg]
```

This is verbose and error-prone. Features like `nom:masc:sg` are repeated three times.

## Design Goals

1. **Reduce verbosity** - Group lexicals with shared features
2. **Enable feature reuse** - Reference previously defined feature groups
3. **Maintain clarity** - Syntax should be concise yet readable
4. **Backward compatible** - V1 templates continue to work
5. **Fail fast** - Validation errors caught at parse time
6. **Feature override warnings** - Alert users when direct features override inherited features

## V2 Syntax

### Basic Grouping

Group multiple lexicals with shared features using parentheses:

```
(article adj noun)@{nom:masc:sg}
```

This is equivalent to the V1:
```
[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg]
```

### Multiple Groups

Separate groups with whitespace:

```
(article adj noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}
```

### Auto-Generated Position IDs

Each group is automatically assigned a position ID based on its order:
- First group: `$1`
- Second group: `$2`
- Third group: `$3`
- And so on...

### Group References

Reference a previous group's features using `@$N`:

```
(article noun)@{nom:masc:sg} (pronoun)@$1
```

The second group inherits `nom:masc:sg` from group 1.

**Rules:**
- References can only point to earlier groups (no forward references)
- Referenced group must exist or parse fails

### Direct Feature Overrides

Apply features directly to a specific lexical using `{...}`:

```
(article noun{fem})@{nom:sg}
```

Here `noun` gets `{fem}` directly while inheriting `{nom:sg}` from the group, resulting in `{nom:fem:sg}`.

### Feature Resolution Precedence

For each lexical in a group:

1. **Referenced group features** (if `@$N` present)
2. **Current group features** (from `@{...}`)
3. **Direct lexical features** (from `lexical{...}`)

When a direct feature's category (case/gender/number/person/tense/voice) conflicts with inherited features, the direct feature wins and a warning is emitted.

### Selective Override with Warnings

When a direct feature overrides an inherited feature:

```
(article noun)@{nom:masc:sg} (pronoun{sec})@$1
```

If group 1 had `pri` for person, this would emit:

```
Warning: In group 2, lexical 'pronoun' overrides feature 'person':
  Inherited value: 'pri' (from group 1)
  Override value: 'sec' (direct feature)
```

## Architecture

### Three-Layer Design

```
Template String → Parser Layer → AST Layer → Generator Layer
```

1. **Parser Layer** - Separate parsers for V1 and V2 syntax
2. **AST Layer** - Unified intermediate representation
3. **Generator Layer** - Existing sentence generation (unchanged)

### Version Detection

When `Syntaxis.generate_sentence()` receives a template:
- Starts with `(` → V2Parser
- Starts with `[` → V1Parser
- Otherwise → Error

### AST Structure

```python
@dataclass
class Feature:
    """Represents a grammatical feature (nom, masc, sg, etc.)"""
    name: str
    category: str  # 'case', 'gender', 'number', 'tense', 'voice', 'person'

@dataclass
class POSToken:
    """Individual lexical with optional direct features"""
    lexical: str  # 'noun', 'verb', 'adj', etc.
    direct_features: list[Feature]  # Features applied directly to this lexical

@dataclass
class Group:
    """A group of lexicals with shared features"""
    tokens: list[POSToken]
    group_features: list[Feature]  # Features applied to the whole group
    reference_id: int | None  # Auto-generated position (1, 2, 3...)
    references: int | None  # Points to another group's ID ($1, $2, etc.)

@dataclass
class Template:
    """Top-level AST for a template"""
    groups: list[Group]
    version: int  # 1 or 2
```

### V2 Parser

**Parsing Flow:**

1. **Tokenization** - Split template into groups by matching parentheses
2. **Group Parsing** - For each `(...)@{...}` or `(...)@$N`:
   - Extract lexicals (space-separated)
   - Check for direct features `lexical{...}`
   - Extract group features from `@{...}`
   - Detect references `@$N`
   - Assign position ID
3. **Validation** - After all groups parsed:
   - Verify reference IDs exist and point backward
   - Check feature completeness
   - Ensure required features for each lexical type
4. **AST Construction** - Build Template object

**Error Handling (fail at parse time):**

- Unknown lexical → "Unknown lexical 'xyz' at position N"
- Missing closing parenthesis → "Unclosed group starting at position N"
- Invalid reference → "Reference $5 does not exist (only 3 groups defined)"
- Forward reference → "Reference $3 points forward to group 3 (current group is 2)"
- Incomplete features → "Lexical 'noun' missing required features: needs case, gender, number"

### V1 Parser

Converts each V1 token `[lexical:feat1:feat2:...]` into a single-item group:

- All features go into `group_features`
- No direct features
- No references
- Position IDs assigned for consistency

**Example:**

```
V1: [article:nom:masc:sg] [noun:nom:masc:sg]
```

Becomes AST:
```
Group(tokens=[article], group_features=[nom, masc, sg], reference_id=1)
Group(tokens=[noun], group_features=[nom, masc, sg], reference_id=2)
```

### Feature Resolution Algorithm

For each lexical in a group:

```
1. Start with empty feature set
2. If group has reference ($N):
   - Copy all features from referenced group
3. Merge in current group features:
   - Replace any conflicting categories (no warning)
4. Merge in lexical direct features:
   - For each direct feature:
     * Determine category
     * If category exists, REPLACE and EMIT WARNING
     * Otherwise add feature
5. Validate completeness for lexical type
```

### Feature Category Mapping

- **Case:** `nom`, `gen`, `acc`, `voc`
- **Gender:** `masc`, `fem`, `neut`
- **Number:** `sg`, `pl`
- **Tense:** `pres`, `aorist`, `paratatikos`
- **Voice:** `act`, `pass`
- **Person:** `pri`, `sec`, `ter`

## Examples

### V1 to V2 Conversions

**Example 1 - Basic grouping:**
```
V1: [article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:ter:sg]
V2: (article adj noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}
```

**Example 2 - With references:**
```
V1: [article:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:ter:sg] [article:acc:fem:pl] [noun:acc:fem:pl]
V2: (article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg} (article noun)@{acc:fem:pl}

V2 Alternative with reference:
(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg} (article noun)@$1
Note: This only works if both groups have identical features
```

**Example 3 - Direct feature override:**
```
V1: [pronoun:nom:pri:sg] [verb:pres:act:pri:sg]
V2: (pronoun)@{nom:pri:sg} (verb)@{pres:act:pri:sg}

V2 with reference and override:
(pronoun)@{nom:pri:sg} (verb{pres:act})@$1
# verb inherits {nom:pri:sg} but overrides with {pres:act}, resulting in {nom:pres:act:pri:sg}
```

## Testing Strategy

### Test Coverage

1. **V1 Parser Tests**
   - Existing V1 templates parse correctly
   - V1 validation rules enforced
   - V1 error messages unchanged

2. **V2 Parser Tests**
   - Basic grouping: `(article noun)@{nom:masc:sg}`
   - Multiple groups: `(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}`
   - Direct features: `(article noun{fem})@{nom:sg}`
   - References: `(article noun)@{nom:masc:sg} (pronoun)@$1`
   - Reference with override: `(article noun)@{nom:masc:sg} (pronoun{sec})@$1`
   - Complex templates: `(article adj noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg} (pronoun{pri})@$1`

3. **Error Cases**
   - Invalid reference: `(noun)@$5` when only 2 groups exist
   - Forward reference: `(noun)@$2` in first group
   - Unknown lexical: `(foobar)@{nom:sg}`
   - Missing features: `(noun)@{nom}` (missing gender, number)
   - Unclosed group: `(article noun@{nom:sg}`
   - Invalid syntax mix: `[article)@{nom:sg}`

4. **Warning Tests**
   - Verify warnings emitted for feature overrides
   - Verify warning messages include inherited and override values

5. **Integration Tests**
   - V1 and V2 templates generate equivalent sentences
   - Generated sentences respect all feature constraints

## Implementation Order

1. Define AST node classes (`Feature`, `POSToken`, `Group`, `Template`)
2. Implement V2Parser with full validation
3. Extract existing parsing logic into V1Parser
4. Implement version detection in `Syntaxis` class
5. Adapt generation logic to work from AST
6. Add comprehensive tests
7. Update documentation

## Open Questions

None - design approved.

## Future Enhancements

Potential future improvements (not in scope for V2):

- Named group IDs: `(article noun)@{nom:masc:sg}#subject` instead of positional `$1`
- Partial feature inheritance: `@$1[case,gender]` to inherit only specific features
- Feature variables: `@features:nom_case` to define reusable feature sets
- Conditional groups: Generate different structures based on context
