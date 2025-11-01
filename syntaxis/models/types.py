from syntaxis.models.enums import (
    Case,
    Gender,
    Mood,
    Number,
    PartOfSpeech,
    Person,
    Tense,
    Voice,
)

type Adjective = dict[PartOfSpeech, dict[Number, dict[Case, set[str]]]]
type Adverb = dict[PartOfSpeech, set[str]]
type Article = dict[Number, dict[Gender, dict[Case, set[str]]]]
type Noun = dict[Gender, dict[Number, dict[Case, set[str]]]]
type Numeral = dict[PartOfSpeech, dict[Number, dict[Gender, dict[Case, set[str]]]]]
type Pronoun = dict[Number, dict[Gender, dict[Case, set[str]]]]
type Verb = dict[
    Tense, dict[Voice, dict[Mood, dict[Number, dict[Person, dict[Case, set[str]]]]]]
]

type Preposition = dict[str, set[str]]
type Conjunction = dict[str, set[str]]
