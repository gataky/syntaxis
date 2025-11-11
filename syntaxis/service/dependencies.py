"""Dependency injection for FastAPI service."""

from functools import lru_cache

from fastapi import Depends

from syntaxis.lib.syntaxis import Syntaxis
from syntaxis.service.core.service import SyntaxisService


@lru_cache()
def get_syntaxis() -> Syntaxis:
    """Get cached Syntaxis instance with default configuration.

    Uses lru_cache to ensure a single Syntaxis instance is reused across
    all requests, improving performance by reusing the database connection.

    Returns:
        Cached Syntaxis instance connected to ./syntaxis.db
    """
    return Syntaxis(db_path="./syntaxis.db")


@lru_cache()
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


def get_service_dependency(syntaxis=Depends(get_syntaxis)):
    """Dependency chain for service injection."""
    return get_service(syntaxis)
