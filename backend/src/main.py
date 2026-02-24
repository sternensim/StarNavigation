"""
StarNavigation Backend - FastAPI Application

Main entry point for the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import navigation, celestial


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
        allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and common dev ports
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
