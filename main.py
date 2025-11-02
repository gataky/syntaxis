import csv

from syntaxis.database.manager import LexicalManager
from syntaxis.models.enums import PartOfSpeechMap


def main():

    m = LexicalManager("test.db")

    with open("dictionary.csv", "r") as f:
        r = csv.reader(f)
        next(r)

        for line in r:
            print(line)

            pos = PartOfSpeechMap[line[0]]
            lemma = line[2]
            translations = line[1].split(",")

            m.add_word(lemma, translations, pos)


if __name__ == "__main__":
    main()
