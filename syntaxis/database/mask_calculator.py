"""Calculate bitmasks for word features by inspecting generated forms."""

from syntaxis.models.enums import (
    PartOfSpeech as POSEnum,
    Number,
    Case,
    Gender,
    Tense,
    Voice,
    Mood,
    Person,
)
from syntaxis.morpheus import Morpheus
from syntaxis.database.bitmasks import build_mask

# Map string keys from modern_greek_inflexion to our enums
STRING_TO_ENUM = {
    # Number
    'sg': Number.SINGULAR,
    'pl': Number.PLURAL,
    # Case
    'nom': Case.NOMINATIVE,
    'voc': Case.VOCATIVE,
    'acc': Case.ACCUSATIVE,
    'gen': Case.GENITIVE,
    # Gender
    'masc': Gender.MASCULINE,
    'fem': Gender.FEMININE,
    'neut': Gender.NEUTER,
    # Tense
    'present': Tense.PRESENT,
    'paratatikos': Tense.PARATATIKOS,
    'aorist': Tense.AORIST,
    # Voice
    'active': Voice.ACTIVE,
    'passive': Voice.PASSIVE,
    # Mood
    'ind': Mood.INDICATIVE,
    'imp': Mood.IMPERATIVE,
    # Person
    'pri': Person.FIRST,
    'sec': Person.SECOND,
    'ter': Person.THIRD,
}


def calculate_masks_for_word(lemma: str, pos: POSEnum) -> dict[str, int]:
    """Calculate bitmask values by inspecting word's available forms.

    Args:
        lemma: The word's base form
        pos: Part of speech

    Returns:
        Dictionary mapping mask column names to integer bitmask values
        (e.g., {'number_mask': 3, 'case_mask': 15})
    """
    # Generate forms using Morpheus
    word = Morpheus.create(lemma, pos)

    masks = {}

    if pos == POSEnum.NOUN:
        # forms[gender][number][case]
        available_numbers = set()
        available_cases = set()

        for gender_dict in word.forms.values():
            for number_key, number_dict in gender_dict.items():
                if number_key in STRING_TO_ENUM:
                    available_numbers.add(STRING_TO_ENUM[number_key])
                for case_key in number_dict.keys():
                    if case_key in STRING_TO_ENUM:
                        available_cases.add(STRING_TO_ENUM[case_key])

        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.VERB:
        # forms[tense][voice][mood][number][person] = set of forms
        available_tenses = set()
        available_voices = set()
        available_moods = set()
        available_numbers = set()
        available_persons = set()

        for tense_key, tense_dict in word.forms.items():
            if tense_key in STRING_TO_ENUM:
                available_tenses.add(STRING_TO_ENUM[tense_key])
            if not isinstance(tense_dict, dict):
                continue
            for voice_key, voice_dict in tense_dict.items():
                if voice_key in STRING_TO_ENUM:
                    available_voices.add(STRING_TO_ENUM[voice_key])
                if not isinstance(voice_dict, dict):
                    continue
                for mood_key, mood_dict in voice_dict.items():
                    if mood_key in STRING_TO_ENUM:
                        available_moods.add(STRING_TO_ENUM[mood_key])
                    if not isinstance(mood_dict, dict):
                        continue
                    for number_key, number_dict in mood_dict.items():
                        if number_key in STRING_TO_ENUM:
                            available_numbers.add(STRING_TO_ENUM[number_key])
                        if not isinstance(number_dict, dict):
                            continue
                        for person_key in number_dict.keys():
                            if person_key in STRING_TO_ENUM:
                                available_persons.add(STRING_TO_ENUM[person_key])

        masks["tense_mask"] = build_mask(available_tenses)
        masks["voice_mask"] = build_mask(available_voices)
        masks["mood_mask"] = build_mask(available_moods)
        masks["number_mask"] = build_mask(available_numbers)
        masks["person_mask"] = build_mask(available_persons)
        masks["case_mask"] = 0  # Verbs don't have case in Greek

    elif pos == POSEnum.ADJECTIVE:
        # forms[pos_type][number][gender][case]
        available_numbers = set()
        available_cases = set()

        for pos_dict in word.forms.values():
            if not isinstance(pos_dict, dict):
                continue
            for number_key, number_dict in pos_dict.items():
                if number_key in STRING_TO_ENUM:
                    available_numbers.add(STRING_TO_ENUM[number_key])
                if not isinstance(number_dict, dict):
                    continue
                for gender_dict in number_dict.values():
                    if not isinstance(gender_dict, dict):
                        continue
                    for case_key in gender_dict.keys():
                        if case_key in STRING_TO_ENUM:
                            available_cases.add(STRING_TO_ENUM[case_key])

        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.ARTICLE:
        # forms[number][gender][case]
        available_numbers = set()
        available_genders = set()
        available_cases = set()

        for number_key, number_dict in word.forms.items():
            if number_key in STRING_TO_ENUM:
                available_numbers.add(STRING_TO_ENUM[number_key])
            for gender_key, gender_dict in number_dict.items():
                if gender_key in STRING_TO_ENUM:
                    available_genders.add(STRING_TO_ENUM[gender_key])
                for case_key in gender_dict.keys():
                    if case_key in STRING_TO_ENUM:
                        available_cases.add(STRING_TO_ENUM[case_key])

        masks["gender_mask"] = build_mask(available_genders)
        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    elif pos == POSEnum.PRONOUN:
        # forms[number][gender][case]
        available_numbers = set()
        available_genders = set()
        available_cases = set()

        for number_key, number_dict in word.forms.items():
            if number_key in STRING_TO_ENUM:
                available_numbers.add(STRING_TO_ENUM[number_key])
            for gender_key, gender_dict in number_dict.items():
                if gender_key in STRING_TO_ENUM:
                    available_genders.add(STRING_TO_ENUM[gender_key])
                for case_key in gender_dict.keys():
                    if case_key in STRING_TO_ENUM:
                        available_cases.add(STRING_TO_ENUM[case_key])

        masks["gender_mask"] = build_mask(available_genders)
        masks["number_mask"] = build_mask(available_numbers)
        masks["case_mask"] = build_mask(available_cases)

    # ADVERB, PREPOSITION, CONJUNCTION have no features
    # Return empty dict

    return masks
