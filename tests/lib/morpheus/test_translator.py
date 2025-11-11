from modern_greek_inflexion import resources

from syntaxis.lib.models import constants as c
from syntaxis.lib.morpheus.translator import translate_forms


def test_translate_forms_set():
    """Test that a set is returned as-is."""
    forms_set = {"word1", "word2"}
    assert translate_forms(forms_set) == forms_set


def test_translate_forms_simple_dict():
    """Test translation of a simple dictionary with MGI keys."""
    input_dict = {resources.MASC: {"άνθρωπος"}}
    expected_dict = {c.MASCULINE: {"άνθρωπος"}}
    assert translate_forms(input_dict) == expected_dict


def test_translate_forms_nested_dict():
    """Test translation of a nested dictionary with MGI keys."""
    input_dict = {resources.MASC: {resources.SG: {resources.NOM: {"άνθρωπος"}}}}
    expected_dict = {c.MASCULINE: {c.SINGULAR: {c.NOMINATIVE: {"άνθρωπος"}}}}
    assert translate_forms(input_dict) == expected_dict


def test_translate_forms_mixed_keys():
    """Test translation with a mix of MGI and non-MGI keys."""
    input_dict = {
        resources.FEM: {"custom_key": {resources.PL: {"γυναίκες"}}},
        "another_key": {"value"},
    }
    expected_dict = {
        c.FEMININE: {"custom_key": {c.PLURAL: {"γυναίκες"}}},
        "another_key": {"value"},
    }
    assert translate_forms(input_dict) == expected_dict


def test_translate_forms_empty_dict():
    """Test translation of an empty dictionary."""
    assert translate_forms({}) == {}
