# Creating Sentence Templates

The core of the `syntaxis` library is its ability to generate random sentences based on a template you provide. This guide explains how to create these templates.

## The `Syntaxis` Class

The main entry point for using the library is the `Syntaxis` class. You can use it to generate sentences from a template string.

```python
from syntaxis import Syntaxis

sx = Syntaxis()
sentence_parts = sx.generate_sentence("[article:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:3:sg]")
for part in sentence_parts:
    print(part.lemma)
```

## Template Syntax

A template is a string that defines the structure of a sentence. It is composed of one or more "tokens", where each token represents a word to be generated.

Tokens are enclosed in square brackets `[]`.

**Example:** `[article:nom:masc:sg] [noun:nom:masc:sg]`

This template specifies an article followed by a noun, both in the nominative, masculine, singular form.

### Token Format

Each token follows the format: `[POS:feature1:feature2:...]`

-   **POS**: The Part of Speech for the word.
-   **features**: A colon-separated list of grammatical features that the word must have. The order of features does not matter.

### Parts of Speech (POS)

The following are the valid Part of Speech tags you can use in a token:

-   `noun`
-   `verb`
-   `adj` (adjective)
-   `article`
-   `pronoun`
-   `adv` (adverb)
-   `prep` (preposition)
-   `conj` (conjunction)
-   `numeral`

### Features

The required features depend on the Part of Speech.

#### For `noun`, `adj` (adjective), and `article`

These require exactly 3 features:
-   **Case**: `nom`, `gen`, `acc`, `voc`
-   **Gender**: `masc`, `fem`, `neut`
-   **Number**: `sg`, `pl`

**Example:** `[noun:acc:fem:pl]` - A plural feminine noun in the accusative case.

#### For `verb`

Verbs require exactly 4 features:
-   **Tense**: `present`, `aorist`, `paratatikos`
-   **Voice**: `active`, `passive`
-   **Person**: `pri` (1st), `sec` (2nd), `ter` (3rd)
-   **Number**: `sg`, `pl`

**Example:** `[verb:aorist:active:pri:sg]` - A verb in the aorist tense, active voice, 1st person singular.

#### For `pronoun`

Pronouns require 3 or 4 features:
-   **Case**: `nom`, `gen`, `acc`
-   **Person**: `pri` (1st), `sec` (2nd), `ter` (3rd)
-   **Number**: `sg`, `pl`
-   **Gender** (`masc`, `fem`, `neut`): Optional, but required for 3rd person pronouns.

**Example:** `[pronoun:gen:ter:sg:masc]` - A masculine 3rd person singular pronoun in the genitive case.

#### For `adv`, `prep`, `conj`, `numeral`

These parts of speech are considered invariable and do not take any features.

**Example:** `[adv]`

### Putting it all together: Example Templates

-   A simple sentence "the man sees":
    `[article:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:3:sg]`

-   A prepositional phrase "with the women":
    `[prep] [article:acc:fem:pl] [noun:acc:fem:pl]`

-   An adjective modifying a noun "the big books":
    `[article:nom:neut:pl] [adj:nom:neut:pl] [noun:nom:neut:pl]`
