"""Seed data for Modern Greek articles."""

import sqlite3

from syntaxis.models import constants as c


def seed(conn: sqlite3.Connection) -> None:
    """Populate greek_articles table with Modern Greek articles and their translations.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Format: (lemma, type, gender, number, case, validation_status, english_translation)
    articles_with_translations = [
        # Definite Articles
        ("ο",   c.DEFINITE, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", "the"),
        ("του", c.DEFINITE, c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated", "the"),
        ("τον", c.DEFINITE, c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated", "the"),
        ("οι",  c.DEFINITE, c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated", "the"),
        ("των", c.DEFINITE, c.MASCULINE, c.PLURAL,   c.GENITIVE,   "validated", "the"),
        ("τους",c.DEFINITE, c.MASCULINE, c.PLURAL,   c.ACCUSATIVE, "validated", "the"),
        ("η",   c.DEFINITE, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", "the"),
        ("της", c.DEFINITE, c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated", "the"),
        ("την", c.DEFINITE, c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated", "the"),
        ("οι",  c.DEFINITE, c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated", "the"),
        ("των", c.DEFINITE, c.FEMININE,  c.PLURAL,   c.GENITIVE,   "validated", "the"),
        ("τις", c.DEFINITE, c.FEMININE,  c.PLURAL,   c.ACCUSATIVE, "validated", "the"),
        ("το",  c.DEFINITE, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", "the"),
        ("το",  c.DEFINITE, c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated", "the"),
        ("του", c.DEFINITE, c.NEUTER,    c.SINGULAR, c.GENITIVE,   "validated", "the"),
        ("τα",  c.DEFINITE, c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated", "the"),
        ("τα",  c.DEFINITE, c.NEUTER,    c.PLURAL,   c.ACCUSATIVE, "validated", "the"),
        ("των", c.DEFINITE, c.NEUTER,    c.PLURAL,   c.GENITIVE,   "validated", "the"),

        # Indefinite Articles
        ("ένας", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", "a"),
        ("ενός", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated", "a"),
        ("έναν", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated", "a"),
        ("μια",  c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", "a"),
        ("μια",  c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated", "a"),
        ("μιας", c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated", "a"),
        ("ένα",  c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", "a"),
        ("ένα",  c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated", "a"),
        ("ενός", c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.GENITIVE,   "validated", "a"),
    ]

    # Extract article data for greek_articles table
    articles = [a[:-1] for a in articles_with_translations]

    # Insert articles
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_articles
        (lemma, type, gender, number, form, validation_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        articles
    )
    print(f"Seeded {cursor.rowcount} article forms into greek_articles table")

    # Seed translations
    for lemma, _, _, _, _, _, english_word in articles_with_translations:
        # Insert English word
        cursor.execute(
            "INSERT OR IGNORE INTO english_words (word, lexical) VALUES (?, ?)",
            (english_word, c.ARTICLE),
        )
        # Get English word ID
        eng_id_row = cursor.execute(
            "SELECT id FROM english_words WHERE word = ? AND lexical = ?",
            (english_word, c.ARTICLE),
        ).fetchone()
        if eng_id_row:
            eng_id = eng_id_row[0]
            # Insert translation link
            cursor.execute(
                "INSERT OR IGNORE INTO translations (english_word_id, greek_lemma, greek_lexical) VALUES (?, ?, ?)",
                (eng_id, lemma, c.ARTICLE),
            )

    conn.commit()
    print("Seeded article translations.")
