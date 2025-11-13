import logging
import sqlite3
from typing import Any

from syntaxis.lib import constants as c
from syntaxis.lib.models.lexical import Lexical
from syntaxis.lib.morpheus import Morpheus

from .schema import create_schema

logger = logging.getLogger(__name__)


class Database:
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
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)

        self._conn.row_factory = sqlite3.Row  # Enable column access by name
        create_schema(self._conn)
        self._morphology_adapter = None

    # Storage methods
    # Random selection methods

    def get_random_word(self, lexical: str, **features: Any) -> Lexical | None:
        """Get a random word of the specified part of speech.

        Args:
            lexical: Part of speech string (c.NOUN, c.VERB, etc.)
            **features: Feature filters as string constants
                        (gender=c.MASCULINE, case=c.NOMINATIVE, etc.)

        Returns:
            Instance of appropriate PartOfSpeech subclass with forms and
            translations, or None if no matches

        Raises:
            ValueError: If invalid features provided for the lexical type

        Examples:
            >>> manager.get_random_word(c.NOUN, number=c.SINGULAR)
            Noun(lemma="άνθρωπος", ...)
        """
        # Validate features
        valid_features = c.VALID_CASE_FEATURES.get(lexical, set())
        invalid_features = set(features.keys()) - valid_features

        if invalid_features:
            raise ValueError(
                f"Invalid features {invalid_features} for {lexical}. "
                + f"Valid features are: {valid_features}"
            )

        cursor = self._conn.cursor()
        table = c.LEXICAL_TO_TABLE_MAP[lexical]

        # Build WHERE conditions using direct column comparisons
        conditions = []
        where_params: list[str] = []

        for feature_name, feature_value in features.items():
            # Use string constant directly and wrap in [] to allow us to use reserved
            # sqlite3 keys as columns.  Case in this example
            conditions.append(f"g.[{feature_name}] = ?")
            where_params.append(feature_value)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Query with DISTINCT to handle multiple rows per lemma
        query = f"""
            SELECT
                g.lemma,
                (SELECT GROUP_CONCAT(e.word, '|')
                 FROM translations t
                 JOIN english_words e ON e.id = t.english_word_id
                 WHERE t.greek_lemma = g.lemma AND t.greek_lexical = ?) as translations
            FROM {table} g
            WHERE {where_clause}
            GROUP BY g.lemma
            ORDER BY RANDOM()
            LIMIT 1
        """

        # Parameters must be in the order they appear in the query:
        # 1. Subquery parameter (lexical) comes first
        # 2. WHERE clause parameters come after
        params = [lexical] + where_params


        row = cursor.execute(query, params).fetchone()
        if not row:
            return None

        lex = self._create_word_from_row(row, lexical)
        lex.apply_features(**features)
        return lex

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

    def _get_word_by_lemma(self, lemma: str, lexical: str):
        """Helper to retrieve a word by its lemma and lexical.

        Args:
            lemma: Greek word lemma
            lexical: Part of speech

        Returns:
            Word object or None if not found
        """
        cursor = self._conn.cursor()
        table = c.LEXICAL_TO_TABLE_MAP[lexical]

        # Query with JOIN to get lemma and translations
        query = f"""
            SELECT
                g.lemma,
                (SELECT GROUP_CONCAT(e.word, '|')
                 FROM translations t
                 JOIN english_words e ON e.id = t.english_word_id
                 WHERE t.greek_lemma = g.lemma AND t.greek_lexical = ?) as translations
            FROM {table} g
            WHERE g.lemma = ?
            LIMIT 1
        """

        row = cursor.execute(query, (lexical, lemma)).fetchone()
        if not row:
            return None

        return self._create_word_from_row(row, lexical)

    def _create_word_from_row(self, row: sqlite3.Row, lexical: str) -> Lexical:
        """Create PartOfSpeech object with translations from query result.

        Args:
            row: Database row with id, lemma, and translations columns
            lexical: Part of speech enum

        Returns:
            Complete PartOfSpeech object with forms and translations
        """
        lemma = row["lemma"]
        translations_str = row["translations"]

        # Parse translations (GROUP_CONCAT returns pipe-delimited string)
        translations = translations_str.split("|") if translations_str else None

        # Create word with inflected forms using Morpheus
        word = Morpheus.create(lemma, lexical)
        word.translations = translations

        return word

    def _extract_noun_features(self, word: Lexical) -> list[dict[str, str | None]]:
        """Extract feature combinations for nouns.

        Args:
            word: Noun with forms structure {gender: {number: {case: form}}}

        Returns:
            List of feature dictionaries
        """
        features_list = []
        for gender, number_dict in word.forms.items():
            for number, case_dict in number_dict.items():
                for case, form in case_dict.items():
                    if form:  # Only if form exists
                        features_list.append(
                            {
                                c.GENDER: gender,
                                c.NUMBER: number,
                                c.CASE: case,
                            }
                        )
        return features_list

    def _extract_verb_features(self, word: Lexical) -> list[dict[str, str | None]]:
        """Extract feature combinations for verbs.

        Handles various verb form structures that Morpheus returns.

        Args:
            word: Verb with forms from Morpheus

        Returns:
            List of feature dictionaries
        """
        features_list = []
        verb_group = getattr(word, "verb_group", None)

        for tense, voice_dict in word.forms.items():
            # Handle case where tense maps directly to a set (shouldn't happen, but defensive)
            if isinstance(voice_dict, set):
                features_list.append(
                    {
                        "verb_group": verb_group,
                        c.TENSE: tense,
                        c.VOICE: None,
                        c.MOOD: None,
                        c.NUMBER: None,
                        c.PERSON: None,
                        c.CASE: None,
                    }
                )
                continue

            for voice, mood_dict in voice_dict.items():
                # Handle case where voice maps directly to a set (shouldn't happen, but defensive)
                if isinstance(mood_dict, set):
                    features_list.append(
                        {
                            "verb_group": verb_group,
                            c.TENSE: tense,
                            c.VOICE: voice,
                            c.MOOD: None,
                            c.NUMBER: None,
                            c.PERSON: None,
                            c.CASE: None,
                        }
                    )
                    continue

                for mood, mood_value in mood_dict.items():
                    # Check if this is an infinitive (just a set of forms)
                    if isinstance(mood_value, set):
                        # Infinitive: no number/person/case
                        features_list.append(
                            {
                                "verb_group": verb_group,
                                c.TENSE: tense,
                                c.VOICE: voice,
                                c.MOOD: mood,
                                c.NUMBER: None,
                                c.PERSON: None,
                                c.CASE: None,
                            }
                        )
                    # Check if this is a participle (has gender level)
                    elif mood == "participle":
                        # Participle: {gender: {number: {case: {forms}}}}
                        for gender, number_dict in mood_value.items():
                            for number, case_dict in number_dict.items():
                                for case, forms in case_dict.items():
                                    if forms:
                                        features_list.append(
                                            {
                                                "verb_group": verb_group,
                                                c.TENSE: tense,
                                                c.VOICE: voice,
                                                c.MOOD: mood,
                                                c.NUMBER: number,
                                                c.PERSON: None,
                                                c.CASE: case,
                                            }
                                        )
                    else:
                        # Regular mood: {number: {person: {forms}}}
                        for number, person_dict in mood_value.items():
                            # Handle case where number maps directly to a set (no person level)
                            if isinstance(person_dict, set):
                                features_list.append(
                                    {
                                        "verb_group": verb_group,
                                        c.TENSE: tense,
                                        c.VOICE: voice,
                                        c.MOOD: mood,
                                        c.NUMBER: number,
                                        c.PERSON: None,
                                        c.CASE: None,
                                    }
                                )
                            else:
                                for person, forms in person_dict.items():
                                    if forms:
                                        features_list.append(
                                            {
                                                "verb_group": verb_group,
                                                c.TENSE: tense,
                                                c.VOICE: voice,
                                                c.MOOD: mood,
                                                c.NUMBER: number,
                                                c.PERSON: person,
                                                c.CASE: None,
                                            }
                                        )
        return features_list

    def _extract_adjective_features(self, word: Lexical) -> list[dict[str, str | None]]:
        """Extract feature combinations for adjectives and articles.

        Args:
            word: Adjective/Article with forms structure {gender: {number: {case: form}}}

        Returns:
            List of feature dictionaries
        """
        features_list = []
        for number, gender_dict in word.forms.get(c.ADJECTIVE, {}).items():
            for gender, case_dict in gender_dict.items():
                for case, form in case_dict.items():
                    if form:
                        features_list.append(
                            {
                                c.GENDER: gender,
                                c.NUMBER: number,
                                c.CASE: case,
                            }
                        )
        return features_list

    def _extract_pronoun_features(self, word: Lexical) -> list[dict[str, str | None]]:
        """Extract feature combinations for pronouns.

        Args:
            word: Pronoun object

        Returns:
            List with single feature dictionary (minimal info, seed will override)
        """
        # Pronouns are complex - for now, store minimal info
        # Will be populated by seed file with proper type/person/gender/number/case
        return [
            {
                "type": "personal_strong",  # Default, will be overridden by seed
                c.PERSON: None,
                c.GENDER: None,
                c.NUMBER: None,
                c.CASE: None,
            }
        ]

    def _extract_simple_features(self) -> list[dict[str, str | None]]:
        """Extract features for simple lexical (adverbs, prepositions, conjunctions).

        Returns:
            List with single empty dictionary (no features)
        """
        return [{}]

    def _extract_features_from_morpheus(
        self, word: Lexical, lexical: str
    ) -> list[dict[str, str | None]]:
        """Extract all valid feature combinations from Morpheus-generated forms.

        Args:
            word: PartOfSpeech object with forms generated by Morpheus
            lexical: Part of speech type

        Returns:
            List of feature dictionaries, one per valid combination

        Examples:
            For a noun: [
                {"gender": "masc", "number": "sg", "case": "nom"},
                {"gender": "masc", "number": "sg", "case": "gen"},
                ...
            ]
        """
        if lexical == c.NOUN:
            return self._extract_noun_features(word)
        elif lexical == c.VERB:
            return self._extract_verb_features(word)
        elif lexical in [c.ADJECTIVE, c.ARTICLE]:
            return self._extract_adjective_features(word)
        elif lexical == c.PRONOUN:
            return self._extract_pronoun_features(word)
        elif lexical in [c.ADVERB, c.PREPOSITION, c.CONJUNCTION]:
            return self._extract_simple_features()
        return []

    def _validate_and_prepare_lemma(
        self, lemma: str, lexical: str, translations: list[str]
    ) -> Lexical:
        """Validate inputs and use Morpheus to create a word object."""
        if not lemma:
            raise ValueError("Lemma cannot be empty")
        if not translations:
            raise ValueError("At least one translation required")

        table = c.LEXICAL_TO_TABLE_MAP[lexical]
        cursor = self._conn.cursor()
        existing = cursor.execute(
            f"SELECT id FROM {table} WHERE lemma = ?", (lemma,)
        ).fetchone()
        if existing:
            raise ValueError(f"Word '{lemma}' already exists as {lexical}")

        try:
            word = Morpheus.create(lemma, lexical)
        except Exception as e:
            raise ValueError(f"Failed to generate forms for '{lemma}': {e}")

        if not word.forms:
            raise ValueError(f"Morpheus generated no forms for '{lemma}'")

        return word

    def _prepare_database_values(
        self, lemma: str, lexical: str, word: Lexical, features: dict[str, str | None]
    ) -> dict[str, str | int | None]:
        """Prepare values for one database row (one feature combination).

        Args:
            lemma: Greek word lemma
            lexical: Part of speech
            word: Morpheus-generated word object
            features: Feature dictionary for this specific row

        Returns:
            Dictionary mapping field names to values for INSERT
        """
        config = c.LEXICAL_CONFIG[lexical]
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
        self,
        lexical: str,
        lemma: str,
        values_list: list[dict[str, Any]],
        translations: list[str],
    ) -> None:
        """Execute database transaction to add word with multiple feature rows.

        Args:
            lexical: Part of speech
            lemma: Greek word lemma
            values_list: List of value dictionaries (one per feature combination)
            translations: English translations
        """
        table = c.LEXICAL_TO_TABLE_MAP[lexical]
        config = c.LEXICAL_CONFIG[lexical]
        fields = config["fields"]
        cursor = self._conn.cursor()

        try:
            # Step 1: Insert all Greek word rows (one per feature combination)
            columns = ", ".join(f'"{field}"' for field in fields)
            placeholders = ", ".join(["?"] * len(fields))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            for values in values_list:
                cursor.execute(sql, [values.get(field) for field in fields])

            # Step 2: Insert/retrieve English words
            english_word_ids = []
            for translation in translations:
                translation = translation.strip()
                cursor.execute(
                    "INSERT OR IGNORE INTO english_words (word, lexical) VALUES (?, ?)",
                    (translation, lexical),
                )
                eng_id_row = cursor.execute(
                    "SELECT id FROM english_words WHERE word = ? AND lexical = ?",
                    (translation, lexical),
                ).fetchone()
                if eng_id_row:
                    english_word_ids.append(eng_id_row[0])

            # Step 3: Create translation links (one per lemma, not per row)
            for eng_id in english_word_ids:
                cursor.execute(
                    "INSERT OR IGNORE INTO translations (english_word_id, greek_lemma, greek_lexical) VALUES (?, ?, ?)",
                    (eng_id, lemma, lexical),
                )

            self._conn.commit()

        except Exception:
            self._conn.rollback()
            raise

    def add_word(self, lemma: str, translations: list[str], lexical: str) -> Lexical:
        """Add a word to the lexicon with automatic feature extraction.

        Args:
            lemma: Greek word in its base form
            translations: List of English translations (at least one required)
            lexical: Part of speech string constant (c.NOUN, c.VERB, etc.)

        Returns:
            Complete PartOfSpeech object with forms and translations

        Raises:
            ValueError: If translations empty, lemma empty, word exists, or Morpheus fails
        """
        # Validate inputs
        word = self._validate_and_prepare_lemma(lemma, lexical, translations)

        # Extract all valid feature combinations from Morpheus forms
        features_list = self._extract_features_from_morpheus(word, lexical)

        if not features_list:
            raise ValueError(f"No valid feature combinations found for '{lemma}'")

        # Prepare database values for each feature combination
        values_list = [
            self._prepare_database_values(lemma, lexical, word, features)
            for features in features_list
        ]

        # Execute transaction to insert all rows
        self._execute_add_word_transaction(lexical, lemma, values_list, translations)

        # Retrieve and return the word
        new_word = self._get_word_by_lemma(lemma, lexical)
        if not new_word:
            raise RuntimeError(f"Failed to retrieve newly added word '{lemma}'")
        return new_word
