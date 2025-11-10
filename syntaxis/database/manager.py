import sqlite3
from typing import Any

from syntaxis.database.bitmasks import POS_TO_TABLE_MAP, VALID_FEATURES
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
                        (gender=Gender.MASCULINE, case_name=Case.NOMINATIVE, etc.)

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

        # Build WHERE conditions using direct column comparisons
        conditions = []
        params: list[str] = [pos.name]  # For JOIN condition

        for feature_name, feature_value in features.items():
            # Convert enum to string (e.g., Number.SINGULAR -> "SINGULAR")
            feature_str = feature_value.name
            conditions.append(f"g.{feature_name} = ?")
            params.append(feature_str)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Query with DISTINCT to handle multiple rows per lemma
        query = f"""
            SELECT DISTINCT
                g.lemma,
                GROUP_CONCAT(e.word, '|') as translations
            FROM {table} g
            LEFT JOIN translations t ON t.greek_lemma = g.lemma
                AND t.greek_pos_type = ?
            LEFT JOIN english_words e ON e.id = t.english_word_id
            WHERE {where_clause}
            GROUP BY g.lemma
            ORDER BY RANDOM()
            LIMIT 1
        """

        row = cursor.execute(query, params).fetchone()
        if not row:
            return None

        word = self._create_word_from_row(row, pos)
        return word

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
                SELECT DISTINCT
                    g.lemma,
                    GROUP_CONCAT(e_all.word, '|') as translations
                FROM {table} g
                JOIN translations t ON t.greek_lemma = g.lemma AND t.greek_pos_type = ?
                JOIN english_words e ON e.id = t.english_word_id
                LEFT JOIN translations t_all ON t_all.greek_lemma = g.lemma AND t_all.greek_pos_type = ?
                LEFT JOIN english_words e_all ON e_all.id = t_all.english_word_id
                WHERE e.word = ?
                GROUP BY g.lemma
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

    def _get_word_by_lemma(self, lemma: str, pos: PartOfSpeech):
        """Helper to retrieve a word by its lemma and POS.

        Args:
            lemma: Greek word lemma
            pos: Part of speech

        Returns:
            Word object or None if not found
        """
        cursor = self._conn.cursor()
        table = POS_TO_TABLE_MAP[pos]

        # Query with JOIN to get lemma and translations
        query = f"""
            SELECT DISTINCT
                g.lemma,
                GROUP_CONCAT(e.word, '|') as translations
            FROM {table} g
            LEFT JOIN translations t ON t.greek_lemma = g.lemma
                AND t.greek_pos_type = ?
            LEFT JOIN english_words e ON e.id = t.english_word_id
            WHERE g.lemma = ?
            GROUP BY g.lemma
        """

        row = cursor.execute(query, (pos.name, lemma)).fetchone()
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

    def _extract_noun_features(self, word: PartOfSpeechBase) -> list[dict[str, str | None]]:
        """Extract feature combinations for nouns.

        Args:
            word: Noun with forms structure {gender: {number: {case: form}}}

        Returns:
            List of feature dictionaries
        """
        features_list = []
        for gender, number_dict in word.forms.items():
            for number, case_dict in number_dict.items():
                for case_name, form in case_dict.items():
                    if form:  # Only if form exists
                        features_list.append({
                            "gender": gender,
                            "number": number,
                            "case_name": case_name,
                        })
        return features_list

    def _extract_verb_features(self, word: PartOfSpeechBase) -> list[dict[str, str | None]]:
        """Extract feature combinations for verbs.

        Args:
            word: Verb with forms structure {tense: {voice: {mood: {number: {person: form}}}}}

        Returns:
            List of feature dictionaries
        """
        features_list = []
        verb_group = getattr(word, "verb_group", None)

        for tense, voice_dict in word.forms.items():
            for voice, mood_dict in voice_dict.items():
                for mood, number_dict in mood_dict.items():
                    for number, person_or_case_dict in number_dict.items():
                        for person_or_case, form in person_or_case_dict.items():
                            if form:
                                # Check if this is a participle (has case) or regular verb (has person)
                                if mood == "PARTICIPLE":
                                    features_list.append({
                                        "verb_group": verb_group,
                                        "tense": tense,
                                        "voice": voice,
                                        "mood": mood,
                                        "number": number,
                                        "person": None,
                                        "case_name": person_or_case,
                                    })
                                else:
                                    features_list.append({
                                        "verb_group": verb_group,
                                        "tense": tense,
                                        "voice": voice,
                                        "mood": mood,
                                        "number": number,
                                        "person": person_or_case,
                                        "case_name": None,
                                    })
        return features_list

    def _extract_adjective_features(self, word: PartOfSpeechBase) -> list[dict[str, str | None]]:
        """Extract feature combinations for adjectives and articles.

        Args:
            word: Adjective/Article with forms structure {gender: {number: {case: form}}}

        Returns:
            List of feature dictionaries
        """
        features_list = []
        for gender, number_dict in word.forms.items():
            for number, case_dict in number_dict.items():
                for case_name, form in case_dict.items():
                    if form:
                        features_list.append({
                            "gender": gender,
                            "number": number,
                            "case_name": case_name,
                        })
        return features_list

    def _extract_pronoun_features(self, word: PartOfSpeechBase) -> list[dict[str, str | None]]:
        """Extract feature combinations for pronouns.

        Args:
            word: Pronoun object

        Returns:
            List with single feature dictionary (minimal info, seed will override)
        """
        # Pronouns are complex - for now, store minimal info
        # Will be populated by seed file with proper type/person/gender/number/case
        return [{
            "type": "personal_strong",  # Default, will be overridden by seed
            "person": None,
            "gender": None,
            "number": None,
            "case_name": None,
        }]

    def _extract_simple_features(self) -> list[dict[str, str | None]]:
        """Extract features for simple POS (adverbs, prepositions, conjunctions).

        Returns:
            List with single empty dictionary (no features)
        """
        return [{}]

    def _extract_features_from_morpheus(
        self, word: PartOfSpeechBase, pos: PartOfSpeech
    ) -> list[dict[str, str | None]]:
        """Extract all valid feature combinations from Morpheus-generated forms.

        Args:
            word: PartOfSpeech object with forms generated by Morpheus
            pos: Part of speech type

        Returns:
            List of feature dictionaries, one per valid combination

        Examples:
            For a noun: [
                {"gender": "M", "number": "SINGULAR", "case_name": "NOMINATIVE"},
                {"gender": "M", "number": "SINGULAR", "case_name": "GENITIVE"},
                ...
            ]
        """
        if pos == PartOfSpeech.NOUN:
            return self._extract_noun_features(word)
        elif pos == PartOfSpeech.VERB:
            return self._extract_verb_features(word)
        elif pos in [PartOfSpeech.ADJECTIVE, PartOfSpeech.ARTICLE]:
            return self._extract_adjective_features(word)
        elif pos == PartOfSpeech.PRONOUN:
            return self._extract_pronoun_features(word)
        elif pos in [PartOfSpeech.ADVERB, PartOfSpeech.PREPOSITION, PartOfSpeech.CONJUNCTION]:
            return self._extract_simple_features()
        return []

    POS_CONFIG = {
        PartOfSpeech.NOUN: {
            "table": "greek_nouns",
            "fields": ["lemma", "gender", "number", "case_name", "validation_status"],
        },
        PartOfSpeech.VERB: {
            "table": "greek_verbs",
            "fields": [
                "lemma",
                "verb_group",
                "tense",
                "voice",
                "mood",
                "number",
                "person",
                "case_name",
                "validation_status",
            ],
        },
        PartOfSpeech.ADJECTIVE: {
            "table": "greek_adjectives",
            "fields": ["lemma", "gender", "number", "case_name", "validation_status"],
        },
        PartOfSpeech.ARTICLE: {
            "table": "greek_articles",
            "fields": ["lemma", "gender", "number", "case_name", "validation_status"],
        },
        PartOfSpeech.PRONOUN: {
            "table": "greek_pronouns",
            "fields": [
                "lemma",
                "type",
                "person",
                "gender",
                "number",
                "case_name",
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
        self, lemma: str, pos: PartOfSpeech, word: PartOfSpeechBase, features: dict[str, str | None]
    ) -> dict[str, str | int | None]:
        """Prepare values for one database row (one feature combination).

        Args:
            lemma: Greek word lemma
            pos: Part of speech
            word: Morpheus-generated word object
            features: Feature dictionary for this specific row

        Returns:
            Dictionary mapping field names to values for INSERT
        """
        config = self.POS_CONFIG[pos]
        fields = config["fields"]

        values: dict[str, str | int | None] = {
            "lemma": lemma,
            "validation_status": "VALID",
        }

        # Add all features from the dictionary
        for key, value in features.items():
            if key in fields:
                values[key] = value

        # Ensure all fields have a value (None for missing ones)
        for field in fields:
            if field not in values:
                values[field] = None

        return values

    def _execute_add_word_transaction(
        self, pos: PartOfSpeech, lemma: str, values_list: list[dict[str, Any]], translations: list[str]
    ) -> None:
        """Execute database transaction to add word with multiple feature rows.

        Args:
            pos: Part of speech
            lemma: Greek word lemma
            values_list: List of value dictionaries (one per feature combination)
            translations: English translations
        """
        table = POS_TO_TABLE_MAP[pos]
        config = self.POS_CONFIG[pos]
        fields = config["fields"]
        cursor = self._conn.cursor()

        try:
            # Step 1: Insert all Greek word rows (one per feature combination)
            columns = ", ".join(fields)
            placeholders = ", ".join(["?"] * len(fields))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            for values in values_list:
                cursor.execute(sql, [values.get(field) for field in fields])

            # Step 2: Insert/retrieve English words
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

            # Step 3: Create translation links (one per lemma, not per row)
            for eng_id in english_word_ids:
                cursor.execute(
                    "INSERT OR IGNORE INTO translations (english_word_id, greek_lemma, greek_pos_type) VALUES (?, ?, ?)",
                    (eng_id, lemma, pos.name),
                )

            self._conn.commit()

        except Exception:
            self._conn.rollback()
            raise

    def add_word(
        self, lemma: str, translations: list[str], pos: PartOfSpeech
    ) -> PartOfSpeechBase:
        """Add a word to the lexicon with automatic feature extraction.

        Args:
            lemma: Greek word in its base form
            translations: List of English translations (at least one required)
            pos: Part of speech enum

        Returns:
            Complete PartOfSpeech object with forms and translations

        Raises:
            ValueError: If translations empty, lemma empty, word exists, or Morpheus fails
        """
        # Validate inputs
        word = self._validate_and_prepare_lemma(lemma, pos, translations)

        # Extract all valid feature combinations from Morpheus forms
        features_list = self._extract_features_from_morpheus(word, pos)

        if not features_list:
            raise ValueError(f"No valid feature combinations found for '{lemma}'")

        # Prepare database values for each feature combination
        values_list = [
            self._prepare_database_values(lemma, pos, word, features)
            for features in features_list
        ]

        # Execute transaction to insert all rows
        self._execute_add_word_transaction(pos, lemma, values_list, translations)

        # Retrieve and return the word
        new_word = self._get_word_by_lemma(lemma, pos)
        if not new_word:
            raise RuntimeError(f"Failed to retrieve newly added word '{lemma}'")
        return new_word
