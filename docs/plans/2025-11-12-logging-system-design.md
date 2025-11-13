# Logging System Design

**Date:** 2025-11-12
**Status:** Approved
**Author:** Claude Code

## Overview

Add comprehensive logging throughout the Syntaxis codebase to aid debugging and observability. The system will use a decorator-based approach with manual fallback, outputting human-readable colored logs to console.

## Requirements

### Functional Requirements
- **Output:** Console only (stdout/stderr)
- **Level Control:** Environment variable `SYNTAXIS_LOG_LEVEL` (defaults to INFO)
- **Format:** Human-readable with terminal colors
- **Coverage:** Template parsing, database queries, word generation, API/service requests, and other relevant operations

### Non-Functional Requirements
- Minimal performance impact from decorators
- Clean, readable log output at INFO level
- Detailed diagnostics available at DEBUG level
- Standard Python logging module (no external dependencies for core logging)

## Design

### 1. Logger Setup and Configuration

Create `syntaxis/lib/logging.py` module with:

**Configuration:**
- Reads `SYNTAXIS_LOG_LEVEL` environment variable (defaults to INFO)
- Configures colored console output with ANSI codes (TTY-aware)
- Log format: `[%(asctime)s] %(levelname)s [%(name)s:%(funcName)s:%(lineno)d] %(message)s`

**Color Scheme:**
- ERROR: Red
- WARNING: Yellow
- INFO: Cyan
- DEBUG: Gray

**API:**
- `setup_logging()`: Call once at application startup
- Each module gets logger via standard `logging.getLogger(__name__)`

### 2. Decorator Implementation

Create `@log_calls` decorator that automatically logs:

**Function Entry (DEBUG):**
- Function name and module
- Arguments (truncated to 100 chars if long)
- Timestamp

**Function Exit (DEBUG):**
- Function name
- Return value (truncated to 100 chars)
- Execution time in milliseconds

**Exception Handling (ERROR):**
- Function name
- Exception type and message
- Re-raises exception after logging

**Features:**
- Lightweight implementation (minimal overhead)
- Supports both sync and async functions
- Skips common dunder methods to reduce noise
- Truncates large values to prevent log spam

### 3. Coverage Plan

#### Decorator Application (@log_calls)

Apply to high-value tracing points:
- **Parsers:** `Template._parse_token`, `V1Parser.parse`, `V2Parser.parse_template`
- **Database:** `Database.get_random_word`, `Database.add_word`, `Database._execute_query`
- **Morpheus:** `Morpheus.create`, `Morpheus._get_inflected_forms`
- **API Routes:** All handlers in `service/api/routes.py`
- **CLI Commands:** All command functions in `cli/app.py`

#### Manual Logging

Strategic placement for mid-function insights:
- **INFO:** Operation milestones and completions
- **DEBUG:** State inspection and decision points
- **ERROR:** Exception handlers and validation failures
- **WARNING:** Unexpected but recoverable situations

#### Skip Logging

Avoid noise from:
- Simple property getters/setters
- Data classes and models (unless complex logic)
- Test files (have their own output)

### 4. Log Level Guidelines

#### DEBUG Level - Detailed Diagnostics
- Template: "Parsing token: [noun:nom:masc:sg]", "Extracted 4 features from token"
- Database: "Executing SQL: SELECT * FROM greek_nouns WHERE...", "Query returned 15 rows in 2ms"
- Morpheus: "Translating MGI forms for lemma 'άνθρωπος'", "Found gender=masc, number=sg, case=nom"
- Feature matching: "Checking word 'άνθρωπος' against features {gender:masc, case:nom}"

#### INFO Level - Key Operations
- Template: "Successfully parsed template with 3 tokens"
- Database: "Connected to database at syntaxis.db", "Added word 'μεγάλος' to greek_adjectives"
- Sentence generation: "Generated sentence: 'ο άνθρωπος βλέπει'"
- API: "GET /api/generate - 200 OK (45ms)"
- CLI: "Seeded 150 nouns into database"

#### ERROR Level - Failures
- Template: "Failed to parse template: Unknown part of speech 'xyz'"
- Database: "No words found matching features {case:nom, gender:masc, number:sg}"
- Morpheus: "MGI returned no forms for lemma 'invalid'"
- API: "Request validation failed: missing required field 'template'"

#### WARNING Level - Unexpected Situations
- "Morpheus returned unexpected form structure, using fallback"
- "Database query slow: 500ms (expected <100ms)"

### 5. Integration Plan

#### Step 1: Create Logging Infrastructure
- Create `syntaxis/lib/logging.py` with `setup_logging()` function
- Implement `@log_calls` decorator with timing and truncation
- Add color support with TTY detection
- Handle `SYNTAXIS_LOG_LEVEL` environment variable

#### Step 2: Initialize at Entry Points
- **CLI:** Call `setup_logging()` in `cli/app.py` before Typer app
- **Service:** Call `setup_logging()` in `service/app.py` at FastAPI startup
- **Library:** Call `setup_logging()` in `syntaxis/lib/__init__.py` for import usage

#### Step 3: Add Module Loggers
- Add `logger = logging.getLogger(__name__)` to all relevant modules
- Replace existing print statements (e.g., `lexical_mapper.py:35`) with logger calls

#### Step 4: Apply Decorators
- Add `@log_calls` to high-value functions
- Start conservatively, expand based on debugging needs

#### Step 5: Add Manual Logs
- INFO logs at operation boundaries
- DEBUG logs for state inspection
- ERROR logs in exception handlers

#### Step 6: Testing and Validation
- Test with `SYNTAXIS_LOG_LEVEL=DEBUG` for comprehensive output
- Test with `SYNTAXIS_LOG_LEVEL=INFO` for clean output
- Verify no performance regression

## Implementation Considerations

### Performance
- Decorator overhead should be negligible (microseconds per call)
- String truncation prevents memory issues with large objects
- Only format log messages when level is enabled (lazy evaluation)

### Maintenance
- Follow standard Python logging patterns (easy for contributors)
- Centralized configuration makes changes simple
- Clear guidelines prevent inconsistent logging

### Future Enhancements
- Could add structured JSON logging for production (currently out of scope)
- Could add file output with rotation (currently out of scope)
- Could add per-module log levels via config file (currently out of scope)

## Success Criteria

- All major operations have entry/exit logging via decorator
- Key state changes logged manually at appropriate levels
- DEBUG level provides sufficient detail for troubleshooting
- INFO level provides clean operational visibility
- No print() statements remain in production code
- Performance impact is imperceptible (<1% overhead)
