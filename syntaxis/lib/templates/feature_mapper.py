"""Maps feature names to their grammatical categories"""

from syntaxis.lib import constants as c


class FeatureMapper:
    """Maps feature names to grammatical categories"""

    @classmethod
    def get_category(cls, feature_name: str) -> tuple[str, str]:
        """Get the grammatical category for a feature name

        Args:
            feature_name: The feature name (e.g., 'nom', 'masc', 'sg')

        Returns:
            The category name (e.g., 'case', 'gender', 'number')

        Raises:
            ValueError: If feature name is not recognized
        """
        # First check for exact match
        if feature_name in c.FEATURE_CATEGORIES:
            return feature_name, c.FEATURE_CATEGORIES[feature_name]

        # If no exact match, look for prefix matches
        valid_features: list[str] = []
        for k in c.FEATURE_CATEGORIES.keys():
            if k.startswith(feature_name):
                valid_features.append(k)

        if len(valid_features) == 0:
            raise ValueError(f"Unknown feature: {feature_name}")
        elif len(valid_features) > 1:
            conflicts = " ".join(valid_features)
            raise ValueError(
                f"Ambiguous feature: {feature_name}.  Conflicts with {conflicts}."
            )

        feature_name = valid_features[0]
        # Wildcards are now in *name* format, no stripping needed
        return feature_name, c.FEATURE_CATEGORIES[feature_name]
