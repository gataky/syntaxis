"""Template parser for extracting token features from template strings."""

import re
from typing import List

from syntaxis.models import constants as c

from .models import (
    ParsedTemplate,
    TokenFeatures,
)


class TemplateParseError(Exception):
    """Raised when a template cannot be parsed."""


class Template:
    """Parses template strings into structured TokenFeatures.

    Template syntax: [POS:feature1:feature2:...]
    Example: [Article:nom:n:pl] [Noun:nom:n:pl] [Verb:pres:act:3:pl]
    """

    # Regex pattern to match tokens in format [POS:feature:feature:...]
    TOKEN_PATTERN = re.compile(r"\[([^\]]+)\]")

    # Valid string constants for validation
    POS_VALUES = {c.NOUN, c.VERB, c.ADJECTIVE, c.ADVERB, c.ARTICLE, c.PRONOUN,
                  c.NUMERAL, c.PREPOSITION, c.CONJUNCTION}
    CASE_VALUES = {c.NOMINATIVE, c.ACCUSATIVE, c.GENITIVE, c.VOCATIVE}
    GENDER_VALUES = {c.MASCULINE, c.FEMININE, c.NEUTER}
    NUMBER_VALUES = {c.SINGULAR, c.PLURAL}
    VOICE_VALUES = {c.ACTIVE, c.PASSIVE}
    TENSE_VALUES = {c.PRESENT, c.AORIST, c.PARATATIKOS}
    PERSON_VALUES = {c.FIRST, c.SECOND, c.THIRD}

    def parse(self, template: str) -> ParsedTemplate:
        """Parse a template string into a ParsedTemplate object.

        Args:
            template: Template string in format [POS:features...] [POS:features...]

        Returns:
            ParsedTemplate object containing the parsed tokens

        Raises:
            TemplateParseError: If the template is malformed or invalid
        """
        if not template or not template.strip():
            raise TemplateParseError("Template cannot be empty")

        # Extract all tokens from the template
        matches = self.TOKEN_PATTERN.findall(template)
        if not matches:
            raise TemplateParseError(f"No valid tokens found in template: {template}")

        tokens = []
        for match in matches:
            token = self._parse_token(match)
            tokens.append(token)

        return ParsedTemplate(raw_template=template, tokens=tokens)

    def _parse_token(self, token_str: str) -> TokenFeatures:
        """Parse a single token string into a TokenFeatures object.

        Args:
            token_str: Token string in format "POS:feature:feature:..."

        Returns:
            TokenFeatures object

        Raises:
            TemplateParseError: If the token is malformed or invalid
        """
        parts = [p.strip() for p in token_str.split(":")]
        if not parts:
            raise TemplateParseError(f"Empty token: [{token_str}]")

        # Parse part of speech
        pos_str = parts[0]
        if pos_str not in self.POS_VALUES:
            raise TemplateParseError(
                f"Unknown part of speech: {pos_str}. "
                f"Valid options: {sorted(self.POS_VALUES)}"
            )

        pos = pos_str
        features = parts[1:]

        # Create TokenFeatures with the POS
        token_features = TokenFeatures(pos=pos)

        # For invariable words, no additional features required
        if token_features.is_invariable():
            if features:
                raise TemplateParseError(
                    f"Invariable word {pos_str} should not have features, "
                    f"but got: {':'.join(features)}"
                )
            return token_features

        # Parse features based on POS type
        if pos in {c.NOUN, c.ADJECTIVE, c.ARTICLE}:
            token_features = self._parse_nominal_features(
                token_features, features, pos_str
            )
        elif pos == c.VERB:
            token_features = self._parse_verbal_features(
                token_features, features, pos_str
            )
        elif pos == c.PRONOUN:
            token_features = self._parse_pronoun_features(
                token_features, features, pos_str
            )

        return token_features

    def _parse_nominal_features(
        self, token: TokenFeatures, features: List[str], pos_str: str
    ) -> TokenFeatures:
        """Parse features for nouns, adjectives, and articles.

        Required features: case, gender, number (in any order)

        Args:
            token: TokenFeatures object to populate
            features: List of feature strings
            pos_str: String representation of POS for error messages

        Returns:
            Updated TokenFeatures object

        Raises:
            TemplateParseError: If features are missing or invalid
        """
        if len(features) != 3:
            raise TemplateParseError(
                f"{pos_str} requires exactly 3 features (case, gender, number), "
                f"but got {len(features)}: {':'.join(features)}"
            )

        # Parse each feature - try to match against case, gender, or number
        for feature in features:
            if feature in self.CASE_VALUES and token.case is None:
                token.case = feature
            elif feature in self.GENDER_VALUES and token.gender is None:
                token.gender = feature
            elif feature in self.NUMBER_VALUES and token.number is None:
                token.number = feature
            else:
                raise TemplateParseError(
                    f"Invalid or duplicate feature for {pos_str}: {feature}"
                )

        # Verify all required features are present
        if token.case is None or token.gender is None or token.number is None:
            raise TemplateParseError(
                f"{pos_str} must have case, gender, and number. Got: {':'.join(features)}"
            )

        return token

    def _parse_verbal_features(
        self, token: TokenFeatures, features: List[str], pos_str: str
    ) -> TokenFeatures:
        """Parse features for verbs.

        Required features: tense, voice, person, number (in any order)

        Args:
            token: TokenFeatures object to populate
            features: List of feature strings
            pos_str: String representation of POS for error messages

        Returns:
            Updated TokenFeatures object

        Raises:
            TemplateParseError: If features are missing or invalid
        """
        if len(features) != 4:
            raise TemplateParseError(
                f"{pos_str} requires exactly 4 features (tense, voice, person, number), "
                f"but got {len(features)}: {':'.join(features)}"
            )

        # Parse each feature
        for feature in features:
            if feature in self.TENSE_VALUES and token.tense is None:
                token.tense = feature
            elif feature in self.VOICE_VALUES and token.voice is None:
                token.voice = feature
            elif feature in self.PERSON_VALUES and token.person is None:
                token.person = feature
            elif feature in self.NUMBER_VALUES and token.number is None:
                token.number = feature
            else:
                raise TemplateParseError(
                    f"Invalid or duplicate feature for {pos_str}: {feature}"
                )

        # Verify all required features are present
        if (
            token.tense is None
            or token.voice is None
            or token.person is None
            or token.number is None
        ):
            raise TemplateParseError(
                f"{pos_str} must have tense, voice, person, and number. "
                f"Got: {':'.join(features)}"
            )

        return token

    def _parse_pronoun_features(
        self, token: TokenFeatures, features: List[str], pos_str: str
    ) -> TokenFeatures:
        """Parse features for pronouns.

        Required features: case, person, number
        Optional features: gender (required for 3rd person)

        Args:
            token: TokenFeatures object to populate
            features: List of feature strings
            pos_str: String representation of POS for error messages

        Returns:
            Updated TokenFeatures object

        Raises:
            TemplateParseError: If features are missing or invalid
        """
        if len(features) < 3 or len(features) > 4:
            raise TemplateParseError(
                f"{pos_str} requires 3-4 features (case, person, number, [gender]), "
                f"but got {len(features)}: {':'.join(features)}"
            )

        # Parse each feature - try to match against case, person, number, or gender
        for feature in features:
            if feature in self.CASE_VALUES and token.case is None:
                token.case = feature
            elif feature in self.PERSON_VALUES and token.person is None:
                token.person = feature
            elif feature in self.NUMBER_VALUES and token.number is None:
                token.number = feature
            elif feature in self.GENDER_VALUES and token.gender is None:
                token.gender = feature
            else:
                raise TemplateParseError(
                    f"Invalid or duplicate feature for {pos_str}: {feature}"
                )

        # Verify all required features are present
        if token.case is None or token.person is None or token.number is None:
            raise TemplateParseError(
                f"{pos_str} must have case, person, and number. Got: {':'.join(features)}"
            )

        return token
