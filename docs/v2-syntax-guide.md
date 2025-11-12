# Template V2 Syntax Guide

## Overview

Template V2 introduces a more concise syntax for defining Greek sentence templates by allowing you to group lexicals with shared grammatical features.

## Basic Syntax

### V1 (Original)
```
[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg]
```

### V2 (New)
```
(article adj noun)@{nom:masc:sg}
```

## Features

### 1. Grouping

Group multiple lexicals that share the same features:

```
(article adj noun)@{nom:masc:sg}
```

This applies `nom:masc:sg` to all three lexicals.

### 2. Multiple Groups

Separate groups with whitespace:

```
(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}
```

### 3. Group References

Reference features from a previous group using `@$N`:

```
(article noun)@{nom:masc:sg} (pronoun)@$1
```

The second group inherits `nom:masc:sg` from group 1 (`$1`).

**Rules:**
- Can only reference earlier groups (no forward references)
- Groups are numbered 1, 2, 3, etc. automatically

### 4. Direct Feature Overrides

Apply features to individual lexicals using `{...}`:

```
(article noun{fem})@{nom:masc:sg}
```

Here, `noun` gets `fem` directly, overriding the group's `masc`.

**Warning:** When a direct feature conflicts with an inherited feature, a warning is logged.

## Feature Resolution

Features are resolved in this order:
1. Referenced group features (`@$N`)
2. Current group features (`@{...}`)
3. Direct lexical features (`lexical{...}`)

Later features override earlier ones by category (case, gender, number, etc.).

## Examples

### Basic Grouping
```
V1: [article:nom:masc:sg] [noun:nom:masc:sg]
V2: (article noun)@{nom:masc:sg}
```

### With References
```
V2: (article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg} (pronoun)@$1
```

The pronoun inherits `nom:masc:sg` from group 1.

### With Direct Overrides
```
V2: (article noun{fem})@{nom:masc:sg}
```

Article gets `nom:masc:sg`, noun gets `nom:fem:sg`.

## Backward Compatibility

All V1 templates continue to work. The parser automatically detects which version based on the first character:
- `[` = V1 syntax
- `(` = V2 syntax

## Error Messages

Common errors:
- `Unclosed group` - Missing closing parenthesis
- `Unclosed brace` - Missing closing brace
- `Reference $N does not exist` - Referenced group number doesn't exist
- `Reference $N points forward` - Can't reference future groups
- `Unknown feature` - Feature name not recognized
