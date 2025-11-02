import sqlite3
from typing import Any

from syntaxis.database.bitmasks import (
    POS_TO_TABLE_MAP,
    VALID_FEATURES,
    enum_to_bit,
)
from syntaxis.database.mask_calculator import calculate_masks_for_word, STRING_TO_ENUM
from syntaxis.database.schema import create_schema
from syntaxis.models.enums import PartOfSpeech
from syntaxis.models.part_of_speech import PartOfSpeech as PartOfSpeechBase
from syntaxis.morpheus import Morpheus


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
        self, pos: PartOfSpeech, **features: Any
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
                f"Invalid features {invalid_features} for {pos.name}. "
                + f"Valid features are: {valid_features}"
            )

        cursor = self._conn.cursor()
        table = POS_TO_TABLE_MAP[pos]

        # Dynamically build WHERE conditions for each feature using bitmasks.
        # This allows filtering words that have the required features.
        # For example, `(g.number_mask & 1) != 0` checks for SINGULAR.
        conditions = []
        params: list[str | int] = [pos.name]  # For JOIN condition

        for feature_name, feature_value in features.items():
            bit = enum_to_bit(feature_value)
            conditions.append(f"(g.{feature_name}_mask & ?) != 0")
            params.append(bit)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # A single query retrieves a random word and all its translations.
        # - LEFT JOINs ensure that words are returned even if they have no translations.
        # - GROUP_CONCAT aggregates multiple translation rows into a single pipe-delimited string.
        # - ORDER BY RANDOM() LIMIT 1 provides efficient random selection.
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
        results = []
        pos_to_check = [pos] if pos else list(POS_TO_TABLE_MAP.keys())

        for pos_enum in pos_to_check:
            if pos_enum not in POS_TO_TABLE_MAP:
                continue

            table = POS_TO_TABLE_MAP[pos_enum]
            query = f"""
                SELECT
                    g.id,
                    g.lemma,
                    GROUP_CONCAT(e_all.word, '|') as translations
                FROM {table} g
                JOIN translations t ON t.greek_word_id = g.id AND t.greek_pos_type = ?
                JOIN english_words e ON e.id = t.english_word_id
                LEFT JOIN translations t_all ON t_all.greek_word_id = g.id AND t_all.greek_pos_type = ?
                LEFT JOIN english_words e_all ON e_all.id = t_all.english_word_id
                WHERE e.word = ?
                GROUP BY g.id, g.lemma
            """
            cursor = self._conn.cursor()
            rows = cursor.execute(
                query, (pos_enum.name, pos_enum.name, english_word)
            ).fetchall()
            for row in rows:
                results.append(self._create_word_from_row(row, pos_enum))

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
        self, row: sqlite3.Row, pos: PartOfSpeech
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

    POS_CONFIG = {
        PartOfSpeech.NOUN: {
            "table": "greek_nouns",
            "fields": [
                "lemma",
                "gender",
                "number_mask",
                "case_mask",
                "validation_status",
            ],
        },
        PartOfSpeech.VERB: {
            "table": "greek_verbs",
            "fields": [
                "lemma",
                "verb_group",
                "tense_mask",
                "voice_mask",
                "mood_mask",
                "number_mask",
                "person_mask",
                "case_mask",
                "validation_status",
            ],
        },
        PartOfSpeech.ADJECTIVE: {
            "table": "greek_adjectives",
            "fields": ["lemma", "number_mask", "case_mask", "validation_status"],
        },
        PartOfSpeech.ARTICLE: {
            "table": "greek_articles",
            "fields": [
                "lemma",
                "gender_mask",
                "number_mask",
                "case_mask",
                "validation_status",
            ],
        },
        PartOfSpeech.PRONOUN: {
            "table": "greek_pronouns",
            "fields": [
                "lemma",
                "gender_mask",
                "number_mask",
                "case_mask",
                "validation_status",
            ],
        },
        PartOfSpeech.ADVERB: {
            "table": "greek_adverbs",
            "fields": ["lemma", "validation_status"],
        },
        PartOfSpeech.PREPOSITION: {
            "table": "greek_prepositions",
            "fields": ["lemma", "validation_status"],
        },
        PartOfSpeech.CONJUNCTION: {
            "table": "greek_conjunctions",
            "fields": ["lemma", "validation_status"],
        },
    }

    def _validate_and_prepare_lemma(
        self, lemma: str, pos: PartOfSpeech, translations: list[str]
    ) -> PartOfSpeechBase:
        """Validate inputs and use Morpheus to create a word object."""
        if not lemma:
            raise ValueError("Lemma cannot be empty")
        if not translations:
            raise ValueError("At least one translation required")

        table = POS_TO_TABLE_MAP[pos]
        cursor = self._conn.cursor()
        existing = cursor.execute(
            f"SELECT id FROM {table} WHERE lemma = ?", (lemma,)
        ).fetchone()
        if existing:
            raise ValueError(f"Word '{lemma}' already exists as {pos.name}")

        try:
            word = Morpheus.create(lemma, pos)
        except Exception as e:
            raise ValueError(f"Failed to generate forms for '{lemma}': {e}")

        if not word.forms:
            raise ValueError(f"Morpheus generated no forms for '{lemma}'")

        return word

    def _prepare_database_values(
        self, lemma: str, pos: PartOfSpeech, word: PartOfSpeechBase
    ) -> dict[str, Any]:
        """Calculate masks and prepare a dictionary of values for DB insertion."""
        masks = calculate_masks_for_word(lemma, pos)
        config = self.POS_CONFIG[pos]
        fields = config["fields"]

        values: dict[str, str | int | None] = {
            "lemma": lemma,
            "validation_status": "VALID",
        }

        if pos == PartOfSpeech.NOUN:
            gender_key = next(iter(word.forms.keys()))
            gender_enum = STRING_TO_ENUM.get(gender_key)
            if gender_enum:
                values["gender"] = gender_enum.name
        elif pos == PartOfSpeech.VERB:
            values["verb_group"] = getattr(word, "verb_group", None)

        for field in fields:
            if field.endswith("_mask") and field in masks:
                values[field] = masks[field]
            elif field.endswith("_mask") and field not in values:
                values[field] = 0

        return values

    def _execute_add_word_transaction(
        self, pos: PartOfSpeech, values: dict[str, Any], translations: list[str]
    ) -> int:
        """Execute the database transaction to add a word and its translations."""
        table = POS_TO_TABLE_MAP[pos]
        config = self.POS_CONFIG[pos]
        fields = config["fields"]
        cursor = self._conn.cursor()

        try:
            # Step 1: Insert Greek word
            columns = ", ".join(fields)
            placeholders = ", ".join(["?"] * len(fields))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, [values.get(field) for field in fields])
            greek_word_id = cursor.lastrowid
            if not greek_word_id:
                raise sqlite3.Error("Failed to insert Greek word, no row ID returned.")

            # Step 2: Insert/retrieve English words and create links
            english_word_ids = []
            for translation in translations:
                translation = translation.strip()
                cursor.execute(
                    "INSERT OR IGNORE INTO english_words (word, pos_type) VALUES (?, ?)",
                    (translation, pos.name),
                )
                eng_id_row = cursor.execute(
                    "SELECT id FROM english_words WHERE word = ? AND pos_type = ?",
                    (translation, pos.name),
                ).fetchone()
                if eng_id_row:
                    english_word_ids.append(eng_id_row[0])

            # Step 3: Create translation links
            for eng_id in english_word_ids:
                cursor.execute(
                    "INSERT INTO translations (english_word_id, greek_word_id, greek_pos_type) VALUES (?, ?, ?)",
                    (eng_id, greek_word_id, pos.name),
                )

            self._conn.commit()
            return greek_word_id

        except Exception:
            self._conn.rollback()
            raise

    def add_word(
        self, lemma: str, translations: list[str], pos: PartOfSpeech
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
        word = self._validate_and_prepare_lemma(lemma, pos, translations)
        values = self._prepare_database_values(lemma, pos, word)
        greek_word_id = self._execute_add_word_transaction(pos, values, translations)

        new_word = self._get_word_by_id(greek_word_id, pos)
        if not new_word:
            # This should not happen if transaction was successful
            raise RuntimeError(f"Failed to retrieve newly added word '{lemma}'")
        return new_word
