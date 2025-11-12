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


@dataclass
class POSToken:
    """Individual lexical with optional direct features

    Attributes:
        lexical: The part of speech type (e.g., 'noun', 'verb', 'adj')
        direct_features: Features applied directly to this lexical (overrides group features)
    """

    lexical: str
    direct_features: list[Feature]


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


@dataclass
class TemplateAST:
    """Top-level AST for a template

    Attributes:
        groups: List of Group objects representing the template structure
        version: Template syntax version (1 for V1, 2 for V2)
    """

    groups: list[Group]
    version: int
