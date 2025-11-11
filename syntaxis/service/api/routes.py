"""API route handlers."""

from fastapi import APIRouter, Depends, HTTPException

from syntaxis.service.core.service import SyntaxisService
from syntaxis.service.dependencies import get_service_dependency
from syntaxis.service.schemas.requests import GenerateRequest
from syntaxis.service.schemas.responses import GenerateResponse, LexicalResponse
from syntaxis.lib.templates.api import TemplateParseError

router = APIRouter(prefix="/api/v1", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
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
    try:
        lexicals_json = service.generate_from_template(request.template)

        # Convert to Pydantic models
        lexicals = [LexicalResponse(**lex) for lex in lexicals_json]

        return GenerateResponse(template=request.template, lexicals=lexicals)

    except TemplateParseError as e:
        # Template parse errors return 400
        raise HTTPException(status_code=400, detail=f"Invalid template: {str(e)}")

    except ValueError as e:
        error_msg = str(e)

        # Template parse errors return 400
        if "template" in error_msg.lower() or "invalid" in error_msg.lower():
            raise HTTPException(
                status_code=400, detail=f"Invalid template: {error_msg}"
            )

        # No matching words returns 500
        raise HTTPException(status_code=500, detail=error_msg)

    except Exception as e:
        # Unexpected errors return 500
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
