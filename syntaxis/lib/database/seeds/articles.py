"""Seed data for Modern Greek articles."""

import sqlite3

from syntaxis.lib import constants as c


def seed(conn: sqlite3.Connection) -> None:
    """Populate greek_articles table with Modern Greek articles and their translations.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Format: (lemma, type, gender, number, case, validation_status, english_translation)
    articles_with_translations = [
        # Definite Articles masculine
        ("ο",    c.DEFINITE,   c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated", "the"),
        ("ο",    c.DEFINITE,   c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.MASCULINE, c.PLURAL,   c.GENITIVE,   "validated", "the"),
        ("ο",    c.DEFINITE,   c.MASCULINE, c.PLURAL,   c.ACCUSATIVE, "validated", "the"),
        # feminine
        ("ο",    c.DEFINITE,   c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated", "the"),
        ("ο",    c.DEFINITE,   c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.FEMININE,  c.PLURAL,   c.GENITIVE,   "validated", "the"),
        ("ο",    c.DEFINITE,   c.FEMININE,  c.PLURAL,   c.ACCUSATIVE, "validated", "the"),
        # neuter
        ("ο",    c.DEFINITE,   c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.NEUTER,    c.SINGULAR, c.GENITIVE,   "validated", "the"),
        ("ο",    c.DEFINITE,   c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.NEUTER,    c.PLURAL,   c.ACCUSATIVE, "validated", "the"),
        ("ο",    c.DEFINITE,   c.NEUTER,    c.PLURAL,   c.GENITIVE,   "validated", "the"),
        # Indefinite Articles masculine
        ("ένας", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", "a"),
        ("ένας", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated", "a"),
        ("ένας", c.INDEFINITE, c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated", "a"),
        # feminine
        ("ένας", c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", "a"),
        ("ένας", c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated", "a"),
        ("ένας", c.INDEFINITE, c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated", "a"),
        # neuter
        ("ένας", c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", "a"),
        ("ένας", c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated", "a"),
        ("ένας", c.INDEFINITE, c.NEUTER,    c.SINGULAR, c.GENITIVE,   "validated", "a"),
    ]

    # Extract article data for greek_articles table
    articles = [a[:-1] for a in articles_with_translations]

    # Insert articles
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_articles
        (lemma, type, gender, number, [case], validation_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        articles,
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
