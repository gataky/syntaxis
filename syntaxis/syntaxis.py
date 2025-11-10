from syntaxis.database import Database
from syntaxis.templates import Template

class Syntaxis:

    def __init__(self):

        self.lexical_manager: Database = Database("./syntaxis.db")
        self.template_parser: Template = Template()

    def generate_sentence(self, template: str):

        parsed = self.template_parser.parse(template)
        for token in parsed.tokens:
            self.lexical_manager.get_random_word(token.pos, **token.__dict__)

        return
