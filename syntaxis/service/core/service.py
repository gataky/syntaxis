"""Business logic layer for Syntaxis API service."""

from syntaxis import Syntaxis


class SyntaxisService:
    """Service layer that wraps Syntaxis core functionality.

    Provides business logic for generating Greek sentences from templates
    and converting lexicals to JSON format for API responses.

    Attributes:
        syntaxis: Syntaxis instance for sentence generation
    """

    def __init__(self, syntaxis: Syntaxis):
        """Initialize service with Syntaxis instance.

        Args:
            syntaxis: Syntaxis instance for generating sentences
        """
        self.syntaxis = syntaxis

    def generate_from_template(self, template: str) -> list[dict]:
        """Generate lexicals from template and convert to JSON.

        Args:
            template: Greek grammar template string

        Returns:
            List of dictionaries representing lexical objects

        Raises:
            TemplateParseError: If template syntax is invalid
            ValueError: If no words match the template features
        """
        lexicals = self.syntaxis.generate_sentence(template)
        return [lexical.to_json() for lexical in lexicals]
