"""API route handlers."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from syntaxis.lib import constants as c
from syntaxis.lib.logging import log_calls
from syntaxis.lib.templates.api import TemplateParseError

logger = logging.getLogger(__name__)
from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.dependencies import get_service_dependency
from syntaxis.service.schemas.requests import GenerateRequest
from syntaxis.service.schemas.responses import GenerateResponse, LexicalResponse

router = APIRouter(prefix="/api/v1", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
@log_calls
async def generate(
    request: GenerateRequest,
    service: SyntaxisService = Depends(get_service_dependency),
) -> GenerateResponse:
    """Generate Greek lexicals from a grammatical template.

    Args:
        request: Request containing the template string
        service: Injected SyntaxisService instance

    Returns:
        Response containing the template and generated lexicals

    Raises:
        HTTPException: 400 if template is invalid, 500 if generation fails
    """
    logger.info(f"POST /generate - template: {request.template}")

    try:
        lexicals_json = service.generate_from_template(request.template)

        # Convert to Pydantic models
        lexicals = [LexicalResponse(**lex) for lex in lexicals_json]

        result = GenerateResponse(template=request.template, lexicals=lexicals)
        logger.info(f"POST /generate - 200 OK - returned {len(result.lexicals)} words")
        return result

    except TemplateParseError as e:
        # Template parse errors return 400
        raise HTTPException(status_code=400, detail=f"Invalid template: {str(e)}")

    except ValueError as e:
        error_msg = str(e)

        # Template parse errors and feature validation errors return 400
        if ("template" in error_msg.lower() or
            "invalid" in error_msg.lower() or
            "no " in error_msg.lower() and "found" in error_msg.lower()):
            raise HTTPException(
                status_code=400, detail=f"Invalid template: {error_msg}"
            )

        # Other ValueErrors are unexpected - let Exception handler catch it
        raise


@router.get("/lexicals/schema")
@log_calls
async def get_lexical_schema():
    """Get all lexical types with their required features.

    Returns a mapping of lexical types to their required grammatical features.
    This endpoint provides metadata needed by the template builder UI.

    Returns:
        dict: Mapping of lexical types to their schema including required features
    """
    schema = {
        "lexicals": {
            c.NOUN: {"required": [c.CASE, c.GENDER, c.NUMBER]},
            c.VERB: {"required": [c.TENSE, c.VOICE, c.PERSON, c.NUMBER]},
            c.ADJECTIVE: {"required": [c.CASE, c.GENDER, c.NUMBER]},
            c.ARTICLE: {"required": [c.CASE, c.GENDER, c.NUMBER]},
            c.PRONOUN: {"required": [c.TYPE], "optional": [c.CASE, c.PERSON, c.NUMBER, c.GENDER]},
            c.ADVERB: {"required": []},
            c.PREPOSITION: {"required": []},
            c.CONJUNCTION: {"required": []},
            c.NUMERAL: {"required": []},
        }
    }
    return schema


@router.get("/features")
@log_calls
async def get_features():
    """Get all grammatical feature categories and their possible values.

    Returns a mapping of feature categories to lists of valid values.
    This endpoint provides metadata needed by the template builder UI.

    Returns:
        dict: Mapping of feature categories to their valid values
    """
    features = {
        c.CASE: sorted(c.CASE_VALUES),
        c.GENDER: sorted(c.GENDER_VALUES),
        c.NUMBER: sorted(c.NUMBER_VALUES),
        c.TENSE: sorted(c.TENSE_VALUES),
        c.VOICE: sorted(c.VOICE_VALUES),
        c.PERSON: sorted(c.PERSON_VALUES),
        c.TYPE: sorted(c.PRONOUN_TYPES),
    }
    return features
