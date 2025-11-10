"""Seed data for Modern Greek pronouns."""

import sqlite3

from syntaxis.models import constants as c


def seed_pronouns(conn: sqlite3.Connection) -> None:
    """Populate greek_pronouns table with Modern Greek pronouns.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Define pronouns by type with explicit feature combinations
    # Format: (lemma, type, person, gender, number, case, validation_status)
    pronouns = [
        # Personal Strong Pronouns - Nominative
        ("εγώ",   "personal_strong", c.FIRST,  None,       c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εσύ",   "personal_strong", c.SECOND, None,       c.SINGULAR, c.NOMINATIVE, "validated"),
        ("αυτός", "personal_strong", c.THIRD,  c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("αυτή",  "personal_strong", c.THIRD,  c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("αυτό",  "personal_strong", c.THIRD,  c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εμείς", "personal_strong", c.FIRST,  None,       c.PLURAL,   c.NOMINATIVE, "validated"),
        ("εσείς", "personal_strong", c.SECOND, None,       c.PLURAL,   c.NOMINATIVE, "validated"),
        ("αυτοί", "personal_strong", c.THIRD,  c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated"),
        ("αυτές", "personal_strong", c.THIRD,  c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated"),
        ("αυτά",  "personal_strong", c.THIRD,  c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated"),

        # Personal Weak Pronouns - Genitive
        ("μου",  "personal_weak", c.FIRST,  None,       c.SINGULAR, c.GENITIVE, "validated"),
        ("σου",  "personal_weak", c.SECOND, None,       c.SINGULAR, c.GENITIVE, "validated"),
        ("του",  "personal_weak", c.THIRD,  c.MASCULINE, c.SINGULAR, c.GENITIVE, "validated"),
        ("της",  "personal_weak", c.THIRD,  c.FEMININE,  c.SINGULAR, c.GENITIVE, "validated"),
        ("μας",  "personal_weak", c.FIRST,  None,       c.PLURAL,   c.GENITIVE, "validated"),
        ("σας",  "personal_weak", c.SECOND, None,       c.PLURAL,   c.GENITIVE, "validated"),
        ("τους", "personal_weak", c.THIRD,  None,       c.PLURAL,   c.GENITIVE, "validated"),

        # Personal Weak Pronouns - Accusative
        ("με",  "personal_weak", c.FIRST,  None,       c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("σε",  "personal_weak", c.SECOND, None,       c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("τον", "personal_weak", c.THIRD,  c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("την", "personal_weak", c.THIRD,  c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("το",  "personal_weak", c.THIRD,  c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("μας", "personal_weak", c.FIRST,  None,       c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("σας", "personal_weak", c.SECOND, None,       c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("τους","personal_weak", c.THIRD,  c.MASCULINE, c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("τις", "personal_weak", c.THIRD,  c.FEMININE,  c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("τα",  "personal_weak", c.THIRD,  c.NEUTER,    c.PLURAL,   c.ACCUSATIVE, "validated"),

        # Demonstrative Pronouns - sample forms
        ("τούτος",  "demonstrative", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("τούτη",   "demonstrative", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("τούτο",   "demonstrative", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εκείνος", "demonstrative", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εκείνη",  "demonstrative", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εκείνο",  "demonstrative", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),

        # Interrogative Pronouns
        ("ποιος", "interrogative", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("ποια",  "interrogative", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("ποιο",  "interrogative", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("τι",    "interrogative", None, None,       None,       None,         "validated"),
        ("πόσος", "interrogative", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("πόση",  "interrogative", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("πόσο",  "interrogative", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),

        # Possessive Pronouns
        ("δικός", "possessive", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("δική",  "possessive", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("δικό",  "possessive", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),

        # Indefinite Pronouns
        ("κάποιος", "indefinite", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κάποια",  "indefinite", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κάποιο",  "indefinite", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κανείς",  "indefinite", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("καμία",   "indefinite", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κανένα",  "indefinite", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κάθε",    "indefinite", None, None,       None,       None,         "validated"),
        ("όλος",    "indefinite", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όλη",     "indefinite", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όλο",     "indefinite", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("μερικοί", "indefinite", None, c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated"),
        ("μερικές", "indefinite", None, c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated"),
        ("μερικά",  "indefinite", None, c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated"),
        ("κάτι",    "indefinite", None, None,       None,       None,         "validated"),
        ("τίποτα",  "indefinite", None, None,       None,       None,         "validated"),

        # Relative Pronouns
        ("που",    "relative", None, None,       None,       None,         "validated"),
        ("οποίος", "relative", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("οποία",  "relative", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("οποίο",  "relative", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όποιος", "relative", None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όποια",  "relative", None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όποιο",  "relative", None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
    ]

    # Insert pronouns
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_pronouns
        (lemma, type, person, gender, number, form, validation_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        pronouns
    )

    conn.commit()
    print(f"Seeded {cursor.rowcount} pronoun forms into greek_pronouns table")
