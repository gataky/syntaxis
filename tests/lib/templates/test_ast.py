# tests/lib/templates/test_ast.py
from syntaxis.lib.templates.ast import Feature, Group, POSToken, TemplateAST


class TestFeature:
    def test_feature_creation(self):
        """Feature should store name and category"""
        feature = Feature(name="nom", category="case")
        assert feature.name == "nom"
        assert feature.category == "case"

    def test_feature_equality(self):
        """Features with same name and category should be equal"""
        f1 = Feature(name="nom", category="case")
        f2 = Feature(name="nom", category="case")
        assert f1 == f2

    def test_feature_inequality(self):
        """Features with different values should not be equal"""
        f1 = Feature(name="nom", category="case")
        f2 = Feature(name="acc", category="case")
        assert f1 != f2


class TestPOSToken:
    def test_postoken_without_direct_features(self):
        """POSToken should store lexical with empty direct features"""
        token = POSToken(lexical="noun", direct_features=[])
        assert token.lexical == "noun"
        assert token.direct_features == []

    def test_postoken_with_direct_features(self):
        """POSToken should store lexical with direct features"""
        features = [Feature(name="fem", category="gender")]
        token = POSToken(lexical="noun", direct_features=features)
        assert token.lexical == "noun"
        assert len(token.direct_features) == 1
        assert token.direct_features[0].name == "fem"


class TestGroup:
    def test_group_basic(self):
        """Group should store tokens, features, and IDs"""
        tokens = [POSToken(lexical="noun", direct_features=[])]
        features = [Feature(name="nom", category="case")]
        group = Group(
            tokens=tokens, group_features=features, reference_id=1, references=None
        )
        assert len(group.tokens) == 1
        assert len(group.group_features) == 1
        assert group.reference_id == 1
        assert group.references is None

    def test_group_with_reference(self):
        """Group can reference another group"""
        tokens = [POSToken(lexical="pronoun", direct_features=[])]
        group = Group(
            tokens=tokens,
            group_features=[],
            reference_id=2,
            references=1,  # References group 1
        )
        assert group.references == 1
        assert group.reference_id == 2


class TestTemplateAST:
    def test_template_ast_v1(self):
        """TemplateAST should store groups and version"""
        group = Group(
            tokens=[POSToken(lexical="noun", direct_features=[])],
            group_features=[Feature(name="nom", category="case")],
            reference_id=1,
            references=None,
        )
        template = TemplateAST(groups=[group], version=1)
        assert len(template.groups) == 1
        assert template.version == 1

    def test_template_ast_v2(self):
        """TemplateAST should support version 2"""
        groups = [
            Group(
                tokens=[POSToken(lexical="article", direct_features=[])],
                group_features=[Feature(name="nom", category="case")],
                reference_id=1,
                references=None,
            ),
            Group(
                tokens=[POSToken(lexical="noun", direct_features=[])],
                group_features=[],
                reference_id=2,
                references=1,
            ),
        ]
        template = TemplateAST(groups=groups, version=2)
        assert len(template.groups) == 2
        assert template.version == 2
        assert template.groups[1].references == 1
