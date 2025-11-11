# Unit Testing Suggestions for Syntaxis

This document outlines areas within the Syntaxis codebase where additional unit tests would significantly improve code quality, stability, and maintainability. The suggestions focus on modules with core logic and critical functionality.

## High-Priority Areas for New Unit Tests

### 1. `syntaxis/models/lexical.py`

This module defines the core logic for word inflection and conjugation. The `Lexical` base class and its numerous subclasses (e.g., `Adjective`, `Noun`, `Verb`) implement the `apply_features` method, which is central to the application's linguistic processing. Robust unit tests are crucial here to ensure correct behavior across all grammatical features and word types.

**Test Suggestions for `Lexical` (Base Class):**
*   Test instantiation with `lemma` and `forms`.
*   Test `__str__` method behavior:
    *   When `word` is `None` (should return `lemma`).
    *   When `word` is a `set` (should return the first element).
*   Test that `apply_features` on the base class raises `NotImplementedError`.

**Test Suggestions for `apply_features` in Subclasses (e.g., `Adjective`, `Noun`, `Verb`):**
*   **Happy Path:** Test with various valid combinations of grammatical features (e.g., gender, number, case, tense, voice) that are expected to exist in the `forms` data. Verify that `self.word` is correctly set and returned.
*   **Edge Cases/Invalid Features:** Test with invalid or non-existent feature values. This should ideally result in a `KeyError` as the method navigates nested dictionaries. Test that these errors are raised as expected.
*   **Missing Required Features:** Test scenarios where required features are not provided, which would also likely lead to `KeyError` or `TypeError`.
*   **Data Structure Integrity:** While not direct unit tests for `lexical.py`, tests should indirectly confirm that the `forms` data (which would come from `syntaxis/models/types.py` definitions) correctly supports the `apply_features` logic.

### 2. `syntaxis/api.py`

This file contains the main `Syntaxis` class, which orchestrates interactions between the database, template parsing, and lexical models.

**Test Suggestions for `Syntaxis` class:**
*   **`__init__` method:**
    *   Ensure that `Database` and `Template` objects are initialized correctly.
    *   Use mocking to verify that `Database` and `Template` constructors are called with the expected arguments.
*   **`generate_sentence` method:**
    *   Mock `self.template.parse` to return a predictable `parsed` object (e.g., a mock object with a `tokens` attribute).
    *   Mock `self.database.get_random_word` to return predictable `Lexical` objects or `None`.
    *   Test with various template inputs (e.g., simple templates, templates with multiple tokens, templates with specific feature requests).
    *   Verify that the correct sequence of `Lexical` objects is returned.
    *   Test cases where `get_random_word` might return `None` or raise an error, and how `generate_sentence` handles these scenarios.

### 3. `syntaxis/cli.py`

This module defines the command-line interface for Syntaxis, including database creation and seeding functionalities. Testing CLI commands typically involves using `typer.testing.CliRunner`.

**Test Suggestions for CLI Commands:**
*   **`create_db` command:**
    *   Test that a database file is created when the command is run.
    *   Test the `--clear` option: verify that an existing database file is removed and then recreated.
    *   Test with default `db_name` and with a custom `db_name`.
    *   Verify success messages are printed to stdout.
*   **`seed_dictionary` command:**
    *   Mock `csv.reader` to provide controlled test data for the CSV file.
    *   Mock `Database.add_word` to verify that it's called with the correct `lemma`, `translations`, and `lexical` arguments for each entry in the mocked CSV.
    *   Test with valid CSV data.
    *   Test with an empty CSV file.
    *   Test with default `csv_file` path and a custom path.
    *   Verify success messages and word count are printed.
*   **`seed_pronouns` and `seed_articles` commands:**
    *   Mock `seeds.pronouns.seed` and `seeds.articles.seed` functions.
    *   Verify that these seeding functions are called when their respective CLI commands are executed, and that they receive the correct database connection object.
    *   Test with default `db_name` and custom `db_name`.

## Existing Test Coverage (Review for Gaps)

The following modules already have associated test files. It is recommended to review these existing tests to identify any potential gaps in coverage or areas where more granular tests could be added:

*   `syntaxis/database/` (covered by `tests/database/test_database.py` and `test_schema.py`)
*   `syntaxis/morpheus/` (covered by `tests/morpheus/test_morpheus.py` and `test_translator.py`)
*   `syntaxis/templates/` (covered by `tests/templates/test_template_parser.py`)

This review should ensure that all critical functions, edge cases, and error handling paths are adequately tested.
