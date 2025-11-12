# Template V2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement V2 template syntax with feature grouping, references, and direct overrides while maintaining full V1 backward compatibility.

**Architecture:** Three-layer design with separate V1/V2 parsers producing unified AST, consumed by existing generator. Version detection routes templates to correct parser based on opening character.

**Tech Stack:** Python 3.11+, pytest, dataclasses, regex

---

## Task 1: Create AST Data Classes

**Files:**
- Create: `syntaxis/lib/templates/ast.py`
- Test: `tests/lib/templates/test_ast.py`

**Step 1: Write the failing test for Feature class**

Create test file with basic Feature tests:

```python
# tests/lib/templates/test_ast.py
import pytest
from syntaxis.lib.templates.ast import Feature, POSToken, Group, TemplateAST


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
```


**Step 2: Write minimal Feature implementation**

```python
# syntaxis/lib/templates/ast.py
"""AST classes for template parsing (V1 and V2)"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Feature:
    """Represents a grammatical feature (nom, masc, sg, etc.)

    Attributes:
        name: The feature value (e.g., 'nom', 'masc', 'sg')
        category: The feature category (e.g., 'case', 'gender', 'number')
    """
    name: str
    category: str
```

**Step 3: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_ast.py::TestFeature -v
```

Expected: All 3 tests PASS

```bash
git add syntaxis/lib/templates/ast.py tests/lib/templates/test_ast.py
git commit -m "feat: add Feature dataclass for AST"
```

---

## Task 2: Add POSToken Class

**Files:**
- Modify: `syntaxis/lib/templates/ast.py`
- Modify: `tests/lib/templates/test_ast.py`

**Step 1: Write the failing test for POSToken**

```python
# Add to tests/lib/templates/test_ast.py

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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_ast.py::TestPOSToken -v
```

Expected: `NameError: name 'POSToken' is not defined`

**Step 3: Write minimal POSToken implementation**

Add to `syntaxis/lib/templates/ast.py`:

```python
@dataclass
class POSToken:
    """Individual lexical with optional direct features

    Attributes:
        lexical: The part of speech type (e.g., 'noun', 'verb', 'adj')
        direct_features: Features applied directly to this lexical (overrides group features)
    """
    lexical: str
    direct_features: list[Feature]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_ast.py::TestPOSToken -v
```

Expected: All 2 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/templates/ast.py tests/lib/templates/test_ast.py
git commit -m "feat: add POSToken dataclass for AST"
```

---

## Task 3: Add Group Class

**Files:**
- Modify: `syntaxis/lib/templates/ast.py`
- Modify: `tests/lib/templates/test_ast.py`

**Step 1: Write the failing test for Group**

```python
# Add to tests/lib/templates/test_ast.py

class TestGroup:
    def test_group_basic(self):
        """Group should store tokens, features, and IDs"""
        tokens = [POSToken(lexical="noun", direct_features=[])]
        features = [Feature(name="nom", category="case")]
        group = Group(
            tokens=tokens,
            group_features=features,
            reference_id=1,
            references=None
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
            references=1  # References group 1
        )
        assert group.references == 1
        assert group.reference_id == 2
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_ast.py::TestGroup -v
```

Expected: `NameError: name 'Group' is not defined`

**Step 3: Write minimal Group implementation**

Add to `syntaxis/lib/templates/ast.py`:

```python
@dataclass
class Group:
    """A group of lexicals with shared features

    Attributes:
        tokens: List of POSToken objects in this group
        group_features: Features applied to all tokens in the group
        reference_id: Auto-generated position (1, 2, 3...) for this group
        references: Points to another group's reference_id ($1, $2, etc.)
    """
    tokens: list[POSToken]
    group_features: list[Feature]
    reference_id: Optional[int]
    references: Optional[int]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_ast.py::TestGroup -v
```

Expected: All 2 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/templates/ast.py tests/lib/templates/test_ast.py
git commit -m "feat: add Group dataclass for AST"
```

---

## Task 4: Add TemplateAST Class

**Files:**
- Modify: `syntaxis/lib/templates/ast.py`
- Modify: `tests/lib/templates/test_ast.py`

**Step 1: Write the failing test for TemplateAST**

```python
# Add to tests/lib/templates/test_ast.py

class TestTemplateAST:
    def test_template_ast_v1(self):
        """TemplateAST should store groups and version"""
        group = Group(
            tokens=[POSToken(lexical="noun", direct_features=[])],
            group_features=[Feature(name="nom", category="case")],
            reference_id=1,
            references=None
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
                references=None
            ),
            Group(
                tokens=[POSToken(lexical="noun", direct_features=[])],
                group_features=[],
                reference_id=2,
                references=1
            )
        ]
        template = TemplateAST(groups=groups, version=2)
        assert len(template.groups) == 2
        assert template.version == 2
        assert template.groups[1].references == 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_ast.py::TestTemplateAST -v
```

Expected: `NameError: name 'TemplateAST' is not defined`

**Step 3: Write minimal TemplateAST implementation**

Add to `syntaxis/lib/templates/ast.py`:

```python
@dataclass
class TemplateAST:
    """Top-level AST for a template

    Attributes:
        groups: List of Group objects representing the template structure
        version: Template syntax version (1 for V1, 2 for V2)
    """
    groups: list[Group]
    version: int
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_ast.py::TestTemplateAST -v
```

Expected: All 2 tests PASS

**Step 5: Run all AST tests**

```bash
pytest tests/lib/templates/test_ast.py -v
```

Expected: All 9 tests PASS

**Step 6: Commit**

```bash
git add syntaxis/lib/templates/ast.py tests/lib/templates/test_ast.py
git commit -m "feat: add TemplateAST dataclass for AST"
```

---

## Task 5: Create Feature Category Mapper

**Files:**
- Create: `syntaxis/lib/templates/feature_mapper.py`
- Test: `tests/lib/templates/test_feature_mapper.py`

**Step 1: Write the failing test for feature category mapping**

```python
# tests/lib/templates/test_feature_mapper.py
import pytest
from syntaxis.lib.templates.feature_mapper import FeatureMapper


class TestFeatureMapper:
    def test_case_features(self):
        """Case features should map to 'case' category"""
        assert FeatureMapper.get_category("nom") == "case"
        assert FeatureMapper.get_category("acc") == "case"
        assert FeatureMapper.get_category("gen") == "case"
        assert FeatureMapper.get_category("voc") == "case"

    def test_gender_features(self):
        """Gender features should map to 'gender' category"""
        assert FeatureMapper.get_category("masc") == "gender"
        assert FeatureMapper.get_category("fem") == "gender"
        assert FeatureMapper.get_category("neut") == "gender"

    def test_number_features(self):
        """Number features should map to 'number' category"""
        assert FeatureMapper.get_category("sg") == "number"
        assert FeatureMapper.get_category("pl") == "number"

    def test_tense_features(self):
        """Tense features should map to 'tense' category"""
        assert FeatureMapper.get_category("pres") == "tense"
        assert FeatureMapper.get_category("aorist") == "tense"
        assert FeatureMapper.get_category("paratatikos") == "tense"

    def test_voice_features(self):
        """Voice features should map to 'voice' category"""
        assert FeatureMapper.get_category("act") == "voice"
        assert FeatureMapper.get_category("pass") == "voice"

    def test_person_features(self):
        """Person features should map to 'person' category"""
        assert FeatureMapper.get_category("pri") == "person"
        assert FeatureMapper.get_category("sec") == "person"
        assert FeatureMapper.get_category("ter") == "person"

    def test_unknown_feature(self):
        """Unknown features should raise ValueError"""
        with pytest.raises(ValueError, match="Unknown feature"):
            FeatureMapper.get_category("invalid")
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_feature_mapper.py -v
```

Expected: `ModuleNotFoundError: No module named 'syntaxis.lib.templates.feature_mapper'`

**Step 3: Write minimal FeatureMapper implementation**

```python
# syntaxis/lib/templates/feature_mapper.py
"""Maps feature names to their grammatical categories"""


class FeatureMapper:
    """Maps feature names to grammatical categories"""

    # Feature category mappings from design document
    FEATURE_CATEGORIES = {
        # Case
        "nom": "case",
        "gen": "case",
        "acc": "case",
        "voc": "case",

        # Gender
        "masc": "gender",
        "fem": "gender",
        "neut": "gender",

        # Number
        "sg": "number",
        "pl": "number",

        # Tense
        "pres": "tense",
        "aorist": "tense",
        "paratatikos": "tense",

        # Voice
        "act": "voice",
        "pass": "voice",

        # Person
        "pri": "person",
        "sec": "person",
        "ter": "person",
    }

    @classmethod
    def get_category(cls, feature_name: str) -> str:
        """Get the grammatical category for a feature name

        Args:
            feature_name: The feature name (e.g., 'nom', 'masc', 'sg')

        Returns:
            The category name (e.g., 'case', 'gender', 'number')

        Raises:
            ValueError: If feature name is not recognized
        """
        if feature_name not in cls.FEATURE_CATEGORIES:
            raise ValueError(f"Unknown feature: {feature_name}")
        return cls.FEATURE_CATEGORIES[feature_name]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_feature_mapper.py -v
```

Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/templates/feature_mapper.py tests/lib/templates/test_feature_mapper.py
git commit -m "feat: add FeatureMapper for category detection"
```

---

## Task 6: Create V2 Parser - Basic Structure

**Files:**
- Create: `syntaxis/lib/templates/v2_parser.py`
- Test: `tests/lib/templates/test_v2_parser.py`

**Step 1: Write the failing test for basic V2 parsing**

```python
# tests/lib/templates/test_v2_parser.py
import pytest
from syntaxis.lib.templates.v2_parser import V2Parser
from syntaxis.lib.templates.ast import TemplateAST, Group, POSToken, Feature


class TestV2ParserBasic:
    def test_parse_single_group_single_token(self):
        """Should parse (noun)@{nom:masc:sg}"""
        template_str = "(noun)@{nom:masc:sg}"
        result = V2Parser.parse(template_str)

        assert isinstance(result, TemplateAST)
        assert result.version == 2
        assert len(result.groups) == 1

        group = result.groups[0]
        assert len(group.tokens) == 1
        assert group.tokens[0].lexical == "noun"
        assert len(group.group_features) == 3
        assert group.reference_id == 1
        assert group.references is None

    def test_parse_single_group_multiple_tokens(self):
        """Should parse (article adj noun)@{nom:masc:sg}"""
        template_str = "(article adj noun)@{nom:masc:sg}"
        result = V2Parser.parse(template_str)

        assert len(result.groups) == 1
        group = result.groups[0]
        assert len(group.tokens) == 3
        assert group.tokens[0].lexical == "article"
        assert group.tokens[1].lexical == "adj"
        assert group.tokens[2].lexical == "noun"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserBasic -v
```

Expected: `ModuleNotFoundError: No module named 'syntaxis.lib.templates.v2_parser'`

**Step 3: Write minimal V2Parser skeleton**

```python
# syntaxis/lib/templates/v2_parser.py
"""V2 template parser - handles grouping syntax with references"""
import re
from syntaxis.lib.templates.ast import TemplateAST, Group, POSToken, Feature
from syntaxis.lib.templates.feature_mapper import FeatureMapper


class V2Parser:
    """Parser for V2 template syntax: (lexical1 lexical2)@{features}"""

    @classmethod
    def parse(cls, template_str: str) -> TemplateAST:
        """Parse a V2 template string into an AST

        Args:
            template_str: V2 template string like "(noun adj)@{nom:masc:sg}"

        Returns:
            TemplateAST object

        Raises:
            ValueError: If template syntax is invalid
        """
        template_str = template_str.strip()
        groups = cls._parse_groups(template_str)
        return TemplateAST(groups=groups, version=2)

    @classmethod
    def _parse_groups(cls, template_str: str) -> list[Group]:
        """Parse all groups from template string"""
        groups = []
        reference_id = 1

        # Pattern: (tokens)@{features} or (tokens)@$N
        group_pattern = r'\(([^)]+)\)@(\{[^}]+\}|\$\d+)'

        for match in re.finditer(group_pattern, template_str):
            tokens_str = match.group(1)
            features_str = match.group(2)

            # Parse tokens
            tokens = cls._parse_tokens(tokens_str)

            # Parse features or reference
            if features_str.startswith('$'):
                # Reference to another group
                ref_id = int(features_str[1:])
                group = Group(
                    tokens=tokens,
                    group_features=[],
                    reference_id=reference_id,
                    references=ref_id
                )
            else:
                # Direct features
                features = cls._parse_features(features_str)
                group = Group(
                    tokens=tokens,
                    group_features=features,
                    reference_id=reference_id,
                    references=None
                )

            groups.append(group)
            reference_id += 1

        return groups

    @classmethod
    def _parse_tokens(cls, tokens_str: str) -> list[POSToken]:
        """Parse space-separated tokens, handling direct features"""
        tokens = []

        # Pattern: token or token{features}
        token_pattern = r'(\w+)(?:\{([^}]+)\})?'

        for token_match in re.finditer(token_pattern, tokens_str):
            lexical = token_match.group(1)
            direct_features_str = token_match.group(2)

            if direct_features_str:
                direct_features = cls._parse_features(f"{{{direct_features_str}}}")
            else:
                direct_features = []

            tokens.append(POSToken(lexical=lexical, direct_features=direct_features))

        return tokens

    @classmethod
    def _parse_features(cls, features_str: str) -> list[Feature]:
        """Parse feature string like {nom:masc:sg} into Feature objects"""
        # Remove braces
        features_str = features_str.strip('{}')

        # Split by colon
        feature_names = features_str.split(':')

        features = []
        for name in feature_names:
            name = name.strip()
            if name:
                category = FeatureMapper.get_category(name)
                features.append(Feature(name=name, category=category))

        return features
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserBasic -v
```

Expected: All 2 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/templates/v2_parser.py tests/lib/templates/test_v2_parser.py
git commit -m "feat: add V2Parser basic structure and group parsing"
```

---

## Task 7: Add V2 Parser - Multiple Groups

**Files:**
- Modify: `tests/lib/templates/test_v2_parser.py`

**Step 1: Write the failing test for multiple groups**

```python
# Add to tests/lib/templates/test_v2_parser.py

class TestV2ParserMultipleGroups:
    def test_parse_two_groups(self):
        """Should parse (article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"""
        template_str = "(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"
        result = V2Parser.parse(template_str)

        assert len(result.groups) == 2

        # First group
        assert result.groups[0].reference_id == 1
        assert len(result.groups[0].tokens) == 2
        assert result.groups[0].tokens[0].lexical == "article"
        assert result.groups[0].tokens[1].lexical == "noun"

        # Second group
        assert result.groups[1].reference_id == 2
        assert len(result.groups[1].tokens) == 1
        assert result.groups[1].tokens[0].lexical == "verb"

    def test_parse_three_groups(self):
        """Should parse three groups with auto-incrementing IDs"""
        template_str = "(article)@{nom:sg} (noun)@{masc} (verb)@{pres:act}"
        result = V2Parser.parse(template_str)

        assert len(result.groups) == 3
        assert result.groups[0].reference_id == 1
        assert result.groups[1].reference_id == 2
        assert result.groups[2].reference_id == 3
```

**Step 2: Run test to verify it passes (should already pass)**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserMultipleGroups -v
```

Expected: All 2 tests PASS (implementation already handles this)

**Step 3: Commit**

```bash
git add tests/lib/templates/test_v2_parser.py
git commit -m "test: add V2Parser tests for multiple groups"
```

---

## Task 8: Add V2 Parser - Group References

**Files:**
- Modify: `tests/lib/templates/test_v2_parser.py`

**Step 1: Write the failing test for group references**

```python
# Add to tests/lib/templates/test_v2_parser.py

class TestV2ParserReferences:
    def test_parse_simple_reference(self):
        """Should parse (article noun)@{nom:masc:sg} (pronoun)@$1"""
        template_str = "(article noun)@{nom:masc:sg} (pronoun)@$1"
        result = V2Parser.parse(template_str)

        assert len(result.groups) == 2
        assert result.groups[0].references is None
        assert result.groups[1].references == 1
        assert result.groups[1].group_features == []

    def test_parse_chain_reference(self):
        """Should parse three groups where last references first"""
        template_str = "(article)@{nom:sg} (noun)@{masc} (adj)@$1"
        result = V2Parser.parse(template_str)

        assert result.groups[2].references == 1
        assert result.groups[2].reference_id == 3
```

**Step 2: Run test to verify it passes (should already pass)**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserReferences -v
```

Expected: All 2 tests PASS

**Step 3: Commit**

```bash
git add tests/lib/templates/test_v2_parser.py
git commit -m "test: add V2Parser tests for group references"
```

---

## Task 9: Add V2 Parser - Direct Features

**Files:**
- Modify: `tests/lib/templates/test_v2_parser.py`

**Step 1: Write the failing test for direct features**

```python
# Add to tests/lib/templates/test_v2_parser.py

class TestV2ParserDirectFeatures:
    def test_parse_direct_feature_single(self):
        """Should parse (article noun{fem})@{nom:sg}"""
        template_str = "(article noun{fem})@{nom:sg}"
        result = V2Parser.parse(template_str)

        group = result.groups[0]
        assert len(group.tokens) == 2

        # Article has no direct features
        assert group.tokens[0].lexical == "article"
        assert group.tokens[0].direct_features == []

        # Noun has direct feature 'fem'
        assert group.tokens[1].lexical == "noun"
        assert len(group.tokens[1].direct_features) == 1
        assert group.tokens[1].direct_features[0].name == "fem"
        assert group.tokens[1].direct_features[0].category == "gender"

    def test_parse_direct_features_multiple(self):
        """Should parse (noun{nom:fem})@{sg}"""
        template_str = "(noun{nom:fem})@{sg}"
        result = V2Parser.parse(template_str)

        token = result.groups[0].tokens[0]
        assert len(token.direct_features) == 2

        # Check features
        feature_names = [f.name for f in token.direct_features]
        assert "nom" in feature_names
        assert "fem" in feature_names
```

**Step 2: Run test to verify it passes (should already pass)**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserDirectFeatures -v
```

Expected: All 2 tests PASS

**Step 3: Commit**

```bash
git add tests/lib/templates/test_v2_parser.py
git commit -m "test: add V2Parser tests for direct features"
```

---

## Task 10: Add V2 Parser Validation - Reference Checks

**Files:**
- Modify: `syntaxis/lib/templates/v2_parser.py`
- Modify: `tests/lib/templates/test_v2_parser.py`

**Step 1: Write the failing test for reference validation**

```python
# Add to tests/lib/templates/test_v2_parser.py

class TestV2ParserValidation:
    def test_invalid_reference_not_exists(self):
        """Should raise error if reference points to non-existent group"""
        template_str = "(noun)@$5"
        with pytest.raises(ValueError, match="Reference \\$5 does not exist"):
            V2Parser.parse(template_str)

    def test_forward_reference(self):
        """Should raise error if reference points forward"""
        template_str = "(noun)@$2 (article)@{nom:sg}"
        with pytest.raises(ValueError, match="Reference \\$2 points forward"):
            V2Parser.parse(template_str)

    def test_valid_backward_reference(self):
        """Should allow backward reference"""
        template_str = "(article)@{nom:sg} (noun)@$1"
        result = V2Parser.parse(template_str)
        assert result.groups[1].references == 1
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserValidation -v
```

Expected: Tests FAIL (validation not implemented)

**Step 3: Add validation to V2Parser**

Add method to `syntaxis/lib/templates/v2_parser.py`:

```python
    @classmethod
    def parse(cls, template_str: str) -> TemplateAST:
        """Parse a V2 template string into an AST

        Args:
            template_str: V2 template string like "(noun adj)@{nom:masc:sg}"

        Returns:
            TemplateAST object

        Raises:
            ValueError: If template syntax is invalid
        """
        template_str = template_str.strip()
        groups = cls._parse_groups(template_str)
        cls._validate_references(groups)  # Add this line
        return TemplateAST(groups=groups, version=2)

    @classmethod
    def _validate_references(cls, groups: list[Group]) -> None:
        """Validate that all group references are valid

        Raises:
            ValueError: If reference is invalid (forward or non-existent)
        """
        for i, group in enumerate(groups):
            if group.references is not None:
                ref_id = group.references
                current_position = i + 1  # 1-indexed

                # Check if reference exists
                if ref_id > len(groups):
                    raise ValueError(
                        f"Reference ${ref_id} does not exist "
                        f"(only {len(groups)} groups defined)"
                    )

                # Check if reference points backward
                if ref_id >= current_position:
                    raise ValueError(
                        f"Reference ${ref_id} points forward to group {ref_id} "
                        f"(current group is {current_position})"
                    )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserValidation -v
```

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/templates/v2_parser.py tests/lib/templates/test_v2_parser.py
git commit -m "feat: add V2Parser reference validation"
```

---

## Task 11: Add V2 Parser Validation - Syntax Errors

**Files:**
- Modify: `syntaxis/lib/templates/v2_parser.py`
- Modify: `tests/lib/templates/test_v2_parser.py`

**Step 1: Write the failing test for syntax validation**

```python
# Add to tests/lib/templates/test_v2_parser.py TestV2ParserValidation class

    def test_unclosed_parenthesis(self):
        """Should raise error for unclosed group"""
        template_str = "(article noun@{nom:sg}"
        with pytest.raises(ValueError, match="Unclosed group"):
            V2Parser.parse(template_str)

    def test_unclosed_brace(self):
        """Should raise error for unclosed brace"""
        template_str = "(article)@{nom:sg"
        with pytest.raises(ValueError, match="Unclosed brace"):
            V2Parser.parse(template_str)

    def test_empty_group(self):
        """Should raise error for empty group"""
        template_str = "()@{nom:sg}"
        with pytest.raises(ValueError, match="Empty group"):
            V2Parser.parse(template_str)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserValidation::test_unclosed_parenthesis -v
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserValidation::test_unclosed_brace -v
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserValidation::test_empty_group -v
```

Expected: Tests FAIL

**Step 3: Add syntax validation**

Modify `_parse_groups` in `syntaxis/lib/templates/v2_parser.py`:

```python
    @classmethod
    def _parse_groups(cls, template_str: str) -> list[Group]:
        """Parse all groups from template string"""
        # Validate balanced parentheses and braces
        if template_str.count('(') != template_str.count(')'):
            raise ValueError("Unclosed group (mismatched parentheses)")
        if template_str.count('{') != template_str.count('}'):
            raise ValueError("Unclosed brace (mismatched braces)")

        groups = []
        reference_id = 1

        # Pattern: (tokens)@{features} or (tokens)@$N
        group_pattern = r'\(([^)]+)\)@(\{[^}]+\}|\$\d+)'

        for match in re.finditer(group_pattern, template_str):
            tokens_str = match.group(1).strip()

            # Check for empty group
            if not tokens_str:
                raise ValueError("Empty group (no tokens specified)")

            features_str = match.group(2)

            # Parse tokens
            tokens = cls._parse_tokens(tokens_str)

            # Parse features or reference
            if features_str.startswith('$'):
                # Reference to another group
                ref_id = int(features_str[1:])
                group = Group(
                    tokens=tokens,
                    group_features=[],
                    reference_id=reference_id,
                    references=ref_id
                )
            else:
                # Direct features
                features = cls._parse_features(features_str)
                group = Group(
                    tokens=tokens,
                    group_features=features,
                    reference_id=reference_id,
                    references=None
                )

            groups.append(group)
            reference_id += 1

        return groups
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserValidation -v
```

Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add syntaxis/lib/templates/v2_parser.py tests/lib/templates/test_v2_parser.py
git commit -m "feat: add V2Parser syntax validation"
```

---

## Task 12: Extract V1 Parser from Existing Code

**Files:**
- Create: `syntaxis/lib/templates/v1_parser.py`
- Test: `tests/lib/templates/test_v1_parser.py`
- Modify: `syntaxis/lib/templates/api.py`

**Step 1: Write test that V1Parser produces same AST**

```python
# tests/lib/templates/test_v1_parser.py
import pytest
from syntaxis.lib.templates.v1_parser import V1Parser
from syntaxis.lib.templates.ast import TemplateAST


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/templates/test_v1_parser.py -v
```

Expected: `ModuleNotFoundError: No module named 'syntaxis.lib.templates.v1_parser'`

**Step 3: Read existing V1 parser code**

```bash
# No command needed - just examine syntaxis/lib/templates/api.py
```

**Step 4: Create V1Parser that wraps existing logic**

```python
# syntaxis/lib/templates/v1_parser.py
"""V1 template parser - handles bracket syntax [lexical:features]"""
from syntaxis.lib.templates.ast import TemplateAST, Group, POSToken, Feature
from syntaxis.lib.templates.api import Template
from syntaxis.lib.templates.feature_mapper import FeatureMapper


class V1Parser:
    """Parser for V1 template syntax: [lexical:feature1:feature2:...]"""

    @classmethod
    def parse(cls, template_str: str) -> TemplateAST:
        """Parse a V1 template string into an AST

        Args:
            template_str: V1 template string like "[noun:nom:masc:sg]"

        Returns:
            TemplateAST object with version=1
        """
        # Use existing V1 parser
        parsed = Template.parse(template_str)

        # Convert to AST format
        groups = []
        for i, token in enumerate(parsed.tokens):
            # Convert token features to Feature objects
            features = []
            for feature_name in token.features:
                category = FeatureMapper.get_category(feature_name)
                features.append(Feature(name=feature_name, category=category))

            # Create single-token group (V1 doesn't support grouping)
            pos_token = POSToken(lexical=token.lexical, direct_features=[])
            group = Group(
                tokens=[pos_token],
                group_features=features,
                reference_id=i + 1,
                references=None
            )
            groups.append(group)

        return TemplateAST(groups=groups, version=1)
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/lib/templates/test_v1_parser.py -v
```

Expected: All 2 tests PASS

**Step 6: Commit**

```bash
git add syntaxis/lib/templates/v1_parser.py tests/lib/templates/test_v1_parser.py
git commit -m "feat: add V1Parser to convert existing parser to AST"
```

---

## Task 13: Add Version Detection to Syntaxis

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/lib/test_syntaxis.py`

**Step 1: Write failing test for version detection**

```python
# Add to tests/lib/test_syntaxis.py

class TestVersionDetection:
    def test_detect_v1_template(self, syntaxis_instance):
        """Should detect V1 template starting with ["""
        template = "[noun:nom:masc:sg]"
        # This should not raise an error
        result = syntaxis_instance.generate_sentence(template)
        assert len(result) == 1

    def test_detect_v2_template(self, syntaxis_instance):
        """Should detect V2 template starting with ("""
        template = "(noun)@{nom:masc:sg}"
        # This should not raise an error
        result = syntaxis_instance.generate_sentence(template)
        assert len(result) == 1

    def test_invalid_template_start(self, syntaxis_instance):
        """Should raise error for invalid template format"""
        template = "noun:nom:masc:sg"
        with pytest.raises(ValueError, match="Invalid template format"):
            syntaxis_instance.generate_sentence(template)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/test_syntaxis.py::TestVersionDetection -v
```

Expected: Test for V2 fails (not implemented), invalid format test fails

**Step 3: Read current Syntaxis implementation**

Already read - in `syntaxis/lib/syntaxis.py`

**Step 4: Add version detection to Syntaxis.generate_sentence**

Modify `syntaxis/lib/syntaxis.py`:

```python
# Add imports at top
from syntaxis.lib.templates.v1_parser import V1Parser
from syntaxis.lib.templates.v2_parser import V2Parser
from syntaxis.lib.templates.ast import TemplateAST

# Modify generate_sentence method
def generate_sentence(self, template: str) -> list[Lexical]:
    """Generate a sentence from a template

    Args:
        template: Template string (V1 or V2 format)

    Returns:
        List of Lexical objects with inflected forms

    Raises:
        ValueError: If template format is invalid
    """
    template = template.strip()

    # Version detection
    if not template:
        raise ValueError("Invalid template format: empty template")

    if template[0] == '[':
        # V1 format
        ast = V1Parser.parse(template)
    elif template[0] == '(':
        # V2 format
        ast = V2Parser.parse(template)
    else:
        raise ValueError(
            f"Invalid template format: must start with '[' (V1) or '(' (V2), "
            f"got '{template[0]}'"
        )

    # Generate sentence from AST
    return self._generate_from_ast(ast)
```

**Step 5: Run test - will fail because _generate_from_ast doesn't exist yet**

```bash
pytest tests/lib/test_syntaxis.py::TestVersionDetection::test_invalid_template_start -v
```

Expected: PASS for invalid format, FAIL for others (missing _generate_from_ast)

**Step 6: Commit what we have**

```bash
git add syntaxis/lib/syntaxis.py tests/lib/test_syntaxis.py
git commit -m "feat: add version detection to Syntaxis class"
```

---

## Task 14: Create AST-to-Lexical Generator

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`

**Step 1: Read existing generation logic**

The current `generate_sentence` uses `Template.parse()` which returns `ParsedTemplate` with tokens. Each token has `lexical` and `features`. The code then calls `self.database.get_random_word(token.lexical, **features)`.

**Step 2: Write _generate_from_ast method**

Add to `syntaxis/lib/syntaxis.py`:

```python
    def _generate_from_ast(self, ast: TemplateAST) -> list[Lexical]:
        """Generate lexicals from AST by resolving features and querying database

        Args:
            ast: Parsed template AST

        Returns:
            List of Lexical objects with inflected forms
        """
        lexicals = []

        for group in ast.groups:
            # Resolve group features (handle references)
            resolved_group_features = self._resolve_group_features(group, ast.groups)

            # Generate lexical for each token in group
            for token in group.tokens:
                # Merge features: group features + direct features
                final_features = self._merge_features(
                    resolved_group_features,
                    token.direct_features
                )

                # Convert features to kwargs for database query
                feature_dict = {f.category: f.name for f in final_features}

                # Get word from database
                lexical = self.database.get_random_word(token.lexical, **feature_dict)
                lexicals.append(lexical)

        return lexicals

    def _resolve_group_features(self, group: Group, all_groups: list[Group]) -> list[Feature]:
        """Resolve group features, following references if present

        Args:
            group: The group to resolve features for
            all_groups: All groups in the template (for reference lookup)

        Returns:
            List of resolved features
        """
        if group.references is None:
            # No reference, just return group features
            return group.group_features.copy()

        # Find referenced group
        referenced_group = all_groups[group.references - 1]  # Convert to 0-indexed

        # Start with referenced group's features (recursively resolve)
        features = self._resolve_group_features(referenced_group, all_groups)

        # Merge in current group features (override by category)
        return self._merge_features(features, group.group_features)

    def _merge_features(self, base_features: list[Feature], override_features: list[Feature]) -> list[Feature]:
        """Merge two feature lists, with overrides replacing by category

        Args:
            base_features: Base feature list
            override_features: Features to override/add

        Returns:
            Merged feature list
        """
        # Build dict of category -> feature from base
        merged = {f.category: f for f in base_features}

        # Override with new features
        for feature in override_features:
            merged[feature.category] = feature

        return list(merged.values())
```

**Step 3: Run tests to see if they pass**

```bash
pytest tests/lib/test_syntaxis.py::TestVersionDetection -v
```

Expected: All 3 tests should PASS now

**Step 4: Run all existing Syntaxis tests**

```bash
pytest tests/lib/test_syntaxis.py -v
```

Expected: Existing tests might fail if they expect old behavior. Fix if needed.

**Step 5: Commit**

```bash
git add syntaxis/lib/syntaxis.py
git commit -m "feat: add AST-to-lexical generator with feature resolution"
```

---

## Task 15: Add Feature Override Warnings

**Files:**
- Modify: `syntaxis/lib/syntaxis.py`
- Test: `tests/lib/test_syntaxis.py`

**Step 1: Write failing test for override warnings**

```python
# Add to tests/lib/test_syntaxis.py

class TestFeatureOverrideWarnings:
    def test_override_warning_emitted(self, syntaxis_instance, caplog):
        """Should warn when direct feature overrides group/reference feature"""
        import logging
        caplog.set_level(logging.WARNING)

        # Group 1 has 'pri' (person), group 2 references it but overrides with 'sec'
        template = "(pronoun)@{nom:pri:sg} (verb{sec})@$1"
        syntaxis_instance.generate_sentence(template)

        # Check warning was logged
        assert any("overrides feature 'person'" in record.message
                   for record in caplog.records)

    def test_no_warning_when_no_conflict(self, syntaxis_instance, caplog):
        """Should not warn when direct feature doesn't conflict"""
        import logging
        caplog.set_level(logging.WARNING)

        # Group features have nom:sg, direct feature adds masc (no conflict)
        template = "(article noun{masc})@{nom:sg}"
        syntaxis_instance.generate_sentence(template)

        # No warnings
        assert not any("overrides" in record.message
                       for record in caplog.records)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/lib/test_syntaxis.py::TestFeatureOverrideWarnings -v
```

Expected: Tests FAIL (warnings not implemented)

**Step 3: Add warning logic to _merge_features**

Modify `_merge_features` in `syntaxis/lib/syntaxis.py`:

```python
import logging

# Add at module level
logger = logging.getLogger(__name__)

    def _merge_features(
        self,
        base_features: list[Feature],
        override_features: list[Feature],
        warn_on_override: bool = False,
        context: str = ""
    ) -> list[Feature]:
        """Merge two feature lists, with overrides replacing by category

        Args:
            base_features: Base feature list
            override_features: Features to override/add
            warn_on_override: If True, emit warning when override occurs
            context: Context string for warning message

        Returns:
            Merged feature list
        """
        # Build dict of category -> feature from base
        merged = {f.category: f for f in base_features}

        # Override with new features
        for feature in override_features:
            if warn_on_override and feature.category in merged:
                old_feature = merged[feature.category]
                logger.warning(
                    f"{context}overrides feature '{feature.category}': "
                    f"{old_feature.name} -> {feature.name}"
                )
            merged[feature.category] = feature

        return list(merged.values())
```

**Step 4: Update _generate_from_ast to enable warnings for direct features**

```python
    def _generate_from_ast(self, ast: TemplateAST) -> list[Lexical]:
        """Generate lexicals from AST by resolving features and querying database"""
        lexicals = []

        for group in ast.groups:
            # Resolve group features (handle references)
            resolved_group_features = self._resolve_group_features(group, ast.groups)

            # Generate lexical for each token in group
            for token in group.tokens:
                # Merge features: group features + direct features (with warnings)
                final_features = self._merge_features(
                    resolved_group_features,
                    token.direct_features,
                    warn_on_override=True,
                    context=f"Token '{token.lexical}' "
                )

                # Convert features to kwargs for database query
                feature_dict = {f.category: f.name for f in final_features}

                # Get word from database
                lexical = self.database.get_random_word(token.lexical, **feature_dict)
                lexicals.append(lexical)

        return lexicals
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/lib/test_syntaxis.py::TestFeatureOverrideWarnings -v
```

Expected: All 2 tests PASS

**Step 6: Commit**

```bash
git add syntaxis/lib/syntaxis.py tests/lib/test_syntaxis.py
git commit -m "feat: add feature override warnings"
```

---

## Task 16: Add V2 Integration Tests

**Files:**
- Create: `tests/integration/test_v2_templates.py`

**Step 1: Write comprehensive V2 integration tests**

```python
# tests/integration/test_v2_templates.py
import pytest
from syntaxis.lib.syntaxis import Syntaxis


@pytest.fixture
def syntaxis_instance():
    """Create Syntaxis instance with test database"""
    import tempfile
    import os

    # Create temporary database
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    syntaxis = Syntaxis(db_path=path)
    syntaxis.database.create_schema()

    yield syntaxis

    # Cleanup
    os.unlink(path)


class TestV2BasicGrouping:
    def test_single_group_generates_words(self, syntaxis_instance):
        """V2: (article adj noun)@{nom:masc:sg} should generate 3 words"""
        template = "(article adj noun)@{nom:masc:sg}"
        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 3
        assert result[0].lexical_type == "article"
        assert result[1].lexical_type == "adj"
        assert result[2].lexical_type == "noun"

    def test_multiple_groups_generates_words(self, syntaxis_instance):
        """V2: Multiple groups should each generate their words"""
        template = "(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"
        result = syntaxis_instance.generate_sentence(template)

        assert len(result) == 3
        assert result[2].lexical_type == "verb"


class TestV2References:
    def test_reference_inherits_features(self, syntaxis_instance):
        """V2: Group with @$1 should inherit features from group 1"""
        template = "(article)@{nom:masc:sg} (noun)@$1"
        result = syntaxis_instance.generate_sentence(template)

        # Both should have same features
        assert result[0].case == result[1].case
        assert result[0].gender == result[1].gender
        assert result[0].number == result[1].number


class TestV2DirectFeatures:
    def test_direct_feature_override(self, syntaxis_instance):
        """V2: Direct features should override group features"""
        template = "(article noun{fem})@{nom:masc:sg}"
        result = syntaxis_instance.generate_sentence(template)

        # Article has masc (from group)
        assert result[0].gender == "masc"

        # Noun has fem (direct override)
        assert result[1].gender == "fem"


class TestV1V2Equivalence:
    def test_v1_v2_same_output_structure(self, syntaxis_instance):
        """V1 and V2 should produce equivalent structures"""
        v1 = "[noun:nom:masc:sg] [verb:pres:act:ter:sg]"
        v2 = "(noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}"

        result_v1 = syntaxis_instance.generate_sentence(v1)
        result_v2 = syntaxis_instance.generate_sentence(v2)

        assert len(result_v1) == len(result_v2)
        assert result_v1[0].lexical_type == result_v2[0].lexical_type
        assert result_v1[1].lexical_type == result_v2[1].lexical_type
```

**Step 2: Run test to verify current state**

```bash
pytest tests/integration/test_v2_templates.py -v
```

Expected: Tests may fail due to database not being seeded or other issues. Fix as needed.

**Step 3: Commit**

```bash
git add tests/integration/test_v2_templates.py
git commit -m "test: add V2 integration tests"
```

---

## Task 17: Fix V1 Parser Feature Mapping

**Files:**
- Modify: `syntaxis/lib/templates/v1_parser.py`
- Test: `tests/lib/templates/test_v1_parser.py`

**Step 1: Check if V1 parser handles all feature types correctly**

The V1 parser currently expects all features from the existing parser. We need to ensure it handles the abbreviated features correctly (pres vs present, act vs active, etc.).

**Step 2: Add test for abbreviated features**

```python
# Add to tests/lib/templates/test_v1_parser.py

class TestV1ParserFeatures:
    def test_parse_verb_abbreviated_features(self):
        """Should parse abbreviated features (pres, act)"""
        template_str = "[verb:pres:act:ter:sg]"
        result = V1Parser.parse(template_str)

        group = result.groups[0]
        feature_names = [f.name for f in group.group_features]
        assert "pres" in feature_names
        assert "act" in feature_names
        assert "ter" in feature_names
        assert "sg" in feature_names
```

**Step 3: Run test**

```bash
pytest tests/lib/templates/test_v1_parser.py::TestV1ParserFeatures -v
```

Expected: Should PASS if existing parser already uses abbreviated forms

**Step 4: If test fails, update FeatureMapper**

Check if FeatureMapper needs to handle full forms (present, active, passive) in addition to abbreviated forms. Add mappings if needed.

**Step 5: Commit any fixes**

```bash
git add syntaxis/lib/templates/v1_parser.py syntaxis/lib/templates/feature_mapper.py tests/lib/templates/test_v1_parser.py
git commit -m "fix: ensure V1Parser handles all feature types"
```

---

## Task 18: Update Service Layer for V2

**Files:**
- Modify: `syntaxis/service/core/service.py`
- Test: `tests/service/core/test_service.py`

**Step 1: Verify service layer uses Syntaxis.generate_sentence**

The service layer should already work since we modified `Syntaxis.generate_sentence` to handle both V1 and V2. Let's verify.

**Step 2: Add test for V2 template via service**

```python
# Add to tests/service/core/test_service.py

class TestServiceV2Templates:
    def test_generate_from_v2_template(self, service_instance):
        """Service should handle V2 templates"""
        template = "(noun)@{nom:masc:sg}"
        result = service_instance.generate_from_template(template)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_generate_from_v2_template_with_reference(self, service_instance):
        """Service should handle V2 templates with references"""
        template = "(article)@{nom:sg} (noun)@$1"
        result = service_instance.generate_from_template(template)

        assert len(result) == 2
```

**Step 3: Run test**

```bash
pytest tests/service/core/test_service.py::TestServiceV2Templates -v
```

Expected: Should PASS if service properly delegates to Syntaxis

**Step 4: Commit test**

```bash
git add tests/service/core/test_service.py
git commit -m "test: add service layer tests for V2 templates"
```

---

## Task 19: Update API Routes for V2

**Files:**
- Test: `tests/service/api/test_routes.py`

**Step 1: Add API test for V2 templates**

```python
# Add to tests/service/api/test_routes.py

class TestV2TemplateRoutes:
    def test_generate_endpoint_v2_template(self, client):
        """POST /generate should accept V2 templates"""
        response = client.post(
            "/generate",
            json={"template": "(noun)@{nom:masc:sg}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "lexicals" in data or isinstance(data, list)

    def test_generate_endpoint_v2_with_reference(self, client):
        """POST /generate should handle V2 references"""
        response = client.post(
            "/generate",
            json={"template": "(article)@{nom:sg} (noun)@$1"}
        )

        assert response.status_code == 200
```

**Step 2: Run test**

```bash
pytest tests/service/api/test_routes.py::TestV2TemplateRoutes -v
```

Expected: Should PASS if routes properly use service layer

**Step 3: Commit test**

```bash
git add tests/service/api/test_routes.py
git commit -m "test: add API route tests for V2 templates"
```

---

## Task 20: Add Comprehensive Error Message Tests

**Files:**
- Modify: `tests/lib/templates/test_v2_parser.py`

**Step 1: Add test for all error cases from design doc**

```python
# Add to tests/lib/templates/test_v2_parser.py

class TestV2ParserErrors:
    def test_error_missing_closing_parenthesis(self):
        """Should provide clear error for missing )"""
        with pytest.raises(ValueError, match="Unclosed group"):
            V2Parser.parse("(article noun@{nom:sg}")

    def test_error_missing_closing_brace(self):
        """Should provide clear error for missing }"""
        with pytest.raises(ValueError, match="Unclosed brace"):
            V2Parser.parse("(article)@{nom:sg")

    def test_error_unknown_feature(self):
        """Should provide clear error for unknown feature"""
        with pytest.raises(ValueError, match="Unknown feature"):
            V2Parser.parse("(noun)@{invalidfeature}")

    def test_error_invalid_reference_high(self):
        """Should error when reference number too high"""
        with pytest.raises(ValueError, match="Reference \\$3 does not exist"):
            V2Parser.parse("(article)@{nom:sg} (noun)@$3")

    def test_error_forward_reference_group_2(self):
        """Should error on forward reference from group 1"""
        with pytest.raises(ValueError, match="points forward"):
            V2Parser.parse("(noun)@$2 (article)@{nom:sg}")
```

**Step 2: Run test**

```bash
pytest tests/lib/templates/test_v2_parser.py::TestV2ParserErrors -v
```

Expected: All should PASS

**Step 3: Commit**

```bash
git add tests/lib/templates/test_v2_parser.py
git commit -m "test: add comprehensive error message tests"
```

---

## Task 21: Run Full Test Suite

**Files:**
- N/A (verification step)

**Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests PASS

**Step 2: If failures, fix them**

Review any failing tests and fix issues.

**Step 3: Run tests with coverage**

```bash
pytest tests/ --cov=syntaxis --cov-report=term-missing
```

Review coverage and add tests for uncovered code if needed.

**Step 4: Commit any fixes**

```bash
git add .
git commit -m "fix: address test failures and improve coverage"
```

---

## Task 22: Update Documentation

**Files:**
- Create: `docs/v2-syntax-guide.md`

**Step 1: Write V2 syntax guide**

```markdown
# Template V2 Syntax Guide

## Overview

Template V2 introduces a more concise syntax for defining Greek sentence templates by allowing you to group lexicals with shared grammatical features.

## Basic Syntax

### V1 (Original)
\`\`\`
[article:nom:masc:sg] [adj:nom:masc:sg] [noun:nom:masc:sg]
\`\`\`

### V2 (New)
\`\`\`
(article adj noun)@{nom:masc:sg}
\`\`\`

## Features

### 1. Grouping

Group multiple lexicals that share the same features:

\`\`\`
(article adj noun)@{nom:masc:sg}
\`\`\`

This applies `nom:masc:sg` to all three lexicals.

### 2. Multiple Groups

Separate groups with whitespace:

\`\`\`
(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}
\`\`\`

### 3. Group References

Reference features from a previous group using `@$N`:

\`\`\`
(article noun)@{nom:masc:sg} (pronoun)@$1
\`\`\`

The second group inherits `nom:masc:sg` from group 1 (`$1`).

**Rules:**
- Can only reference earlier groups (no forward references)
- Groups are numbered 1, 2, 3, etc. automatically

### 4. Direct Feature Overrides

Apply features to individual lexicals using `{...}`:

\`\`\`
(article noun{fem})@{nom:masc:sg}
\`\`\`

Here, `noun` gets `fem` directly, overriding the group's `masc`.

**Warning:** When a direct feature conflicts with an inherited feature, a warning is logged.

## Feature Resolution

Features are resolved in this order:
1. Referenced group features (`@$N`)
2. Current group features (`@{...}`)
3. Direct lexical features (`lexical{...}`)

Later features override earlier ones by category (case, gender, number, etc.).

## Examples

### Basic Grouping
\`\`\`
V1: [article:nom:masc:sg] [noun:nom:masc:sg]
V2: (article noun)@{nom:masc:sg}
\`\`\`

### With References
\`\`\`
V2: (article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg} (pronoun)@$1
\`\`\`

The pronoun inherits `nom:masc:sg` from group 1.

### With Direct Overrides
\`\`\`
V2: (article noun{fem})@{nom:masc:sg}
\`\`\`

Article gets `nom:masc:sg`, noun gets `nom:fem:sg`.

## Backward Compatibility

All V1 templates continue to work. The parser automatically detects which version based on the first character:
- `[` = V1 syntax
- `(` = V2 syntax

## Error Messages

Common errors:
- `Unclosed group` - Missing closing parenthesis
- `Unclosed brace` - Missing closing brace
- `Reference $N does not exist` - Referenced group number doesn't exist
- `Reference $N points forward` - Can't reference future groups
- `Unknown feature` - Feature name not recognized
```

**Step 2: Save documentation**

Already written above in file content.

**Step 3: Commit**

```bash
git add docs/v2-syntax-guide.md
git commit -m "docs: add V2 syntax guide"
```

---

## Task 23: Update README

**Files:**
- Modify: `README.md`

**Step 1: Add V2 section to README**

Read current README, then add section about V2 templates:

```markdown
## Template Syntax

Syntaxis supports two template syntax versions:

### V1 Syntax (Original)

\`\`\`
[article:nom:masc:sg] [noun:nom:masc:sg] [verb:pres:act:ter:sg]
\`\`\`

### V2 Syntax (Recommended)

More concise with feature grouping:

\`\`\`
(article noun)@{nom:masc:sg} (verb)@{pres:act:ter:sg}
\`\`\`

See [V2 Syntax Guide](docs/v2-syntax-guide.md) for complete documentation.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with V2 syntax info"
```

---

## Task 24: Final Verification & Cleanup

**Files:**
- N/A (verification)

**Step 1: Run all tests one final time**

```bash
pytest tests/ -v --cov=syntaxis
```

Expected: All tests PASS with good coverage

**Step 2: Test manually via CLI**

```bash
python main.py  # Try both V1 and V2 templates interactively
```

**Step 3: Test via API**

```bash
# Start server
uvicorn syntaxis.service.app:app --reload

# In another terminal, test with curl
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"template": "(article noun)@{nom:masc:sg}"}'
```

**Step 4: Review all changes**

```bash
git log --oneline
git diff main
```

**Step 5: Create summary commit if needed**

```bash
git add .
git commit -m "chore: final cleanup and verification for V2 templates"
```

---

## Summary

This plan implements the Template V2 design with:

✅ AST data classes (Feature, POSToken, Group, TemplateAST)
✅ V2Parser with validation and error handling
✅ V1Parser wrapping existing logic
✅ Version detection in Syntaxis class
✅ Feature resolution with reference support
✅ Feature override warnings
✅ Full test coverage
✅ Integration tests
✅ Documentation

**Total Tasks:** 24
**Estimated Time:** 6-8 hours (following TDD, frequent commits)

**Key Implementation Principles:**
- TDD throughout (write test, see it fail, implement, see it pass)
- Small commits after each passing test
- DRY - reuse existing V1 parser logic
- YAGNI - only implement what's in the design doc
- Backward compatibility - V1 templates work unchanged
