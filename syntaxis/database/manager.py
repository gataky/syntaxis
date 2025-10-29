import sqlite3

from syntaxis.database.schema import create_schema
from syntaxis.models.enums import PartOfSpeech


class LexicalManager:
    """Manages vocabulary storage and retrieval for sentence generation.

    The lexical manager maintains vocabulary in a SQLite database and provides
    methods to query and retrieve words based on required features.
    """

    def __init__(self, db_path: str | None = None):
        """Initialize the lexical manager with SQLite backend.

        Args:
            db_path: Path to SQLite database file. If None, creates in-memory database.
        """
        self._db_path = db_path

        if db_path is None:
            self._conn = sqlite3.connect(":memory:")
        else:
            self._conn = sqlite3.connect(db_path)

        create_schema(self._conn)
        self._morphology_adapter = None

    # Storage methods
    # Random selection methods

    def get_random_word(self, pos: PartOfSpeech, **features) -> object | None:
        """Get a random word of the specified part of speech.

        Args:
            pos: Part of speech
            **features: Optional filtering features (gender, case, tense, etc.)

        Returns:
            Random word object matching criteria, or None if no matches
        """
        return None

    # Helper methods

    def count_total_words(self) -> int:
        """Return the total number of words in the lexicon."""
        cursor = self._conn.cursor()
        _ = cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM greek_nouns) +
                (SELECT COUNT(*) FROM greek_verbs) +
                (SELECT COUNT(*) FROM greek_adjectives) +
                (SELECT COUNT(*) FROM greek_articles) +
                (SELECT COUNT(*) FROM greek_pronouns) +
                (SELECT COUNT(*) FROM greek_prepositions) +
                (SELECT COUNT(*) FROM greek_conjunctions) +
                (SELECT COUNT(*) FROM greek_adverbs)
        """
        )
        return cursor.fetchone()[0]

    # Reverse lookup methods

    def get_words_by_english(
        self, english_word: str, pos: PartOfSpeech | None = None
    ) -> list:
        """Find all Greek words that translate to the given English word.

        Args:
            english_word: English word to search for
            pos: Optional filter by part of speech

        Returns:
            List of Word objects (mixed types) with english_translations populated
        """
        cursor = self._conn.cursor()

        # First find the english_word_id(s)
        if pos is not None:
            _ = cursor.execute(
                "SELECT id, pos_type FROM english_words WHERE word = ? AND pos_type = ?",
                (english_word, pos.name),
            )
        else:
            _ = cursor.execute(
                "SELECT id, pos_type FROM english_words WHERE word = ?", (english_word,)
            )

        english_entries = cursor.fetchall()
        if not english_entries:
            return []

        results = []

        for english_word_id, pos_type in english_entries:
            pos_enum = PartOfSpeech[pos_type]

            # Get Greek words for this English word and POS
            _ = cursor.execute(
                """
                SELECT greek_word_id FROM translations
                WHERE english_word_id = ? AND greek_pos_type = ?
                """,
                (english_word_id, pos_type),
            )
            greek_word_ids = [row[0] for row in cursor.fetchall()]

            # Retrieve each Greek word using existing get methods
            for greek_word_id in greek_word_ids:
                word_obj = self._get_word_by_id(greek_word_id, pos_enum)
                if word_obj:
                    results.append(word_obj)

        return results

    def _get_word_by_id(self, word_id: int, pos: PartOfSpeech):
        """Helper to retrieve a word by its database ID and POS.

        Args:
            word_id: Database ID of the Greek word
            pos: Part of speech

        Returns:
            Word object or None if not found
        """
        _ = self._conn.cursor()
        return None
