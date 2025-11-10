import sqlite3

from syntaxis.database.schema import create_schema


def test_schema_creates_greek_nouns_with_bitmask_columns():
    """greek_nouns table should have feature columns (gender, number, form)."""
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(greek_nouns)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "number" in columns
    assert columns["number"] == "TEXT"
    assert "form" in columns
    assert columns["form"] == "TEXT"
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
    assert "form" in columns
    for col in [
        "tense",
        "voice",
        "mood",
        "number",
        "person",
        "form",
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
    assert "form" in columns
    assert columns["form"] == "TEXT"


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
    assert "form" in columns
    assert columns["form"] == "TEXT"


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
    assert "form" in columns
    assert columns["form"] == "TEXT"
    assert "person" in columns
    assert columns["person"] == "TEXT"
