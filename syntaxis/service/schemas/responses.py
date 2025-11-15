"""Response schemas for API endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class LexicalResponse(BaseModel):
    """Response model for a single lexical item.

    Attributes:
        lemma: Dictionary form of the word
        word: Set of inflected forms (None if not yet inflected)
        translations: Set of English translations
        features: Dictionary of grammatical features
    """

    pos: str = Field(
        ...,
        description="The part of speach this word belongs to (noun, verb, adjective, etc.)",
        examples=["noun"],
    )

    lemma: str = Field(
        ...,
        description="Dictionary form of the Greek word",
        examples=["άνδρας"],
    )
    word: Optional[set[str]] = Field(
        None,
        description="Inflected word form(s)",
        examples=[{"άνδρας"}],
    )
    translations: Optional[set[str]] = Field(
        None,
        description="English translations",
        examples=[{"man", "male"}],
    )
    features: dict[str, str] = Field(
        ...,
        description="Grammatical features (case, gender, number, etc.)",
        examples=[{"case": "nom", "gender": "masc", "number": "sg"}],
    )


class GenerateResponse(BaseModel):
    """Response model for generate endpoint.

    Attributes:
        template: The original template string that was processed
        lexicals: List of generated lexical items with their features
    """

    template: str = Field(
        ...,
        description="Original template string",
        examples=["[article:nom:masc:sg] [noun:nom:masc:sg]"],
    )
    lexicals: list[LexicalResponse] = Field(
        ...,
        description="Generated lexicals matching the template",
    )


class TemplateResponse(BaseModel):
    """Response model for a template.

    Attributes:
        id: Template ID
        template: Template string
        created_at: Timestamp when created
    """

    id: int = Field(..., description="Template ID", examples=[1])
    template: str = Field(
        ...,
        description="Template string",
        examples=["noun(case=nominative,gender=masculine,number=singular)"],
    )
    created_at: str = Field(
        ..., description="ISO 8601 timestamp", examples=["2025-11-15 10:30:00"]
    )


class DeleteTemplateResponse(BaseModel):
    """Response model for template deletion.

    Attributes:
        message: Success message
    """

    message: str = Field(
        ..., description="Success message", examples=["Template deleted successfully"]
    )
