import csv

from syntaxis.syntaxis import Syntaxis
from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeechMap
from syntaxis.templates.parser import TemplateParser


def populate_db():
    m = LexicalManager("syntaxis.db")
    with open("dictionary.csv", "r") as f:
        r = csv.reader(f)
        for line in r:
            pos = PartOfSpeechMap[line[0]]
            lemma = line[2]
            translations = line[1].split(",")
            m.add_word(lemma, translations, pos)



if __name__ == "__main__":

    p = TemplateParser()
    l = LexicalManager("syntaxis.db")

    template = "[article:nom:neut:pl] [noun:nom:neut:pl] [verb:present:active:ter:pl]"

    parts = p.parse(template)

    words = []
    for token in parts.tokens:

        features = {k: v for k, v in token.__dict__.items() if v is not None}

        word = l.get_random_word(**features)
        words.append(word)
