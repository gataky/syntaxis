"""FastAPI application setup and configuration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from syntaxis.service.api.routes import router

# Create FastAPI application
app = FastAPI(
    title="Syntaxis API",
    description="REST API for generating Greek sentences from grammatical templates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors.

    Args:
        request: The request that caused the exception
        exc: The exception that was raised

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Register routers
app.include_router(router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint.

    Returns:
        Status indicating the service is running
    """
    return {"status": "healthy", "service": "syntaxis-api"}
