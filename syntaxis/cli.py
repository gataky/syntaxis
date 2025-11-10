import typer
import os
from syntaxis.database import Database
from syntaxis.models.constants import LEXICAL_MAP
from syntaxis.database import seeds
import csv

app = typer.Typer()

@app.command()
def create_db(db_name: str = "syntaxis.db", clear: bool = typer.Option(False, "--clear")):
    """
    Create the database.
    """
    if clear and os.path.exists(db_name):
        os.remove(db_name)
        print(f"Existing database '{db_name}' removed.")
    Database(db_name)
    print(f"Database '{db_name}' created.")

@app.command()
def seed_db(db_name: str = "syntaxis.db", csv_file: str = "data/dictionary.csv"):
    """
    Seed the database with words from a CSV file.
    """
    m = Database(db_name)
    with open(csv_file, "r") as f:
        r = csv.reader(f)
        next(r)
        for line in r:
            lexical = LEXICAL_MAP[line[0]]
            translations = line[1].split(",")
            lemma = line[2]
            m.add_word(lemma, translations, lexical)
    print("Database seeded.")

@app.command()
def seed_pronouns(db_name: str = "syntaxis.db"):
    """
    Seed the database with pronoun data.
    """
    db = Database(db_name)
    seeds.seed_pronouns(db._conn)

if __name__ == "__main__":
    app()
