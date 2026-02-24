"""
StarNavigation Backend - FastAPI Application

Main entry point for the FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .api.routes import navigation, celestial

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="StarNavigation API",
        description="Celestial compass navigation algorithm API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Configure CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all for easier local testing, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred.",
                "type": type(exc).__name__
            }
        )
    
    # Include routers
    app.include_router(navigation.router, prefix="/api/v1")
    app.include_router(celestial.router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint with API info."""
        return {
            "name": "StarNavigation API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "endpoints": {
                "navigation": "/api/v1/navigation",
                "celestial": "/api/v1/celestial"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
