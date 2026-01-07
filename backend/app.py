"""
Food Agent App - Main FastAPI Application

Entry point for the food-agent application backend server.
"""

import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Food Agent App API",
    description="AI-powered recipe management and meal planning service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi. json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check & Status Endpoints

@app.get("/", tags=["Status"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Food Agent App API",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime. utcnow().isoformat()
    }


@app.get("/health", tags=["Status"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime. utcnow().isoformat()
    }


@app.get("/api/v1/status", tags=["Status"])
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# Placeholder Routes

@app.get("/api/v1/recipes", tags=["Recipes"])
async def list_recipes():
    """List all recipes - coming in v0.2"""
    return {"message": "Recipe listing endpoint - coming in v0.2", "status": "not_implemented"}


@app.post("/api/v1/recipes", tags=["Recipes"])
async def create_recipe():
    """Create a new recipe - coming in v0.2"""
    return {"message": "Recipe creation endpoint - coming in v0.2", "status": "not_implemented"}


@app.get("/api/v1/suggestions/daily", tags=["Suggestions"])
async def get_daily_suggestions():
    """Get daily meal suggestions - coming in v0.2"""
    return {"message": "Daily suggestions endpoint - coming in v0.2", "status": "not_implemented"}


@app.get("/api/v1/meal-plans", tags=["Meal Planning"])
async def list_meal_plans():
    """List meal plans - coming in v0.2"""
    return {"message": "Meal plans endpoint - coming in v0.2", "status": "not_implemented"}


@app.get("/api/v1/shopping-lists", tags=["Shopping"])
async def list_shopping_lists():
    """List shopping lists - coming in v0.2"""
    return {"message": "Shopping lists endpoint - coming in v0.2", "status": "not_implemented"}


# Error Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Startup & Shutdown Events

@app.on_event("startup")
async def startup_event():
    """Handle application startup."""
    logger.info("Starting Food Agent App v0.1.0")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown."""
    logger.info("Shutting down Food Agent App")


# Entry Point

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
