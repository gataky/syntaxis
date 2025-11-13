"""Maps feature names to their grammatical categories"""

from syntaxis.lib import constants as c


class LexicalMapper:
    """Maps lexical names to grammatical categories"""

    @classmethod
    def get_lexical(cls, lexical_name: str) -> str:
        """Get the grammatical category for a feature name

        Args:
            feature_name: The feature name (e.g., 'nom', 'masc', 'sg')

        Returns:
            The category name (e.g., 'case', 'gender', 'number')

        Raises:
            ValueError: If feature name is not recognized
        """
        valid_lexicals: list[str] = []
        for lexical in c.LEXICAL_VALUES:
            if lexical.startswith(lexical_name):
                valid_lexicals.append(lexical)

        if len(valid_lexicals) == 0:
            raise ValueError(f"Unknown lexical: {lexical_name}")
        elif len(valid_lexicals) > 1:
            conflicts = " ".join(valid_lexicals)
            raise ValueError(
                f"Ambiguous lexical: {lexical_name}.  Conflicts with {conflicts}."
            )

        print("LexicalMapper: ", lexical_name, valid_lexicals)
        lexical_name = valid_lexicals.pop()
        return lexical_name
