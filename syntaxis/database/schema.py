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
            word TEXT NOT NULL UNIQUE,
            pos_type TEXT NOT NULL
        )
    """
    )

    # Greek nouns table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_nouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            gender TEXT NOT NULL,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek verbs table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_verbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            verb_group TEXT,
            tense_mask INTEGER,
            voice_mask INTEGER,
            mood_mask INTEGER,
            number_mask INTEGER,
            person_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek adjectives table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_adjectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek articles table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            gender_mask INTEGER,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
        )
    """
    )

    # Greek pronouns table
    _ = cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS greek_pronouns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lemma TEXT NOT NULL UNIQUE,
            person TEXT,
            gender_mask INTEGER,
            number_mask INTEGER,
            case_mask INTEGER,
            validation_status TEXT NOT NULL
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
            greek_word_id INTEGER NOT NULL,
            greek_pos_type TEXT NOT NULL,
            FOREIGN KEY (english_word_id) REFERENCES english_words(id),
            UNIQUE(english_word_id, greek_word_id, greek_pos_type)
        )
    """
    )

    conn.commit()
