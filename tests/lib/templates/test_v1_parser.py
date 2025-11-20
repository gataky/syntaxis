from syntaxis.lib.templates.ast import TemplateAST
from syntaxis.lib.templates.v1_parser import V1Parser


class TestV1Parser:
    def test_parse_single_noun(self):
        """Should parse [noun:nom:masc:sg]"""
        template_str = "[noun:nom:masc:sg]"
        result = V1Parser.parse(template_str)

        assert isinstance(result, TemplateAST)
        assert result.version == 1
        assert len(result.groups) == 1

        group = result.groups[0]
        assert len(group.tokens) == 1
        assert group.tokens[0].lexical == "noun"
        assert len(group.group_features) == 3
        assert group.reference_id == 1

    def test_parse_multiple_tokens(self):
        """Should parse [article:nom:masc:sg] [noun:nom:masc:sg]"""
        template_str = "[article:nom:masc:sg] [noun:nom:masc:sg]"
        result = V1Parser.parse(template_str)

        assert len(result.groups) == 2
        assert result.groups[0].tokens[0].lexical == "article"
        assert result.groups[1].tokens[0].lexical == "noun"
        assert result.groups[0].reference_id == 1
        assert result.groups[1].reference_id == 2


class TestV1ParserFeatures:
    def test_parse_verb_full_features(self):
        """Should parse full feature names (present, active)"""
        template_str = "[verb:present:active:ter:sg]"
        result = V1Parser.parse(template_str)

        group = result.groups[0]
        feature_names = [f.name for f in group.group_features]
        assert "present" in feature_names
        assert "active" in feature_names
        assert "ter" in feature_names
        assert "sg" in feature_names

    def test_parse_all_case_features(self):
        """Should parse all case features"""
        for case in ["nom", "gen", "acc", "voc"]:
            template_str = f"[noun:{case}:masc:sg]"
            result = V1Parser.parse(template_str)
            feature_names = [f.name for f in result.groups[0].group_features]
            assert case in feature_names

    def test_parse_all_gender_features(self):
        """Should parse all gender features"""
        for gender in ["masc", "fem", "neut"]:
            template_str = f"[noun:nom:{gender}:sg]"
            result = V1Parser.parse(template_str)
            feature_names = [f.name for f in result.groups[0].group_features]
            assert gender in feature_names

    def test_parse_all_number_features(self):
        """Should parse all number features"""
        for number in ["sg", "pl"]:
            template_str = f"[noun:nom:masc:{number}]"
            result = V1Parser.parse(template_str)
            feature_names = [f.name for f in result.groups[0].group_features]
            assert number in feature_names
