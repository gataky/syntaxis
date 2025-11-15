"""Template storage API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from syntaxis.lib.database import templates
from syntaxis.service.dependencies import get_service_dependency
from syntaxis.service.schemas.requests import SaveTemplateRequest
from syntaxis.service.schemas.responses import DeleteTemplateResponse, TemplateResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.post("", response_model=TemplateResponse, status_code=201)
async def save_template(
    request: SaveTemplateRequest, service=Depends(get_service_dependency)
):
    """Save a new template.

    Args:
        request: Request with template string
        service: Injected service (provides database connection)

    Returns:
        Saved template with ID and created_at

    Raises:
        HTTPException: 409 if template already exists
    """
    logger.info(f"POST /templates - template: {request.template}")

    try:
        result = templates.save_template(
            service.syntaxis.database._conn, request.template
        )
        logger.info(f"POST /templates - 201 Created - id: {result['id']}")
        return result
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise


@router.get("", response_model=list[TemplateResponse])
async def list_templates(service=Depends(get_service_dependency)):
    """List all saved templates.

    Args:
        service: Injected service (provides database connection)

    Returns:
        List of all templates ordered by created_at descending
    """
    logger.info("GET /templates")
    result = templates.list_templates(service.syntaxis.database._conn)
    logger.info(f"GET /templates - 200 OK - returned {len(result)} templates")
    return result


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, service=Depends(get_service_dependency)):
    """Get a specific template by ID.

    Args:
        template_id: Template ID
        service: Injected service (provides database connection)

    Returns:
        Template with matching ID

    Raises:
        HTTPException: 404 if template not found
    """
    logger.info(f"GET /templates/{template_id}")
    result = templates.get_template(service.syntaxis.database._conn, template_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Template not found")

    logger.info(f"GET /templates/{template_id} - 200 OK")
    return result


@router.delete("/{template_id}", response_model=DeleteTemplateResponse)
async def delete_template(template_id: int, service=Depends(get_service_dependency)):
    """Delete a template by ID.

    Args:
        template_id: Template ID
        service: Injected service (provides database connection)

    Returns:
        Success message

    Raises:
        HTTPException: 404 if template not found
    """
    logger.info(f"DELETE /templates/{template_id}")
    deleted = templates.delete_template(service.syntaxis.database._conn, template_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")

    logger.info(f"DELETE /templates/{template_id} - 200 OK")
    return {"message": "Template deleted successfully"}
