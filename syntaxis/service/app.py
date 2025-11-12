"""FastAPI application setup and configuration."""

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from syntaxis.service.api.routes import router

# Configure logging to stdout with uvicorn-style format
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("syntaxis.service")

log.info("wtf")

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
    allow_origins=["http://localhost:5173"], # Allow client origin
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
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
    log.error(str(exc))
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
