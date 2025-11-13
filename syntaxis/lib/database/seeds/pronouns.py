"""Seed data for Modern Greek pronouns."""

import sqlite3

from syntaxis.lib import constants as c


def seed(conn: sqlite3.Connection) -> None:
    """Populate greek_pronouns table with Modern Greek pronouns and their translations.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Format: (lemma, type, person, gender, number, case, validation_status, [english_translations])
    pronouns_with_translations = [
        # Personal Strong Pronouns - Nominative
        ( "εγώ",     c.PERSONAL_STRONG, c.FIRST,  None,        c.SINGULAR, c.NOMINATIVE, "validated", ["I"]),
        ( "εσύ",     c.PERSONAL_STRONG, c.SECOND, None,        c.SINGULAR, c.NOMINATIVE, "validated", ["you"]),
        ( "αυτός",   c.PERSONAL_STRONG, c.THIRD,  c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["he", "it"]),
        ( "αυτή",    c.PERSONAL_STRONG, c.THIRD,  c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["she", "it"]),
        ( "αυτό",    c.PERSONAL_STRONG, c.THIRD,  c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["it"]),
        ( "εμείς",   c.PERSONAL_STRONG, c.FIRST,  None,        c.PLURAL,   c.NOMINATIVE, "validated", ["we"]),
        ( "εσείς",   c.PERSONAL_STRONG, c.SECOND, None,        c.PLURAL,   c.NOMINATIVE, "validated", ["you"]),
        ( "αυτοί",   c.PERSONAL_STRONG, c.THIRD,  c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated", ["they"]),
        ( "αυτές",   c.PERSONAL_STRONG, c.THIRD,  c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated", ["they"]),
        ( "αυτά",    c.PERSONAL_STRONG, c.THIRD,  c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated", ["they"]),
        # Personal Weak Pronouns - Genitive
        ( "μου",     c.PERSONAL_WEAK,   c.FIRST,  None,        c.SINGULAR, c.GENITIVE,   "validated", ["me", "my"]),
        ( "σου",     c.PERSONAL_WEAK,   c.SECOND, None,        c.SINGULAR, c.GENITIVE,   "validated", ["you", "your"]),
        ( "του",     c.PERSONAL_WEAK,   c.THIRD,  c.MASCULINE, c.SINGULAR, c.GENITIVE,   "validated", ["him", "his", "it"]),
        ( "της",     c.PERSONAL_WEAK,   c.THIRD,  c.FEMININE,  c.SINGULAR, c.GENITIVE,   "validated", ["her", "hers", "it"]),
        ( "μας",     c.PERSONAL_WEAK,   c.FIRST,  None,        c.PLURAL,   c.GENITIVE,   "validated", ["us", "our"]),
        ( "σας",     c.PERSONAL_WEAK,   c.SECOND, None,        c.PLURAL,   c.GENITIVE,   "validated", ["you", "your"]),
        ( "τους",    c.PERSONAL_WEAK,   c.THIRD,  None,        c.PLURAL,   c.GENITIVE,   "validated", ["them", "their"]),
        # Personal Weak Pronouns - Accusative
        ( "με",      c.PERSONAL_WEAK,   c.FIRST,  None,        c.SINGULAR, c.ACCUSATIVE, "validated", ["me"]),
        ( "σε",      c.PERSONAL_WEAK,   c.SECOND, None,        c.SINGULAR, c.ACCUSATIVE, "validated", ["you"]),
        ( "τον",     c.PERSONAL_WEAK,   c.THIRD,  c.MASCULINE, c.SINGULAR, c.ACCUSATIVE, "validated", ["him", "it"]),
        ( "την",     c.PERSONAL_WEAK,   c.THIRD,  c.FEMININE,  c.SINGULAR, c.ACCUSATIVE, "validated", ["her", "it"]),
        ( "το",      c.PERSONAL_WEAK,   c.THIRD,  c.NEUTER,    c.SINGULAR, c.ACCUSATIVE, "validated", ["it"]),
        ( "μας",     c.PERSONAL_WEAK,   c.FIRST,  None,        c.PLURAL,   c.ACCUSATIVE, "validated", ["us"]),
        ( "σας",     c.PERSONAL_WEAK,   c.SECOND, None,        c.PLURAL,   c.ACCUSATIVE, "validated", ["you"]),
        ( "τους",    c.PERSONAL_WEAK,   c.THIRD,  c.MASCULINE, c.PLURAL,   c.ACCUSATIVE, "validated", ["them"]),
        ( "τις",     c.PERSONAL_WEAK,   c.THIRD,  c.FEMININE,  c.PLURAL,   c.ACCUSATIVE, "validated", ["them"]),
        ( "τα",      c.PERSONAL_WEAK,   c.THIRD,  c.NEUTER,    c.PLURAL,   c.ACCUSATIVE, "validated", ["them"]),
        # Demonstrative Pronouns - sample forms
        ( "τούτος",  c.DEMONSTRATIVE,   None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["this"]),
        ( "τούτη",   c.DEMONSTRATIVE,   None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["this"]),
        ( "τούτο",   c.DEMONSTRATIVE,   None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["this"]),
        ( "εκείνος", c.DEMONSTRATIVE,   None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["that"]),
        ( "εκείνη",  c.DEMONSTRATIVE,   None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["that"]),
        ( "εκείνο",  c.DEMONSTRATIVE,   None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["that"]),
        # Interrogative Pronouns
        ( "ποιος",   c.INTERROGATIVE,   None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["who", "which"]),
        ( "ποια",    c.INTERROGATIVE,   None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["who", "which"]),
        ( "ποιο",    c.INTERROGATIVE,   None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["who", "which"]),
        ( "πόσος",   c.INTERROGATIVE,   None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["how much", "how many"]),
        ( "πόση",    c.INTERROGATIVE,   None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["how much", "how many"]),
        ( "πόσο",    c.INTERROGATIVE,   None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["how much", "how many"]),
        ( "τι",      c.INTERROGATIVE,   None,     None,        None,       None,         "validated", ["what"]),
        # Possessive Pronouns
        ( "δικός",   c.POSSESSIVE,      None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["own"]),
        ( "δική",    c.POSSESSIVE,      None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["own"]),
        ( "δικό",    c.POSSESSIVE,      None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["own"]),
        # Indefinite Pronouns
        ( "κάποιος", c.INDEFINITE,      None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["someone"]),
        ( "κάποια",  c.INDEFINITE,      None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["someone"]),
        ( "κάποιο",  c.INDEFINITE,      None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["someone"]),
        ( "κανείς",  c.INDEFINITE,      None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["anyone", "no one"]),
        ( "καμία",   c.INDEFINITE,      None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["anyone", "no one"]),
        ( "κανένα",  c.INDEFINITE,      None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["anyone", "no one"]),
        ( "όλος",    c.INDEFINITE,      None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["all", "whole"]),
        ( "όλη",     c.INDEFINITE,      None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["all", "whole"]),
        ( "όλο",     c.INDEFINITE,      None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["all", "whole"]),
        ( "μερικοί", c.INDEFINITE,      None,     c.MASCULINE, c.PLURAL,   c.NOMINATIVE, "validated", ["some"]),
        ( "μερικές", c.INDEFINITE,      None,     c.FEMININE,  c.PLURAL,   c.NOMINATIVE, "validated", ["some"]),
        ( "μερικά",  c.INDEFINITE,      None,     c.NEUTER,    c.PLURAL,   c.NOMINATIVE, "validated", ["some"]),
        ( "κάτι",    c.INDEFINITE,      None,     None,        None,       None,         "validated", ["something"]),
        ( "τίποτα",  c.INDEFINITE,      None,     None,        None,       None,         "validated", ["nothing",  "anything"]),
        # Relative Pronouns
        ( "που",     c.RELATIVE,        None,     None,        None,       None,         "validated", ["that", "who", "which"]),
        ( "οποίος",  c.RELATIVE,        None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["who", "which"]),
        ( "οποία",   c.RELATIVE,        None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["who", "which"]),
        ( "οποίο",   c.RELATIVE,        None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["who", "which"]),
        ( "όποιος",  c.RELATIVE,        None,     c.MASCULINE, c.SINGULAR, c.NOMINATIVE, "validated", ["whoever",  "whichever"]),
        ( "όποια",   c.RELATIVE,        None,     c.FEMININE,  c.SINGULAR, c.NOMINATIVE, "validated", ["whoever",  "whichever"]),
        ( "όποιο",   c.RELATIVE,        None,     c.NEUTER,    c.SINGULAR, c.NOMINATIVE, "validated", ["whoever",  "whichever"]),
    ]

    # Extract pronoun data for greek_pronouns table
    pronouns = [p[:-1] for p in pronouns_with_translations]

    # Insert pronouns
    cursor.executemany(
        """
        INSERT OR IGNORE INTO greek_pronouns
        (lemma, type, person, gender, number, [case], validation_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        pronouns,
    )
    print(f"Seeded {cursor.rowcount} pronoun forms into greek_pronouns table")

    # Seed translations
    for lemma, _, _, _, _, _, _, english_words in pronouns_with_translations:
        for english_word in english_words:
            # Insert English word
            cursor.execute(
                "INSERT OR IGNORE INTO english_words (word, lexical) VALUES (?, ?)",
                (english_word, c.PRONOUN),
            )
            # Get English word ID
            eng_id_row = cursor.execute(
                "SELECT id FROM english_words WHERE word = ? AND lexical = ?",
                (english_word, c.PRONOUN),
            ).fetchone()
            if eng_id_row:
                eng_id = eng_id_row[0]
                # Insert translation link
                cursor.execute(
                    "INSERT OR IGNORE INTO translations (english_word_id, greek_lemma, greek_lexical) VALUES (?, ?, ?)",
                    (eng_id, lemma, c.PRONOUN),
                )

    conn.commit()
    print("Seeded pronoun translations.")
