# tests/lib/templates/test_feature_mapper.py
import pytest

from syntaxis.lib.models import constants as c
from syntaxis.lib.templates.feature_mapper import FeatureMapper


class TestFeatureMapper:
    def test_case_features(self):
        """Case features should map to 'case' category"""
        assert FeatureMapper.get_category(c.NOMINATIVE) == (c.NOMINATIVE, c.CASE)
        assert FeatureMapper.get_category(c.ACCUSATIVE) == (c.ACCUSATIVE, c.CASE)
        assert FeatureMapper.get_category(c.GENITIVE) == (c.GENITIVE, c.CASE)
        assert FeatureMapper.get_category(c.VOCATIVE) == (c.VOCATIVE, c.CASE)

    def test_gender_features(self):
        """Gender features should map to 'gender' category"""
        assert FeatureMapper.get_category(c.MASCULINE) == (c.MASCULINE, c.GENDER)
        assert FeatureMapper.get_category(c.FEMININE) == (c.FEMININE, c.GENDER)
        assert FeatureMapper.get_category(c.NEUTER) == (c.NEUTER, c.GENDER)

    def test_number_features(self):
        """Number features should map to 'number' category"""
        assert FeatureMapper.get_category(c.SINGULAR) == (c.SINGULAR, c.NUMBER)
        assert FeatureMapper.get_category(c.PLURAL) == (c.PLURAL, c.NUMBER)

    def test_tense_features(self):
        """Tense features should map to 'tense' category"""
        assert FeatureMapper.get_category(c.PRESENT) == (c.PRESENT, c.TENSE)
        assert FeatureMapper.get_category(c.AORIST) == (c.AORIST, c.TENSE)
        assert FeatureMapper.get_category(c.PARATATIKOS) == (c.PARATATIKOS, c.TENSE)

    def test_voice_features(self):
        """Voice features should map to 'voice' category"""
        assert FeatureMapper.get_category(c.ACTIVE) == (c.ACTIVE, c.VOICE)
        assert FeatureMapper.get_category(c.PASSIVE) == (c.PASSIVE, c.VOICE)

    def test_person_features(self):
        """Person features should map to 'person' category"""
        assert FeatureMapper.get_category(c.FIRST) == (c.FIRST, c.PERSON)
        assert FeatureMapper.get_category(c.SECOND) == (c.SECOND, c.PERSON)
        assert FeatureMapper.get_category(c.THIRD) == (c.THIRD, c.PERSON)

    def test_unknown_feature(self):
        """Unknown features should raise ValueError"""
        with pytest.raises(ValueError, match="Unknown feature"):
            FeatureMapper.get_category("invalid")
