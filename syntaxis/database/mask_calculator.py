"""Calculate bitmasks for word features by inspecting generated forms."""

from syntaxis.database.bitmasks import build_mask, enum_to_bit
from syntaxis.models.enums import (
    Case,
    Gender,
    Mood,
    Number,
)
from syntaxis.models.enums import PartOfSpeech as POSEnum
from syntaxis.models.enums import (
    Person,
    Tense,
    Voice,
)
from syntaxis.morpheus import Morpheus

# Map string keys from modern_greek_inflexion to our enums
STRING_TO_ENUM = {
    # Number
    "sg": Number.SINGULAR,
    "pl": Number.PLURAL,
    # Case
    "nom": Case.NOMINATIVE,
    "voc": Case.VOCATIVE,
    "acc": Case.ACCUSATIVE,
    "gen": Case.GENITIVE,
    # Gender
    "masc": Gender.MASCULINE,
    "fem": Gender.FEMININE,
    "neut": Gender.NEUTER,
    # Tense
    "present": Tense.PRESENT,
    "paratatikos": Tense.PARATATIKOS,
    "aorist": Tense.AORIST,
    # Voice
    "active": Voice.ACTIVE,
    "passive": Voice.PASSIVE,
    # Mood
    "ind": Mood.INDICATIVE,
    "imp": Mood.IMPERATIVE,
    # Person
    "pri": Person.FIRST,
    "sec": Person.SECOND,
    "ter": Person.THIRD,
}


def _collect_keys(d: dict) -> set[str]:
    """Recursively collect all keys from a nested dictionary."""
    keys = set()
    for k, v in d.items():
        keys.add(k)
        if isinstance(v, dict):
            keys.update(_collect_keys(v))
    return keys


POS_FEATURE_MAP = {
    POSEnum.NOUN: [Number, Case, Gender],
    POSEnum.VERB: [Tense, Voice, Mood, Number, Person],
    POSEnum.ADJECTIVE: [Number, Case, Gender],
    POSEnum.ARTICLE: [Number, Case, Gender],
    POSEnum.PRONOUN: [Number, Case, Gender, Person],
}

FEATURE_TO_MASK_NAME = {
    Number: "number_mask",
    Case: "case_mask",
    Gender: "gender_mask",
    Tense: "tense_mask",
    Voice: "voice_mask",
    Mood: "mood_mask",
    Person: "person_mask",
}


def calculate_masks_for_word(lemma: str, pos: POSEnum) -> dict[str, int]:
    """Calculate bitmask values by inspecting word's available forms."""
    word = Morpheus.create(lemma, pos)
    if not word.forms:
        return {}

    all_keys = _collect_keys(word.forms)
    masks = {}

    if pos not in POS_FEATURE_MAP:
        return {}

    for feature_enum in POS_FEATURE_MAP[pos]:
        mask_name = FEATURE_TO_MASK_NAME[feature_enum]
        mask_value = 0
        for key_str, enum_val in STRING_TO_ENUM.items():
            if key_str in all_keys and isinstance(enum_val, feature_enum):
                mask_value |= enum_to_bit(enum_val)
        masks[mask_name] = mask_value

    if pos == POSEnum.VERB:
        masks["case_mask"] = 0

    return masks
