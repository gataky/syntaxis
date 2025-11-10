import os
import csv
import random

from prettytable import PrettyTable
from syntaxis.syntaxis import Syntaxis
from syntaxis.database import Database
from syntaxis.templates import Template


def populate_db():
    m = Database("syntaxis.db")
    with open("dictionary.csv", "r") as f:
        r = csv.reader(f)
        next(r)
        for line in r:
            pos = PartOfSpeechMap[line[0]]
            lemma = line[2]
            translations = line[1].split(",")
            m.add_word(lemma, translations, pos)


def plumbing():
    pass

if __name__ == "__main__":
    # populate_db()
    p = Template()
    l = Database("syntaxis.db")

    while True:
        os.system("clear")
        templates = [
            # "[article:nom:neut:pl] [noun:nom:neut:pl]",
            # "[article:nom:masc:pl] [noun:nom:masc:pl]",
            # "[article:nom:fem:pl]  [noun:nom:fem:pl]",
            # "[article:nom:neut:sg] [noun:nom:neut:sg]",
            # "[article:nom:masc:sg] [noun:nom:masc:sg]",
            # "[article:nom:fem:sg]  [noun:nom:fem:sg]",

            "[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg]",
            "[article:nom:fem:sg]  [adj:nom:fem:sg]  [noun:nom:fem:sg]",
            "[article:nom:neut:sg] [adj:nom:neut:sg] [noun:nom:neut:sg]",
        ]

        template = random.choice(templates)

        parts = p.parse(template)

        table = PrettyTable()
        field_names = []
        for i, token in enumerate(parts.tokens):
            field_names.append(f"{i}:{token.case.value}:{token.number.value}")

        table.field_names = field_names

        words = []
        for token in parts.tokens:
            # table.field_names.append(f"{token.case.value}:{token.number.value}")

            features = {k: v for k, v in token.__dict__.items() if v is not None}

            word = l.get_random_word(**features)

            f = {k: v.value for k, v in token.__dict__.items() if v is not None}
            word.word = word.get_form(**f)

            words.append(word)

        en_sentence = list(map(lambda x: list(x.translations)[0], words))
        table.add_row(en_sentence)
        print(table)
        input("")
        os.system("clear")

        gr_sentence = list(map(lambda x: list(x.word)[0], words))
        table.add_row(gr_sentence)
        print(table)
        input("")
