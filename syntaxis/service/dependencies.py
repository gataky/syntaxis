"""Dependency injection for FastAPI service."""

from syntaxis.api import Syntaxis
from syntaxis.service.core.service import SyntaxisService


def get_syntaxis() -> Syntaxis:
    """Get Syntaxis instance with default configuration.

    Returns:
        Syntaxis instance connected to ./syntaxis.db
    """
    return Syntaxis(db_path="./syntaxis.db")


def get_service(syntaxis: Syntaxis) -> SyntaxisService:
    """Get SyntaxisService instance.

    This is a factory function used by FastAPI's dependency injection.
    In routes, use: service: SyntaxisService = Depends(get_service)

    Args:
        syntaxis: Syntaxis instance (injected by FastAPI)

    Returns:
        SyntaxisService instance
    """
    return SyntaxisService(syntaxis=syntaxis)
