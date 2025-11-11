import csv
import os

import typer

from syntaxis.lib.database import Database, seeds
from syntaxis.lib.models.constants import LEXICAL_MAP

app = typer.Typer()

DEFAULT_DB_NAME = "syntaxis.db"


@app.command()
def create_db(
    db_name: str = DEFAULT_DB_NAME, clear: bool = typer.Option(False, "--clear")
):
    """
    Create the database.
    """
    if clear and os.path.exists(db_name):
        os.remove(db_name)
        print(f"Existing database '{db_name}' removed.")
    Database(db_name)
    print(f"Database '{db_name}' created.")


@app.command()
def seed_dictionary(
    db_name: str = DEFAULT_DB_NAME, csv_file: str = "data/dictionary.csv"
):
    """
    Seed the database with words from a CSV file.
    """
    m = Database(db_name)
    with open(csv_file, "r") as f:
        r = csv.reader(f)
        next(r)
        count = 0
        for line in r:
            lexical = LEXICAL_MAP[line[0]]
            translations = line[1].split(",")
            lemma = line[2]
            m.add_word(lemma, translations, lexical)
            count += 1
        print(f"Seeded {count} words forms {csv_file} into {db_name}")


@app.command()
def seed_pronouns(db_name: str = DEFAULT_DB_NAME):
    """
    Seed the database with pronoun data.
    """
    db = Database(db_name)
    seeds.pronouns.seed(db._conn)


@app.command()
def seed_articles(db_name: str = DEFAULT_DB_NAME):
    """
    Seed the database with article data.
    """
    db = Database(db_name)
    seeds.articles.seed(db._conn)


if __name__ == "__main__":
    app()
