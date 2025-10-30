# Using get_random_word()

## Overview

The `get_random_word()` method retrieves a random Greek word from the lexicon, optionally filtered by grammatical features.

## Basic Usage

```python
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeech as POSEnum

manager = LexicalManager("greek.db")

# Get any random noun
word = manager.get_random_word(POSEnum.NOUN)
print(word.lemma)  # e.g., "άνθρωπος"
print(word.translations)  # e.g., ["person", "human"]
```

## Filtering by Features

### Nouns

Valid features: `gender`, `number`, `case`

```python
from syntaxis.models.enums import Number, Case, Gender

# Get singular nominative masculine noun
word = manager.get_random_word(
    POSEnum.NOUN,
    number=Number.SINGULAR,
    case=Case.NOMINATIVE,
    gender=Gender.MASCULINE
)
```

### Verbs

Valid features: `tense`, `voice`, `mood`, `number`, `person`, `case`

```python
from syntaxis.models.enums import Tense, Voice, Mood

# Get present tense active voice verb
word = manager.get_random_word(
    POSEnum.VERB,
    tense=Tense.PRESENT,
    voice=Voice.ACTIVE
)
```

### Adjectives

Valid features: `number`, `case`

```python
# Get plural genitive adjective
word = manager.get_random_word(
    POSEnum.ADJECTIVE,
    number=Number.PLURAL,
    case=Case.GENITIVE
)
```

## Adding Words with Masks

When adding words to the database, calculate and store bitmasks:

```python
from syntaxis.database.mask_calculator import calculate_masks_for_word

lemma = "άνθρωπος"
masks = calculate_masks_for_word(lemma, POSEnum.NOUN)

cursor.execute(
    """
    INSERT INTO greek_nouns
    (lemma, gender, number_mask, case_mask, validation_status)
    VALUES (?, ?, ?, ?, ?)
    """,
    (lemma, "MASCULINE", masks["number_mask"], masks["case_mask"], "validated")
)
```

## Error Handling

```python
# Invalid feature for POS type raises ValueError
try:
    word = manager.get_random_word(POSEnum.NOUN, tense=Tense.PRESENT)
except ValueError as e:
    print(e)  # "Invalid features {'tense'} for NOUN. Valid features are: {'gender', 'number', 'case'}"

# No matching words returns None
word = manager.get_random_word(POSEnum.NOUN, number=Number.SINGULAR)
if word is None:
    print("No words match the criteria")
```
