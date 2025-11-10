"""Translation logic for forms dictionaries."""

from syntaxis.morpheus.mappings import MGI_TO_SYNTAXIS


def translate_forms(forms: dict | set) -> dict | set:
    """Recursively translate mgi forms dictionary to syntaxis constants.

    Args:
        forms: Nested dictionary or set from modern_greek_inflexion

    Returns:
        Translated structure with syntaxis constants as keys

    Examples:
        Input:  {resources.MASC: {resources.SG: {resources.NOM: {'άνθρωπος'}}}}
        Output: {'masc': {'sg': {'nom': {'άνθρωπος'}}}}
    """
    if isinstance(forms, set):
        return forms  # Terminal case: set of word forms

    if isinstance(forms, dict):
        translated = {}
        for key, value in forms.items():
            # Translate key if it's an mgi constant, otherwise keep as-is
            new_key = MGI_TO_SYNTAXIS.get(key, key)
            # Recursively translate nested structures
            translated[new_key] = translate_forms(value)
        return translated

    return forms  # Fallback for any other type
