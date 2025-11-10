"""Database schema for SQLite-backed lexical storage."""

import sqlite3


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all tables for lexical storage.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # English words table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS english_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word     TEXT NOT NULL,
            pos_type TEXT NOT NULL
        )
    """
    )

    # Greek nouns table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_nouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL,
            gender TEXT NOT NULL,
            number TEXT NOT NULL,
            case_name TEXT NOT NULL,
            validation_status TEXT NOT NULL,
            UNIQUE(lemma, gender, number, case_name)
        )
    """
    )

    # Greek verbs table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_verbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL,
            verb_group TEXT,
            tense TEXT,
            voice TEXT,
            mood TEXT,
            number TEXT,
            person TEXT,
            case_name TEXT,
            validation_status TEXT NOT NULL,
            UNIQUE(lemma, verb_group, tense, voice, mood, number, person, case_name)
        )
    """
    )

    # Greek adjectives table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_adjectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL,
            gender TEXT,
            number TEXT,
            case_name TEXT,
            validation_status TEXT NOT NULL,
            UNIQUE(lemma, gender, number, case_name)
        )
    """
    )

    # Greek articles table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL,
            gender TEXT,
            number TEXT,
            case_name TEXT,
            validation_status TEXT NOT NULL,
            UNIQUE(lemma, gender, number, case_name)
        )
    """
    )

    # Greek pronouns table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_pronouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL,
            type TEXT NOT NULL,
            person TEXT,
            gender TEXT,
            number TEXT,
            case_name TEXT,
            validation_status TEXT NOT NULL,
            UNIQUE(lemma, type, person, gender, number, case_name)
        )
    """
    )

    # Greek prepositions table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_prepositions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek conjunctions table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_conjunctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek adverbs table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_adverbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Translation junction table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english_word_id INTEGER NOT NULL,
            greek_lemma TEXT NOT NULL,
            greek_pos_type TEXT NOT NULL,
            FOREIGN KEY (english_word_id) REFERENCES english_words(id),
            UNIQUE(english_word_id, greek_lemma, greek_pos_type)
        )
    """
    )

    conn.commit()
