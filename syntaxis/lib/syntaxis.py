from syntaxis.lib.database import Database
from syntaxis.lib.models.lexical import Lexical
from syntaxis.lib.templates import Template


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

    def generate_sentence(self, template: str) -> list[Lexical]:
        """Generate a list of Greek words matching a grammatical template.

        Parses the template string into grammatical tokens, then retrieves random
        Greek words from the database that match each token's lexical type and
        grammatical features. Each word is returned as a Lexical object that
        contains both the lemma and inflected forms.

        Args:
            template: A template string specifying the sentence structure.
                Format: "[lexical:feature1:feature2:...] [lexical:...]"
                Examples:
                - "[article:nom:masc:sg] [noun:nom:masc:sg]"
                - "[verb:aorist:active:pri:pl]"
                - "[prep] [article:acc:fem:pl] [noun:acc:fem:pl]"

        Returns:
            A list of Lexical objects (Noun, Verb, Adjective, etc.), one for each
            token in the template. Each Lexical object can be converted to a string
            to get the inflected word form, or accessed via .lemma for the base form.

        Raises:
            TemplateParseError: If the template syntax is invalid or features are
                incorrectly specified for a lexical type
            ValueError: If no words in the database match the specified features

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

            Mixed with invariable words:

            >>> template = "[article:nom:masc:sg] [noun:nom:masc:sg] [prep] [article:acc:neut:sg] [noun:acc:neut:sg]"
            >>> words = sx.generate_sentence(template)
            >>> print(" ".join(str(w) for w in words))
            ο άνδρας με το παιδί

        Note:
            The order and specific words returned will vary on each call since
            words are selected randomly from the database. Only the grammatical
            structure is guaranteed to match the template.
        """
        parsed = self.template.parse(template)
        words = []
        for token in parsed.tokens:
            word = self.database.get_random_word(token.lexical, **token.features())
            words.append(word)

        return words
