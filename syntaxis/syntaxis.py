from syntaxis.database.manager import LexicalManager
from syntaxis.templates.parser import TemplateParser

class Syntaxis:

    def __init__(self):

        self.lexical_manager: LexicalManager = LexicalManager("./syntaxis.db")
        self.template_parser: TemplateParser = TemplateParser()

    def generate_sentence(self, template: str):

        parsed = self.template_parser.parse(template)
        for token in parsed.tokens:
            self.lexical_manager.get_random_word(token.pos, **token.__dict__)

        return
