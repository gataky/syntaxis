"""Seed data for Modern Greek articles."""

import sqlite3

from syntaxis.models import constants as c

def seed(conn: sqlite3.Connection) -> None:
    """Populate greek_articles table with Modern Greek articles.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Define articles by type with explicit feature combinations
    # Format: (lemma, type, gender, number, case, validation_status)
    articles = [
        # Definite Articles
        # Masculine
        ("ο",   c.DEFINITE, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("του", c.DEFINITE, c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated"),
        ("τον", c.DEFINITE, c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("οι",  c.DEFINITE, c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated"),
        ("των", c.DEFINITE, c.MASCULINE, c.PLURAL,   c.GENITIVE,   "validated"),
        ("τους",c.DEFINITE, c.MASCULINE, c.PLURAL,   c.ACCUSATIVE, "validated"),
        # Feminine
        ("η",   c.DEFINITE, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("της", c.DEFINITE, c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated"),
        ("την", c.DEFINITE, c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("οι",  c.DEFINITE, c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated"),
        ("των", c.DEFINITE, c.FEMININE,  c.PLURAL,   c.GENITIVE,   "validated"),
        ("τις", c.DEFINITE, c.FEMININE,  c.PLURAL,   c.ACCUSATIVE, "validated"),
        # Neuter
        ("το",  c.DEFINITE, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("το",  c.DEFINITE, c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("του", c.DEFINITE, c.NEUTER,    c.SINGULAR, c.GENITIVE,   "validated"),
        ("τα",  c.DEFINITE, c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated"),
        ("τα",  c.DEFINITE, c.NEUTER,    c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("των", c.DEFINITE, c.NEUTER,    c.PLURAL,   c.GENITIVE,   "validated"),

        # Indefinite Articles
        # Masculine
        ("ένας", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("ενός", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated"),
        ("έναν", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated"),
        # Feminine
        ("μια",  c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("μια",  c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("μιας", c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated"),
        # Neuter
        ("ένα",  c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("ένα",  c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("ενός", c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.GENITIVE,   "validated"),
    ]

    # Insert articles
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_articles
        (lemma, type, gender, number, form, validation_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        articles
    )

    conn.commit()
    print(f"Seeded {cursor.rowcount} article forms into greek_articles table")
