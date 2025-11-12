"""V2 template parser - handles grouping syntax with references"""

import re

from syntaxis.lib.templates.ast import Feature, Group, POSToken, TemplateAST
from syntaxis.lib.templates.feature_mapper import FeatureMapper


class V2Parser:
    """Parser for V2 template syntax: (lexical1 lexical2)@{features}"""

    @classmethod
    def parse(cls, template_str: str) -> TemplateAST:
        """Parse a V2 template string into an AST

        Args:
            template_str: V2 template string like "(noun adj)@{nom:masc:sg}"

        Returns:
            TemplateAST object

        Raises:
            ValueError: If template syntax is invalid
        """
        template_str = template_str.strip()
        groups = cls._parse_groups(template_str)
        cls._validate_references(groups)
        return TemplateAST(groups=groups, version=2)

    @classmethod
    def _parse_groups(cls, template_str: str) -> list[Group]:
        """Parse all groups from template string"""
        # Validate balanced parentheses and braces
        if template_str.count("(") != template_str.count(")"):
            raise ValueError("Unclosed group (mismatched parentheses)")
        if template_str.count("{") != template_str.count("}"):
            raise ValueError("Unclosed brace (mismatched braces)")

        # Check for empty groups - pattern: ()@
        if re.search(r"\(\s*\)@", template_str):
            raise ValueError("Empty group (no tokens specified)")

        groups = []
        reference_id = 1

        # Pattern: (tokens)@{features} or (tokens)@$N
        group_pattern = r"\(([^)]+)\)@(\{[^}]+\}|\$\d+)"

        for match in re.finditer(group_pattern, template_str):
            tokens_str = match.group(1).strip()

            # Check for empty group
            if not tokens_str:
                raise ValueError("Empty group (no tokens specified)")

            features_str = match.group(2)

            # Parse tokens
            tokens = cls._parse_tokens(tokens_str)

            # Parse features or reference
            if features_str.startswith("$"):
                # Reference to another group
                ref_id = int(features_str[1:])
                group = Group(
                    tokens=tokens,
                    group_features=[],
                    reference_id=reference_id,
                    references=ref_id,
                )
            else:
                # Direct features
                features = cls._parse_features(features_str)
                group = Group(
                    tokens=tokens,
                    group_features=features,
                    reference_id=reference_id,
                    references=None,
                )

            groups.append(group)
            reference_id += 1

        return groups

    @classmethod
    def _parse_tokens(cls, tokens_str: str) -> list[POSToken]:
        """Parse space-separated tokens, handling direct features"""
        tokens = []

        # Pattern: token or token{features}
        token_pattern = r"(\w+)(?:\{([^}]+)\})?"

        for token_match in re.finditer(token_pattern, tokens_str):
            lexical = token_match.group(1)
            direct_features_str = token_match.group(2)

            if direct_features_str:
                direct_features = cls._parse_features(f"{{{direct_features_str}}}")
            else:
                direct_features = []

            tokens.append(POSToken(lexical=lexical, direct_features=direct_features))

        return tokens

    @classmethod
    def _parse_features(cls, features_str: str) -> list[Feature]:
        """Parse feature string like {nom:masc:sg} into Feature objects"""
        # Remove braces
        features_str = features_str.strip("{}")

        # Split by colon
        feature_names = features_str.split(":")

        features = []
        for name in feature_names:
            name = name.strip()
            if name:
                sanitized_name, category = FeatureMapper.get_category(name)
                features.append(Feature(name=sanitized_name, category=category))

        return features

    @classmethod
    def _validate_references(cls, groups: list[Group]) -> None:
        """Validate that all group references are valid

        Raises:
            ValueError: If reference is invalid (forward or non-existent)
        """
        for i, group in enumerate(groups):
            if group.references is not None:
                ref_id = group.references
                current_position = i + 1  # 1-indexed

                # Check if reference exists
                if ref_id > len(groups):
                    raise ValueError(
                        f"Reference ${ref_id} does not exist "
                        f"(only {len(groups)} groups defined)"
                    )

                # Check if reference points backward
                if ref_id >= current_position:
                    raise ValueError(
                        f"Reference ${ref_id} points forward to group {ref_id} "
                        f"(current group is {current_position})"
                    )
