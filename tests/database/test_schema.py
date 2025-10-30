import sqlite3

import pytest

from syntaxis.database.schema import create_schema


def test_schema_creates_greek_nouns_with_bitmask_columns():
    """greek_nouns table should have number_mask and case_mask columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_nouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "number_mask" in columns
    assert columns["number_mask"] == "INTEGER"
    assert "case_mask" in columns
    assert columns["case_mask"] == "INTEGER"
    assert "gender" in columns  # Existing column
    assert "lemma" in columns


def test_schema_creates_greek_verbs_with_bitmask_columns():
    """greek_verbs table should have all verb feature mask columns."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_verbs)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "tense_mask" in columns
    assert "voice_mask" in columns
    assert "mood_mask" in columns
    assert "number_mask" in columns
    assert "person_mask" in columns
    assert "case_mask" in columns
    for col in [
        "tense_mask",
        "voice_mask",
        "mood_mask",
        "number_mask",
        "person_mask",
        "case_mask",
    ]:
        assert columns[col] == "INTEGER"


def test_schema_creates_greek_adjectives_with_bitmask_columns():
    """greek_adjectives table should have number_mask and case_mask."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_adjectives)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "number_mask" in columns
    assert "case_mask" in columns


def test_schema_creates_greek_articles_with_bitmask_columns():
    """greek_articles table should have gender_mask, number_mask, case_mask."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_articles)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender_mask" in columns
    assert "number_mask" in columns
    assert "case_mask" in columns


def test_schema_creates_greek_pronouns_with_bitmask_columns():
    """greek_pronouns table should have gender_mask, number_mask, case_mask."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_pronouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "gender_mask" in columns
    assert "number_mask" in columns
    assert "case_mask" in columns
    assert "person" in columns  # Existing column
