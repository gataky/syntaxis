import sqlite3
from typing import Any

from syntaxis.database.mask_calculator import calculate_masks_for_word
from syntaxis.database.schema import create_schema
from syntaxis.models.enums import PartOfSpeech
from syntaxis.morpheus import Morpheus
from syntaxis.models.part_of_speech import PartOfSpeech as PartOfSpeechBase
from syntaxis.database.bitmasks import (
    enum_to_bit,
    VALID_FEATURES,
    POS_TO_TABLE_MAP,
)


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

        self._conn.row_factory = sqlite3.Row  # Enable column access by name
        create_schema(self._conn)
        self._morphology_adapter = None

    # Storage methods
    # Random selection methods

    def get_random_word(
        self,
        pos: PartOfSpeech,
        **features: Any
    ) -> PartOfSpeechBase | None:
        """Get a random word of the specified part of speech.

        Args:
            pos: Part of speech enum (PartOfSpeech.NOUN, PartOfSpeech.VERB, etc.)
            **features: Feature filters as enum values
                        (gender=Gender.MASCULINE, case=Case.NOMINATIVE, etc.)

        Returns:
            Instance of appropriate PartOfSpeech subclass with forms and
            translations, or None if no matches

        Raises:
            ValueError: If invalid features provided for the POS type

        Examples:
            >>> manager.get_random_word(PartOfSpeech.NOUN, number=Number.SINGULAR)
            Noun(lemma="άνθρωπος", ...)
        """
        # Validate features
        valid_features = VALID_FEATURES.get(pos, set())
        invalid_features = set(features.keys()) - valid_features

        if invalid_features:
            raise ValueError(
                f"Invalid features {invalid_features} for {pos.name}. " +
                f"Valid features are: {valid_features}"
            )

        cursor = self._conn.cursor()
        table = POS_TO_TABLE_MAP[pos]

        # Build WHERE conditions for bitmask features
        conditions = []
        params: list[str | int] = [pos.name]  # For JOIN condition

        for feature_name, feature_value in features.items():
            bit = enum_to_bit(feature_value)
            conditions.append(f"(g.{feature_name}_mask & ?) != 0")
            params.append(bit)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Single query with JOIN to get lemma and translations
        query = f"""
            SELECT
                g.id,
                g.lemma,
                GROUP_CONCAT(e.word, '|') as translations
            FROM {table} g
            LEFT JOIN translations t ON t.greek_word_id = g.id
                AND t.greek_pos_type = ?
            LEFT JOIN english_words e ON e.id = t.english_word_id
            WHERE {where_clause}
            GROUP BY g.id
            ORDER BY RANDOM()
            LIMIT 1
        """

        row = cursor.execute(query, params).fetchone()
        if not row:
            return None

        return self._create_word_from_row(row, pos)

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
        cursor = self._conn.cursor()
        table = POS_TO_TABLE_MAP[pos]

        # Query with JOIN to get lemma and translations
        query = f"""
            SELECT
                g.id,
                g.lemma,
                GROUP_CONCAT(e.word, '|') as translations
            FROM {table} g
            LEFT JOIN translations t ON t.greek_word_id = g.id
                AND t.greek_pos_type = ?
            LEFT JOIN english_words e ON e.id = t.english_word_id
            WHERE g.id = ?
            GROUP BY g.id
        """

        row = cursor.execute(query, (pos.name, word_id)).fetchone()
        if not row:
            return None

        return self._create_word_from_row(row, pos)

    def _create_word_from_row(
        self,
        row: sqlite3.Row,
        pos: PartOfSpeech
    ) -> PartOfSpeechBase:
        """Create PartOfSpeech object with translations from query result.

        Args:
            row: Database row with id, lemma, and translations columns
            pos: Part of speech enum

        Returns:
            Complete PartOfSpeech object with forms and translations
        """
        lemma = row["lemma"]
        translations_str = row["translations"]

        # Parse translations (GROUP_CONCAT returns pipe-delimited string)
        translations = translations_str.split("|") if translations_str else None

        # Create word with inflected forms using Morpheus
        word = Morpheus.create(lemma, pos)
        word.translations = translations

        return word


    def add_word(
        self,
        lemma: str,
        translations: list[str],
        pos: PartOfSpeech
    ) -> PartOfSpeechBase:
        """Add a word to the lexicon with automatic mask calculation.

        Args:
            lemma: Greek word in its base form
            translations: List of English translations (at least one required)
            pos: Part of speech enum

        Returns:
            Complete PartOfSpeech object with forms and translations

        Raises:
            ValueError: If translations empty, lemma empty, word exists, or Morpheus fails
        """
        # Validate lemma
        if not lemma:
            raise ValueError("Lemma cannot be empty")
        # Validate translations
        if not translations:
            raise ValueError("At least one translation required")

        # Check for duplicates
        table = POS_TO_TABLE_MAP[pos]
        cursor = self._conn.cursor()
        existing = cursor.execute(
            f"SELECT id FROM {table} WHERE lemma = ?",
            (lemma,)
        ).fetchone()
        if existing:
            raise ValueError(f"Word '{lemma}' already exists as {pos.name}")

        # Generate forms with Morpheus
        try:
            word = Morpheus.create(lemma, pos)
        except Exception as e:
            raise ValueError(f"Failed to generate forms for '{lemma}': {e}")

        if not word.forms:
            raise ValueError(f"Morpheus generated no forms for '{lemma}'")

        validation_status = "VALID"

        # Calculate masks
        masks = calculate_masks_for_word(lemma, pos)

        # Infer POS-specific fields
        pos_fields = {}

        if pos == PartOfSpeech.NOUN:
            # Infer gender from forms structure: forms[gender][number][case]
            # Map from mask_calculator's STRING_TO_ENUM
            from syntaxis.database.mask_calculator import STRING_TO_ENUM
            gender_key = next(iter(word.forms.keys()))
            gender_enum = STRING_TO_ENUM.get(gender_key)
            if gender_enum:
                pos_fields['gender'] = gender_enum.name
        elif pos == PartOfSpeech.VERB:
            # Check if word has verb_group attribute
            verb_group = getattr(word, 'verb_group', None)
            pos_fields['verb_group'] = verb_group

        # Insert into database (transactional)
        try:
            # Step 1: Insert Greek word
            if pos == PartOfSpeech.NOUN:
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, gender, number_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (lemma, pos_fields['gender'], masks.get('number_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos == PartOfSpeech.VERB:
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, verb_group, tense_mask, voice_mask, mood_mask,
                     number_mask, person_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (lemma, pos_fields.get('verb_group'), masks.get('tense_mask', 0),
                     masks.get('voice_mask', 0), masks.get('mood_mask', 0),
                     masks.get('number_mask', 0), masks.get('person_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos == PartOfSpeech.ADJECTIVE:
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, number_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (lemma, masks.get('number_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos in (PartOfSpeech.ARTICLE, PartOfSpeech.PRONOUN):
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, gender_mask, number_mask, case_mask, validation_status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (lemma, masks.get('gender_mask', 0), masks.get('number_mask', 0),
                     masks.get('case_mask', 0), validation_status)
                )
            elif pos in (PartOfSpeech.ADVERB, PartOfSpeech.PREPOSITION, PartOfSpeech.CONJUNCTION):
                cursor.execute(
                    f"""
                    INSERT INTO {table}
                    (lemma, validation_status)
                    VALUES (?, ?)
                    """,
                    (lemma, validation_status)
                )

            greek_word_id = cursor.lastrowid

            # Step 2: Insert/retrieve English words
            english_word_ids = []
            for translation in translations:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO english_words (word, pos_type)
                    VALUES (?, ?)
                    """,
                    (translation, pos.name)
                )

                eng_id = cursor.execute(
                    """
                    SELECT id FROM english_words WHERE word = ? AND pos_type = ?
                    """,
                    (translation, pos.name)
                ).fetchone()[0]

                english_word_ids.append(eng_id)

            # Step 3: Create translation links
            for eng_id in english_word_ids:
                cursor.execute(
                    """
                    INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type)
                    VALUES (?, ?, ?)
                    """,
                    (eng_id, greek_word_id, pos.name)
                )

            self._conn.commit()

            # Step 4: Build and return Word object
            # Query back the complete row to get proper sqlite3.Row
            row = cursor.execute(
                f"""
                SELECT
                    g.id,
                    g.lemma,
                    GROUP_CONCAT(e.word, '|') as translations
                FROM {table} g
                LEFT JOIN translations t ON t.greek_word_id = g.id
                    AND t.greek_pos_type = ?
                LEFT JOIN english_words e ON e.id = t.english_word_id
                WHERE g.id = ?
                GROUP BY g.id
                """,
                (pos.name, greek_word_id)
            ).fetchone()

            return self._create_word_from_row(row, pos)

        except Exception:
            self._conn.rollback()
            raise
