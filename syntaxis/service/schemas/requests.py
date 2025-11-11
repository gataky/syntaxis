"""Request schemas for API endpoints."""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request body for generating lexicals from a template.

    Attributes:
        template: Greek grammar template string (e.g., "[noun:nom:masc:sg]")
    """

    template: str = Field(
        ...,
        min_length=1,
        description="Greek grammar template with tokens like [noun:nom:masc:sg]",
        examples=["[article:nom:masc:sg] [noun:nom:masc:sg]"],
    )
