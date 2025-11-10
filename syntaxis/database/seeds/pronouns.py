"""Seed data for Modern Greek pronouns."""

import sqlite3

from syntaxis.models import constants as c


def seed(conn: sqlite3.Connection) -> None:
    """Populate greek_pronouns table with Modern Greek pronouns.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Define pronouns by type with explicit feature combinations
    # Format: (lemma, type, person, gender, number, case, validation_status)
    pronouns = [
        # Personal Strong Pronouns - Nominative
        ("εγώ",   c.PERSONAL_STRONG, c.FIRST,  None,       c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εσύ",   c.PERSONAL_STRONG, c.SECOND, None,       c.SINGULAR, c.NOMINATIVE, "validated"),
        ("αυτός", c.PERSONAL_STRONG, c.THIRD,  c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("αυτή",  c.PERSONAL_STRONG, c.THIRD,  c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("αυτό",  c.PERSONAL_STRONG, c.THIRD,  c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εμείς", c.PERSONAL_STRONG, c.FIRST,  None,       c.PLURAL,   c.NOMINATIVE, "validated"),
        ("εσείς", c.PERSONAL_STRONG, c.SECOND, None,       c.PLURAL,   c.NOMINATIVE, "validated"),
        ("αυτοί", c.PERSONAL_STRONG, c.THIRD,  c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated"),
        ("αυτές", c.PERSONAL_STRONG, c.THIRD,  c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated"),
        ("αυτά",  c.PERSONAL_STRONG, c.THIRD,  c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated"),

        # Personal Weak Pronouns - Genitive
        ("μου",  c.PERSONAL_WEAK, c.FIRST,  None,       c.SINGULAR, c.GENITIVE, "validated"),
        ("σου",  c.PERSONAL_WEAK, c.SECOND, None,       c.SINGULAR, c.GENITIVE, "validated"),
        ("του",  c.PERSONAL_WEAK, c.THIRD,  c.MASCULINE, c.SINGULAR, c.GENITIVE, "validated"),
        ("της",  c.PERSONAL_WEAK, c.THIRD,  c.FEMININE,  c.SINGULAR, c.GENITIVE, "validated"),
        ("μας",  c.PERSONAL_WEAK, c.FIRST,  None,       c.PLURAL,   c.GENITIVE, "validated"),
        ("σας",  c.PERSONAL_WEAK, c.SECOND, None,       c.PLURAL,   c.GENITIVE, "validated"),
        ("τους", c.PERSONAL_WEAK, c.THIRD,  None,       c.PLURAL,   c.GENITIVE, "validated"),

        # Personal Weak Pronouns - Accusative
        ("με",  c.PERSONAL_WEAK, c.FIRST,  None,       c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("σε",  c.PERSONAL_WEAK, c.SECOND, None,       c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("τον", c.PERSONAL_WEAK, c.THIRD,  c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("την", c.PERSONAL_WEAK, c.THIRD,  c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("το",  c.PERSONAL_WEAK, c.THIRD,  c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated"),
        ("μας", c.PERSONAL_WEAK, c.FIRST,  None,       c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("σας", c.PERSONAL_WEAK, c.SECOND, None,       c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("τους",c.PERSONAL_WEAK, c.THIRD,  c.MASCULINE, c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("τις", c.PERSONAL_WEAK, c.THIRD,  c.FEMININE,  c.PLURAL,   c.ACCUSATIVE, "validated"),
        ("τα",  c.PERSONAL_WEAK, c.THIRD,  c.NEUTER,    c.PLURAL,   c.ACCUSATIVE, "validated"),

        # Demonstrative Pronouns - sample forms
        ("τούτος",  c.DEMONSTRATIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("τούτη",   c.DEMONSTRATIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("τούτο",   c.DEMONSTRATIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εκείνος", c.DEMONSTRATIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εκείνη",  c.DEMONSTRATIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("εκείνο",  c.DEMONSTRATIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),

        # Interrogative Pronouns
        ("ποιος", c.INTERROGATIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("ποια",  c.INTERROGATIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("ποιο",  c.INTERROGATIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("τι",    c.INTERROGATIVE, None, None,       None,       None,         "validated"),
        ("πόσος", c.INTERROGATIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("πόση",  c.INTERROGATIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("πόσο",  c.INTERROGATIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),

        # Possessive Pronouns
        ("δικός", c.POSSESSIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("δική",  c.POSSESSIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("δικό",  c.POSSESSIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),

        # Indefinite Pronouns
        ("κάποιος", c.INDEFINITE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κάποια",  c.INDEFINITE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κάποιο",  c.INDEFINITE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κανείς",  c.INDEFINITE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("καμία",   c.INDEFINITE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κανένα",  c.INDEFINITE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("κάθε",    c.INDEFINITE, None, None,       None,       None,         "validated"),
        ("όλος",    c.INDEFINITE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όλη",     c.INDEFINITE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όλο",     c.INDEFINITE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("μερικοί", c.INDEFINITE, None, c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated"),
        ("μερικές", c.INDEFINITE, None, c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated"),
        ("μερικά",  c.INDEFINITE, None, c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated"),
        ("κάτι",    c.INDEFINITE, None, None,       None,       None,         "validated"),
        ("τίποτα",  c.INDEFINITE, None, None,       None,       None,         "validated"),

        # Relative Pronouns
        ("που",    c.RELATIVE, None, None,       None,       None,         "validated"),
        ("οποίος", c.RELATIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("οποία",  c.RELATIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("οποίο",  c.RELATIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όποιος", c.RELATIVE, None, c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όποια",  c.RELATIVE, None, c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated"),
        ("όποιο",  c.RELATIVE, None, c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated"),
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
