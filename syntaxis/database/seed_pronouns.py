"""Seed data for Modern Greek pronouns."""

import sqlite3


def seed_pronouns(conn: sqlite3.Connection) -> None:
    """Populate greek_pronouns table with Modern Greek pronouns.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Define pronouns by type with explicit feature combinations
    # Format: (lemma, type, person, gender, number, case_name, validation_status)
    pronouns = [
        # Personal Strong Pronouns - Nominative
        ("εγώ",   "personal_strong", "1", None, "SINGULAR", "NOMINATIVE", "validated"),
        ("εσύ",   "personal_strong", "2", None, "SINGULAR", "NOMINATIVE", "validated"),
        ("αυτός", "personal_strong", "3", "M",  "SINGULAR", "NOMINATIVE", "validated"),
        ("αυτή",  "personal_strong", "3", "F",  "SINGULAR", "NOMINATIVE", "validated"),
        ("αυτό",  "personal_strong", "3", "N",  "SINGULAR", "NOMINATIVE", "validated"),
        ("εμείς", "personal_strong", "1", None, "PLURAL",   "NOMINATIVE", "validated"),
        ("εσείς", "personal_strong", "2", None, "PLURAL",   "NOMINATIVE", "validated"),
        ("αυτοί", "personal_strong", "3", "M",  "PLURAL",   "NOMINATIVE", "validated"),
        ("αυτές", "personal_strong", "3", "F",  "PLURAL",   "NOMINATIVE", "validated"),
        ("αυτά",  "personal_strong", "3", "N",  "PLURAL",   "NOMINATIVE", "validated"),

        # Personal Weak Pronouns - Genitive
        ("μου",  "personal_weak", "1", None, "SINGULAR", "GENITIVE", "validated"),
        ("σου",  "personal_weak", "2", None, "SINGULAR", "GENITIVE", "validated"),
        ("του",  "personal_weak", "3", "M",  "SINGULAR", "GENITIVE", "validated"),
        ("της",  "personal_weak", "3", "F",  "SINGULAR", "GENITIVE", "validated"),
        ("μας",  "personal_weak", "1", None, "PLURAL",   "GENITIVE", "validated"),
        ("σας",  "personal_weak", "2", None, "PLURAL",   "GENITIVE", "validated"),
        ("τους", "personal_weak", "3", None, "PLURAL",   "GENITIVE", "validated"),

        # Personal Weak Pronouns - Accusative
        ("με",  "personal_weak", "1", None, "SINGULAR", "ACCUSATIVE", "validated"),
        ("σε",  "personal_weak", "2", None, "SINGULAR", "ACCUSATIVE", "validated"),
        ("τον", "personal_weak", "3", "M",  "SINGULAR", "ACCUSATIVE", "validated"),
        ("την", "personal_weak", "3", "F",  "SINGULAR", "ACCUSATIVE", "validated"),
        ("το",  "personal_weak", "3", "N",  "SINGULAR", "ACCUSATIVE", "validated"),
        ("μας", "personal_weak", "1", None, "PLURAL",   "ACCUSATIVE", "validated"),
        ("σας", "personal_weak", "2", None, "PLURAL",   "ACCUSATIVE", "validated"),
        ("τους","personal_weak", "3", "M",  "PLURAL",   "ACCUSATIVE", "validated"),
        ("τις", "personal_weak", "3", "F",  "PLURAL",   "ACCUSATIVE", "validated"),
        ("τα",  "personal_weak", "3", "N",  "PLURAL",   "ACCUSATIVE", "validated"),

        # Demonstrative Pronouns - sample forms
        ("τούτος",  "demonstrative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("τούτη",   "demonstrative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("τούτο",   "demonstrative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("εκείνος", "demonstrative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("εκείνη",  "demonstrative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("εκείνο",  "demonstrative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),

        # Interrogative Pronouns
        ("ποιος", "interrogative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("ποια",  "interrogative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("ποιο",  "interrogative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("τι",    "interrogative", None, None, None, None, "validated"),
        ("πόσος", "interrogative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("πόση",  "interrogative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("πόσο",  "interrogative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),

        # Possessive Pronouns
        ("δικός", "possessive", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("δική",  "possessive", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("δικό",  "possessive", None, "N", "SINGULAR", "NOMINATIVE", "validated"),

        # Indefinite Pronouns
        ("κάποιος", "indefinite", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("κάποια",  "indefinite", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("κάποιο",  "indefinite", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("κανείς",  "indefinite", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("καμία",   "indefinite", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("κανένα",  "indefinite", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("κάθε",    "indefinite", None, None, None, None, "validated"),
        ("όλος",    "indefinite", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("όλη",     "indefinite", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("όλο",     "indefinite", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("μερικοί", "indefinite", None, "M", "PLURAL", "NOMINATIVE", "validated"),
        ("μερικές", "indefinite", None, "F", "PLURAL", "NOMINATIVE", "validated"),
        ("μερικά",  "indefinite", None, "N", "PLURAL", "NOMINATIVE", "validated"),
        ("κάτι",    "indefinite", None, None, None, None, "validated"),
        ("τίποτα",  "indefinite", None, None, None, None, "validated"),

        # Relative Pronouns
        ("που",    "relative", None, None, None, None, "validated"),
        ("οποίος", "relative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("οποία",  "relative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("οποίο",  "relative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
        ("όποιος", "relative", None, "M", "SINGULAR", "NOMINATIVE", "validated"),
        ("όποια",  "relative", None, "F", "SINGULAR", "NOMINATIVE", "validated"),
        ("όποιο",  "relative", None, "N", "SINGULAR", "NOMINATIVE", "validated"),
    ]

    # Insert pronouns
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_pronouns
        (lemma, type, person, gender, number, case_name, validation_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        pronouns
    )

    conn.commit()
    print(f"Seeded {cursor.rowcount} pronoun forms into greek_pronouns table")
