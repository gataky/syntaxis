import logging

from syntaxis.lib.database import Database
from syntaxis.lib.logging import log_calls
from syntaxis.lib.models.lexical import Lexical
from syntaxis.lib.templates import Template
from syntaxis.lib.templates.ast import Feature, Group, TemplateAST
from syntaxis.lib.templates.v1_parser import V1Parser
from syntaxis.lib.templates.v2_parser import V2Parser

logger = logging.getLogger(__name__)


class Syntaxis:
    """Main API for generating grammatically correct Greek sentences.

    This class orchestrates the entire sentence generation workflow by:
    1. Parsing grammatical templates into structured tokens
    2. Retrieving random Greek words from the database that match each token's features
    3. Returning lexical objects that can be inflected to the correct forms

    The Syntaxis class integrates the template parser, database, and morphological
    system to provide a simple interface for generating varied Greek sentences
    based on grammatical specifications.

    Attributes:
        database: Database instance containing the Greek vocabulary lexicon
        template: Template parser for converting template strings into tokens

    Example:
        Basic usage with a simple sentence template:

        >>> sx = Syntaxis()
        >>> words = sx.generate_sentence("[article:nom:masc:sg] [noun:nom:masc:sg]")
        >>> print(" ".join(str(word) for word in words))
        ο άνδρας

        More complex template with verb:

        >>> template = "[article:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:3:sg]"
        >>> words = sx.generate_sentence(template)
        >>> sentence = " ".join(str(word) for word in words)
        >>> print(sentence)
        ο άνδρας βλέπει

        Accessing word properties:

        >>> words = sx.generate_sentence("[noun:acc:fem:pl]")
        >>> word = words[0]
        >>> print(f"Lemma: {word.lemma}")
        >>> print(f"Inflected: {word}")
        Lemma: γυναίκα
        Inflected: γυναίκες
    """

    def __init__(self, db_path: str = "./syntaxis.db"):
        """Initialize the Syntaxis sentence generator.

        Creates a new Syntaxis instance with:
        - A Database connection to "./syntaxis.db" for vocabulary storage
        - A Template parser for processing grammatical templates

        The database must be pre-populated with Greek vocabulary using the
        CLI commands (create-db, seed-dictionary, seed-articles, seed-pronouns).

        Raises:
            FileNotFoundError: If syntaxis.db does not exist in the current directory
            sqlite3.DatabaseError: If the database file is corrupted or invalid
        """
        self.database: Database = Database(db_path)
        self.template: Template = Template()

    @log_calls
    def generate_sentence(self, template: str) -> list[Lexical]:
        """Generate a list of Greek words matching a grammatical template.

        Parses the template string into grammatical tokens, then retrieves random
        Greek words from the database that match each token's lexical type and
        grammatical features. Each word is returned as a Lexical object that
        contains both the lemma and inflected forms.

        Args:
            template: A template string specifying the sentence structure.
                V1 Format: "[lexical:feature1:feature2:...] [lexical:...]"
                V2 Format: "(lexical1 lexical2)@{feature1:feature2:...}"
                Examples:
                - "[article:nom:masc:sg] [noun:nom:masc:sg]"
                - "(article noun)@{nom:masc:sg}"
                - "[verb:aorist:active:pri:pl]"
                - "[prep] [article:acc:fem:pl] [noun:acc:fem:pl]"

        Returns:
            A list of Lexical objects (Noun, Verb, Adjective, etc.), one for each
            token in the template. Each Lexical object can be converted to a string
            to get the inflected word form, or accessed via .lemma for the base form.

        Raises:
            TemplateParseError: If the template syntax is invalid or features are
                incorrectly specified for a lexical type
            ValueError: If template format is invalid or no words in the database
                match the specified features

        Example:
            Simple nominative phrase:

            >>> sx = Syntaxis()
            >>> words = sx.generate_sentence("[article:nom:neut:pl] [noun:nom:neut:pl]")
            >>> for word in words:
            ...     print(f"{word.lemma} -> {word}")
            το -> τα
            παιδί -> παιδιά

            Complete sentence with verb:

            >>> template = "[noun:nom:masc:sg] [verb:present:active:ter:sg] [noun:acc:fem:sg]"
            >>> words = sx.generate_sentence(template)
            >>> sentence = " ".join(str(word) for word in words)
            >>> print(sentence)
            άνδρας βλέπει γυναίκα

            V2 syntax with grouping:

            >>> template = "(article noun)@{nom:masc:sg}"
            >>> words = sx.generate_sentence(template)
            >>> print(" ".join(str(w) for w in words))
            ο άνδρας

        Note:
            The order and specific words returned will vary on each call since
            words are selected randomly from the database. Only the grammatical
            structure is guaranteed to match the template.
        """
        template = template.strip()

        # Version detection
        if not template:
            raise ValueError("Invalid template format: empty template")

        if template[0] == "[":
            # V1 format
            ast = V1Parser.parse(template)
        elif template[0] == "(":
            # V2 format
            ast = V2Parser.parse(template)
        else:
            raise ValueError(
                f"Invalid template format: must start with '[' (V1) or '(' (V2), "
                f"got '{template[0]}'"
            )

        # Generate sentence from AST
        result = self._generate_from_ast(ast)
        sentence_text = " ".join(str(word) for word in result)
        logger.info(f"Generated sentence: '{sentence_text}'")
        return result

    @log_calls
    def _generate_from_ast(self, ast: TemplateAST) -> list[Lexical]:
        """Generate lexicals from AST by resolving features and querying database

        Args:
            ast: Parsed template AST

        Returns:
            List of Lexical objects with inflected forms
        """
        lexicals = []

        for group in ast.groups:
            # Resolve group features (handle references)
            resolved_group_features = self._resolve_group_features(group, ast.groups)

            # Generate lexical for each token in group
            for token in group.tokens:
                # Merge features: group features + direct features (with warnings)
                final_features = self._merge_features(
                    resolved_group_features,
                    token.direct_features,
                    warn_on_override=True,
                    context=f"Token '{token.lexical}' ",
                )

                # Convert features to kwargs for database query
                feature_dict = {f.category: f.name for f in final_features}

                # Get word from database
                lexical = self.database.get_random_word(token.lexical, **feature_dict)

                if not lexical:
                    # Build feature string for error message
                    feature_str = ":".join([f.name for f in final_features])
                    raise ValueError(
                        f"No {token.lexical} found matching features [{feature_str}]. "
                        f"This combination of features may not exist in the database."
                    )

                logger.debug(
                    f"Selected word '{lexical.lemma}' for token {token.lexical}"
                )
                lexicals.append(lexical)

        return lexicals

    def _resolve_group_features(
        self, group: Group, all_groups: list[Group]
    ) -> list[Feature]:
        """Resolve group features, following references if present

        Args:
            group: The group to resolve features for
            all_groups: All groups in the template (for reference lookup)

        Returns:
            List of resolved features
        """
        if group.references is None:
            # No reference, just return group features
            return group.group_features.copy()

        # Find referenced group
        referenced_group = all_groups[group.references - 1]  # Convert to 0-indexed

        # Start with referenced group's features (recursively resolve)
        features = self._resolve_group_features(referenced_group, all_groups)

        # Merge in current group features (override by category)
        return self._merge_features(features, group.group_features)

    def _merge_features(
        self,
        base_features: list[Feature],
        override_features: list[Feature],
        warn_on_override: bool = False,
        context: str = "",
    ) -> list[Feature]:
        """Merge two feature lists, with overrides replacing by category

        Args:
            base_features: Base feature list
            override_features: Features to override/add
            warn_on_override: If True, emit warning when override occurs
            context: Context string for warning message

        Returns:
            Merged feature list
        """
        # Build dict of category -> feature from base
        merged = {f.category: f for f in base_features}

        # Override with new features
        for feature in override_features:
            if warn_on_override and feature.category in merged:
                old_feature = merged[feature.category]
                logger.warning(
                    f"{context}overrides feature '{feature.category}': "
                    f"{old_feature.name} -> {feature.name}"
                )
            merged[feature.category] = feature

        return list(merged.values())
