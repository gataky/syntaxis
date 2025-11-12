"""Template parser for extracting token features from template strings."""

import re
from typing import List

from syntaxis.lib import constants as c

from .models import (
    ParsedTemplate,
    Token,
)


class TemplateParseError(Exception):
    """Raised when a template cannot be parsed."""


class Template:
    """Parses template strings into structured TokenFeatures.

    Template syntax: [lexical:feature1:feature2:...]
    Example: [Article:nom:n:pl] [Noun:nom:n:pl] [Verb:pres:act:3:pl]
    """

    # Regex pattern to match tokens in format [lexical:feature:feature:...]
    TOKEN_PATTERN = re.compile(r"\[([^\]]+)\]")

    def parse(self, template: str) -> ParsedTemplate:
        """Parse a template string into a ParsedTemplate object.

        Args:
            template: Template string in format [lexical:features...] [lexical:features...]

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

    def _parse_token(self, token_str: str) -> Token:
        """Parse a single token string into a TokenFeatures object.

        Args:
            token_str: Token string in format "lexical:feature:feature:..."

        Returns:
            TokenFeatures object

        Raises:
            TemplateParseError: If the token is malformed or invalid
        """
        parts = [p.strip() for p in token_str.split(":")]
        if not parts:
            raise TemplateParseError(f"Empty token: [{token_str}]")

        # Parse part of speech
        lexical = parts[0]
        if lexical not in c.LEXICAL_VALUES:
            raise TemplateParseError(
                f"Unknown part of speech: {lexical}. "
                f"Valid options: {sorted(c.LEXICAL_VALUES)}"
            )

        features = parts[1:]

        token = Token(lexical)

        # For invariable words, no additional features required
        if token.is_invariable():
            if features:
                raise TemplateParseError(
                    f"Invariable word {lexical} should not have features, "
                    f"but got: {':'.join(features)}"
                )
            return token

        # Parse features based on lexical type
        if lexical in {c.NOUN, c.ADJECTIVE, c.ARTICLE}:
            token = self._parse_nominal_features(token, features, lexical)
        elif lexical == c.VERB:
            token = self._parse_verbal_features(token, features, lexical)
        elif lexical == c.PRONOUN:
            token = self._parse_pronoun_features(token, features, lexical)

        return token

    def _parse_nominal_features(
        self, token: Token, features: List[str], lexical: str
    ) -> Token:
        """Parse features for nouns, adjectives, and articles.

        Required features: case, gender, number (in any order)

        Args:
            token: TokenFeatures object to populate
            features: List of feature strings
            lexical: String representation of lexical for error messages

        Returns:
            Updated TokenFeatures object

        Raises:
            TemplateParseError: If features are missing or invalid
        """
        if len(features) != 3:
            raise TemplateParseError(
                f"{lexical} requires exactly 3 features (case, gender, number), "
                f"but got {len(features)}: {':'.join(features)}"
            )

        # Parse each feature - try to match against case, gender, or number
        for feature in features:
            if feature in c.CASE_VALUES and token.case is None:
                token.case = feature
            elif feature in c.GENDER_VALUES and token.gender is None:
                token.gender = feature
            elif feature in c.NUMBER_VALUES and token.number is None:
                token.number = feature
            else:
                raise TemplateParseError(
                    f"Invalid or duplicate feature for {lexical}: {feature}"
                )

        # Verify all required features are present
        if token.case is None or token.gender is None or token.number is None:
            raise TemplateParseError(
                f"{lexical} must have case, gender, and number. Got: {':'.join(features)}"
            )

        return token

    def _parse_verbal_features(
        self, token: Token, features: List[str], lexical: str
    ) -> Token:
        """Parse features for verbs.

        Required features: tense, voice, person, number (in any order)

        Args:
            token: TokenFeatures object to populate
            features: List of feature strings
            lexical: String representation of lexical for error messages

        Returns:
            Updated TokenFeatures object

        Raises:
            TemplateParseError: If features are missing or invalid
        """
        if len(features) != 4:
            raise TemplateParseError(
                f"{lexical} requires exactly 4 features (tense, voice, person, number), "
                f"but got {len(features)}: {':'.join(features)}"
            )

        # Parse each feature
        for feature in features:
            if feature in c.TENSE_VALUES and token.tense is None:
                token.tense = feature
            elif feature in c.VOICE_VALUES and token.voice is None:
                token.voice = feature
            elif feature in c.PERSON_VALUES and token.person is None:
                token.person = feature
            elif feature in c.NUMBER_VALUES and token.number is None:
                token.number = feature
            else:
                raise TemplateParseError(
                    f"Invalid or duplicate feature for {lexical}: {feature}"
                )

        # Verify all required features are present
        if (
            token.tense is None
            or token.voice is None
            or token.person is None
            or token.number is None
        ):
            raise TemplateParseError(
                f"{lexical} must have tense, voice, person, and number. "
                f"Got: {':'.join(features)}"
            )

        return token

    def _parse_pronoun_features(
        self, token: Token, features: List[str], lexical: str
    ) -> Token:
        """Parse features for pronouns.

        Required features: case, person, number
        Optional features: gender (required for 3rd person)

        Args:
            token: TokenFeatures object to populate
            features: List of feature strings
            lexical: String representation of lexical for error messages

        Returns:
            Updated TokenFeatures object

        Raises:
            TemplateParseError: If features are missing or invalid
        """
        if len(features) < 3 or len(features) > 4:
            raise TemplateParseError(
                f"{lexical} requires 3-4 features (case, person, number, [gender]), "
                f"but got {len(features)}: {':'.join(features)}"
            )

        # Parse each feature - try to match against case, person, number, or gender
        for feature in features:
            if feature in c.CASE_VALUES and token.case is None:
                token.case = feature
            elif feature in c.PERSON_VALUES and token.person is None:
                token.person = feature
            elif feature in c.NUMBER_VALUES and token.number is None:
                token.number = feature
            elif feature in c.GENDER_VALUES and token.gender is None:
                token.gender = feature
            else:
                raise TemplateParseError(
                    f"Invalid or duplicate feature for {lexical}: {feature}"
                )

        # Verify all required features are present
        if token.case is None or token.person is None or token.number is None:
            raise TemplateParseError(
                f"{lexical} must have case, person, and number. Got: {':'.join(features)}"
            )

        return token
