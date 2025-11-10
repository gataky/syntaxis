from syntaxis.database import Database
from syntaxis.models.lexical import Lexical
from syntaxis.templates import Template


class Syntaxis:

    def __init__(self):

        self.database: Database = Database("./syntaxis.db")
        self.template: Template = Template()

    def generate_sentence(self, template: str) -> list[Lexical]:

        parsed = self.template.parse(template)
        words = []
        for token in parsed.tokens:
            word = self.database.get_random_word(token.lexical, **token.features())
            words.append(word)

        return words
