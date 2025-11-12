"""V1 template parser - handles bracket syntax [lexical:features]"""

from syntaxis.lib.templates.api import Template
from syntaxis.lib.templates.ast import Feature, Group, POSToken, TemplateAST
from syntaxis.lib.templates.feature_mapper import FeatureMapper


class V1Parser:
    """Parser for V1 template syntax: [lexical:feature1:feature2:...]"""

    @classmethod
    def parse(cls, template_str: str) -> TemplateAST:
        """Parse a V1 template string into an AST

        Args:
            template_str: V1 template string like "[noun:nom:masc:sg]"

        Returns:
            TemplateAST object with version=1
        """
        # Use existing V1 parser
        template_parser = Template()
        parsed = template_parser.parse(template_str)

        # Convert to AST format
        groups = []
        for i, token in enumerate(parsed.tokens):
            # Convert token features to Feature objects
            features = []
            token_features = token.features()
            for category, feature_name in token_features.items():
                # Get the expanded feature name and category from the mapper
                expanded_name, expanded_category = FeatureMapper.get_category(
                    feature_name
                )
                features.append(Feature(name=expanded_name, category=expanded_category))

            # Create single-token group (V1 doesn't support grouping)
            pos_token = POSToken(lexical=token.lexical, direct_features=[])
            group = Group(
                tokens=[pos_token],
                group_features=features,
                reference_id=i + 1,
                references=None,
            )
            groups.append(group)

        return TemplateAST(groups=groups, version=1)
