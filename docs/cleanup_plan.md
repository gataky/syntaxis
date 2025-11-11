# Syntaxis Codebase Cleanup Plan

**Generated:** 2025-11-10
**Status:** In Progress

## Overview

This document tracks cleanup opportunities identified in the Syntaxis codebase (1,858 lines production code, 855 lines test code). Focus areas: test coverage, unused code removal, and documentation improvements.

---

## 1. Test Coverage Gaps (~46% current coverage)

### Critical Priority (No Tests - 0% coverage)

#### ✅ syntaxis/api.py
- **Location:** `/Users/jeff/Documents/syntaxis/syntaxis/api.py`
- **Lines:** 127 (now with comprehensive docstrings)
- **Issue:** Main `Syntaxis` class and `generate_sentence()` method completely untested
- **Impact:** HIGH - This is the primary public API
- **Action:** Create `tests/test_api.py`
- **Test Requirements:**
  - End-to-end test with real templates
  - Test with various template types (nominal, verbal, mixed)
  - Mock database for isolation
  - Error handling tests
- **Completed:** Created comprehensive test suite with 30 tests covering:
  - All lexical types (nouns, verbs, adjectives, articles, pronouns, prepositions, adverbs, conjunctions)
  - Single and multi-token templates
  - Different grammatical features
  - Error handling (invalid templates, missing features)
  - Integration tests with complex templates
  - All tests passing ✅
- **Status:** ✅ Completed

#### ✅ syntaxis/cli.py
- **Location:** `/Users/jeff/Documents/syntaxis/syntaxis/cli.py`
- **Lines:** 68
- **Issue:** All CLI commands untested (`create_db`, `seed_dictionary`, `seed_pronouns`, `seed_articles`)
- **Impact:** HIGH - User-facing interface
- **Action:** Create `tests/test_cli.py`
- **Test Requirements:**
  - Use Typer's CliRunner for testing
  - Test `create_db()` with temp files
  - Test `seed_dictionary()` with mock CSV
  - Test `seed_pronouns()` and `seed_articles()`
  - Test --clear flag behavior
- **Completed:** Created comprehensive CLI test suite with 19 tests covering:
  - Database creation with default and custom names
  - --clear flag functionality
  - Dictionary seeding from CSV
  - Pronoun and article seeding
  - Error handling (nonexistent files, empty CSVs)
  - Default parameter behavior
  - Full integration workflow
  - All tests passing ✅
- **Status:** ✅ Completed

#### ❌ syntaxis/models/lexical.py
- **Location:** `/Users/jeff/Documents/syntaxis/syntaxis/models/lexical.py`
- **Lines:** 99
- **Issue:** All 9 `Lexical` subclasses lack tests for `apply_features()` methods
- **Impact:** MEDIUM - Core functionality
- **Action:** Create `tests/models/test_lexical.py`
- **Test Requirements:**
  - Test `apply_features()` for: Noun, Verb, Adjective, Article, Pronoun, Adverb, Numeral, Preposition, Conjunction
  - Test word extraction from forms dictionary
  - Test edge cases with missing features
  - Test the base class NotImplementedError
- **Status:** ⬜ Not Started

### Medium Priority (Partial Coverage)

#### 🟡 syntaxis/morpheus/api.py
- **Location:** `/Users/jeff/Documents/syntaxis/syntaxis/morpheus/api.py`
- **Lines:** 113
- **Current Coverage:** ~40% (38 lines of tests)
- **Issue:** Only Noun and Verb tested; missing Adjective, Article, Pronoun, Adverb, Numeral
- **Action:** Expand `tests/morpheus/test_morpheus.py`
- **Status:** ⬜ Not Started

#### 🟡 Seed Data Tests
- **Location:**
  - `/Users/jeff/Documents/syntaxis/syntaxis/database/seeds/pronouns.py` (136 lines)
  - `/Users/jeff/Documents/syntaxis/syntaxis/database/seeds/articles.py` (85 lines)
- **Issue:** No validation of seed data integrity
- **Action:** Create `tests/database/test_seeds.py`
- **Status:** ⬜ Not Started

#### 🟡 Constants Validation
- **Location:** `/Users/jeff/Documents/syntaxis/syntaxis/models/constants.py` (131 lines)
- **Issue:** No tests for LEXICAL_MAP completeness or constant definitions
- **Action:** Create `tests/models/test_constants.py`
- **Status:** ⬜ Not Started

### Low Priority Enhancements

#### Integration Tests
- **Action:** Create `tests/test_integration.py`
- **Requirements:** Full workflow test (create DB → seed → query → parse → generate)
- **Status:** ⬜ Not Started

#### Test Infrastructure
- **Action:** Set up pytest-cov and coverage reporting
- **Requirements:**
  - Add `.coveragerc` configuration
  - Add coverage badge to README
  - Set up CI/CD coverage reporting
- **Status:** ⬜ Not Started

#### Shared Fixtures
- **Action:** Create `tests/conftest.py`
- **Requirements:**
  - Shared database fixtures
  - Template parser fixture
  - Mock data generators
- **Status:** ⬜ Not Started

---

## 2. Unused Code to Remove

### Dead Code

#### ❌ Unused Constants: FUTURE and FUTURE_SIMPLE
- **Location:** `syntaxis/models/constants.py:85-86`
- **Code:**
  ```python
  FUTURE = "future c"
  FUTURE_SIMPLE = "future s"
  ```
- **Issue:** Not included in TENSE_VALUES set, never referenced anywhere
- **Action:** Delete these two constants
- **Status:** ⬜ Not Started

#### ❌ Unused Method: count_total_words()
- **Location:** `syntaxis/database/api.py:116-132`
- **Issue:** Public method never called anywhere in codebase
- **Action:** Either delete or add to API if needed
- **Status:** ⬜ Not Started

#### ❌ Stub Implementation: NUMERAL
- **Location:** `syntaxis/models/constants.py:16, 26, 118` and related
- **Issue:** NUMERAL constant exists, has Morpheus support, but never used in templates
- **Action:** Either:
  - Option A: Implement full template support for numerals
  - Option B: Remove NUMERAL constant and related code
- **Decision Needed:** Do you want numeral support?
- **Status:** ⬜ Not Started

#### ❌ Debug Code
- **Location:** `scripts/exp.py:5`
- **Code:** `# import pudb; pudb.set_trace()`
- **Action:** Remove commented debug line
- **Status:** ⬜ Not Started

### Code Duplication

#### 🔄 Duplicated apply_features() Methods
- **Location:** `syntaxis/models/lexical.py`
- **Issue:** 5 classes (Noun, Adjective, Article, Pronoun, Numeral) have nearly identical implementations
- **Pattern:** All use `forms[gender][number][case]`
- **Action:** Refactor to shared helper method or base class implementation
- **Suggested Approach:**
  ```python
  def _apply_nominal_features(forms, gender, number, case):
      """Shared implementation for nominal word types."""
      return forms[gender][number][case]
  ```
- **Status:** ⬜ Not Started

#### 🔄 Database Query Pattern Duplication
- **Location:** `syntaxis/database/api.py:87-99, 148-158`
- **Issue:** `get_random_word()` and `_get_word_by_lemma()` have nearly identical SQL queries
- **Action:** Extract shared SQL into helper method
- **Status:** ⬜ Not Started

### TODOs to Resolve

#### 📝 LEXICAL_MAP TODO
- **Location:** `syntaxis/models/constants.py:110`
- **Code:**
  ```python
  # TODO: do we really need this? Perhaps just force the csv to follow conventions here.
  LEXICAL_MAP = {...}
  ```
- **Action:** Decide and document: keep mapping or enforce CSV conventions
- **Status:** ⬜ Not Started

---

## 3. Documentation Improvements

### Critical Missing Documentation

#### ✅ syntaxis/api.py - Main Entry Point
- **Location:** `syntaxis/api.py:1-127`
- **Issue:**
  - `Syntaxis` class has NO class docstring
  - `__init__()` has NO docstring
  - `generate_sentence()` has NO docstring (main public API!)
- **Impact:** HIGHEST - Primary user-facing API
- **Action:** Add comprehensive docstrings with examples
- **Completed:** Added comprehensive Google-style docstrings with:
  - Class-level docstring explaining the workflow and purpose
  - Full `__init__()` docstring with Raises section
  - Detailed `generate_sentence()` docstring with Args, Returns, Raises, Examples, and Note sections
  - Multiple usage examples showing different template types
- **Status:** ✅ Completed

#### ❌ syntaxis/models/lexical.py - All Subclasses
- **Location:** `syntaxis/models/lexical.py:39-98`
- **Issue:** 9 subclasses lack docstrings: Adjective, Adverb, Article, Noun, Numeral, Pronoun, Verb, Preposition, Conjunction
- **Impact:** HIGH - Core data model
- **Action:** Add docstring to each class explaining:
  - What part of speech it represents
  - Structure of the forms dictionary
  - Example of usage
- **Status:** ⬜ Not Started

#### ❌ Complex Methods Need Inline Comments
- **Location:** `syntaxis/database/api.py`
- **Methods Needing Comments:**
  1. `_extract_verb_features()` (lines 211-320) - Very complex nested logic
  2. `get_random_word()` (lines 42-112) - SQL parameter ordering unclear
  3. `_execute_add_word_transaction()` (lines 466-521) - Complex transaction logic
- **Action:** Add inline comments explaining:
  - WHY the structure exists (not just WHAT)
  - Rationale for conditional checks
  - Data flow through nested structures
- **Status:** ⬜ Not Started

### Documentation Style Inconsistencies

#### 📋 Standardize Docstring Format
- **Issue:** Mixed styles across codebase
  - Database: Detailed Args/Returns/Raises format
  - API: No docstrings
  - CLI: Brief one-liners
- **Action:** Choose standard (Google or NumPy style) and document in CONTRIBUTING.md
- **Status:** ⬜ Not Started

### Missing Documentation Files

#### 📄 Data Structures Guide
- **Action:** Create `docs/data_structures.md`
- **Content:**
  - Explain nested dictionary structure for forms (Noun, Verb, Adjective, etc.)
  - Provide examples of actual forms dictionaries
  - Document structure for each part of speech
- **Status:** ⬜ Not Started

#### 📄 Architecture Documentation
- **Action:** Create `docs/architecture.md`
- **Content:**
  - System overview diagram
  - Module relationships
  - Explain morpheus translation layer design
  - Data flow from template to generated sentence
- **Status:** ⬜ Not Started

#### 📄 Expand README.md
- **Location:** `README.md` (currently minimal)
- **Action:** Add:
  - Quick start example
  - Installation instructions
  - Link to detailed guides
  - Basic usage examples
- **Status:** ⬜ Not Started

---

## Implementation Phases

### Phase 1: Critical Fixes (1-2 hours)
**Goal:** Fix highest-impact documentation and remove dead code

- [x] Add docstrings to `Syntaxis` class and `generate_sentence()` method
- [ ] Add docstrings to all 9 `Lexical` subclasses
- [ ] Remove unused `FUTURE` and `FUTURE_SIMPLE` constants
- [ ] Remove or document `count_total_words()` method
- [ ] Clean up debug comment in `scripts/exp.py`

### Phase 2: Test Coverage (3-4 hours)
**Goal:** Get critical modules under test

- [x] Create `tests/test_api.py` - test `generate_sentence()` end-to-end
- [x] Create `tests/test_cli.py` - test all CLI commands
- [ ] Create `tests/models/test_lexical.py` - test `apply_features()` for all classes
- [ ] Expand `tests/morpheus/test_morpheus.py` - cover all parts of speech
- [ ] Set up pytest-cov for coverage reporting

### Phase 3: Code Quality (2-3 hours)
**Goal:** Reduce duplication and improve maintainability

- [ ] Refactor duplicated `apply_features()` methods
- [ ] Extract shared database query patterns
- [ ] Add inline comments to complex database methods
- [ ] Resolve TODO in constants.py about LEXICAL_MAP
- [ ] Decide on NUMERAL: implement fully or remove

### Phase 4: Documentation Enhancement (2-3 hours)
**Goal:** Create comprehensive developer and user documentation

- [ ] Create `docs/data_structures.md`
- [ ] Create `docs/architecture.md`
- [ ] Expand README.md with quick start
- [ ] Standardize docstring format and document in CONTRIBUTING.md
- [ ] Create `tests/conftest.py` with shared fixtures

---

## Progress Tracking

- **Total Items:** 32
- **Completed:** 3
- **In Progress:** 0
- **Not Started:** 29

**Last Updated:** 2025-11-10

---

## Notes

- Consider running a code quality tool like `pylint` or `ruff` to find additional issues
- Consider adding pre-commit hooks to enforce standards
- Test coverage target: 80%+
- All public APIs should have comprehensive docstrings with examples
