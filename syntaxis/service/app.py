"""FastAPI application setup and configuration."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from syntaxis.lib.logging import setup_logging
from syntaxis.service.api.routes import router

# Initialize logging before service starts
setup_logging()

log = logging.getLogger("syntaxis.service")

# Create FastAPI application
app = FastAPI(
    title="Syntaxis API",
    description="REST API for generating Greek sentences from grammatical templates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Added CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow client origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for expected HTTP errors (validation, business logic).

    Logs at warning level since these are expected error cases.

    Args:
        request: The request that caused the exception
        exc: The HTTPException that was raised

    Returns:
        JSON response with error details
    """
    log.warning(f"{exc.status_code} {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
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
