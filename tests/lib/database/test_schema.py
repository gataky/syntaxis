import sqlite3

import pytest

from syntaxis.lib.database.schema import create_schema


def test_schema_creates_greek_nouns_with_bitmask_columns():
    """greek_nouns table should have feature columns (gender, number, case)."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_nouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "number" in columns
    assert columns["number"] == "TEXT"
    assert "case" in columns
    assert columns["case"] == "TEXT"
    assert "gender" in columns
    assert columns["gender"] == "TEXT"
    assert "lemma" in columns


def test_schema_creates_greek_verbs_with_bitmask_columns():
    """greek_verbs table should have all verb feature columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_verbs)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "tense" in columns
    assert "voice" in columns
    assert "mood" in columns
    assert "number" in columns
    assert "person" in columns
    assert "case" in columns
    for col in [
        "tense",
        "voice",
        "mood",
        "number",
        "person",
        "case",
    ]:
        assert columns[col] == "TEXT"


def test_schema_creates_greek_adjectives_with_bitmask_columns():
    """greek_adjectives table should have feature columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_adjectives)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender" in columns
    assert columns["gender"] == "TEXT"
    assert "number" in columns
    assert columns["number"] == "TEXT"
    assert "case" in columns
    assert columns["case"] == "TEXT"


def test_schema_creates_greek_articles_with_bitmask_columns():
    """greek_articles table should have feature columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_articles)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender" in columns
    assert columns["gender"] == "TEXT"
    assert "number" in columns
    assert columns["number"] == "TEXT"
    assert "case" in columns
    assert columns["case"] == "TEXT"


def test_schema_creates_greek_pronouns_with_bitmask_columns():
    """greek_pronouns table should have feature columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_pronouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender" in columns
    assert columns["gender"] == "TEXT"
    assert "number" in columns
    assert columns["number"] == "TEXT"
    assert "case" in columns
    assert columns["case"] == "TEXT"
    assert "person" in columns
    assert columns["person"] == "TEXT"


def test_create_schema_creates_templates_table():
    """Should create templates table with correct schema."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='templates'"
    )
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == "templates"


def test_templates_table_has_correct_columns():
    """Should create templates table with id, template, created_at columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(templates)")
    columns = cursor.fetchall()

    column_names = [col[1] for col in columns]
    assert "id" in column_names
    assert "template" in column_names
    assert "created_at" in column_names


def test_templates_table_unique_constraint_on_template():
    """Should enforce UNIQUE constraint on template column."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO templates (template) VALUES (?)",
        ("noun(case=nominative,gender=masculine,number=singular)",),
    )
    conn.commit()

    # Try to insert duplicate
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
        cursor.execute(
            "INSERT INTO templates (template) VALUES (?)",
            ("noun(case=nominative,gender=masculine,number=singular)",),
        )
