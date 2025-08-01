"""
Smart Waste Sorter Backend API
FastAPI application with AI-powered waste detection and management
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
from pathlib import Path

# Import routers
from app.routers import (
    auth,
    waste_detection,
    user_profile,
    smart_card,
    shop,
    analytics,
    diy_projects
)

# Import database
from app.database import engine, Base
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Waste Sorter API",
    description="AI-powered waste management and sorting system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs("uploads/waste_images", exist_ok=True)
os.makedirs("uploads/user_avatars", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(waste_detection.router, prefix="/api/detection", tags=["Waste Detection"])
app.include_router(user_profile.router, prefix="/api/profile", tags=["User Profile"])
app.include_router(smart_card.router, prefix="/api/smart-card", tags=["Smart Card"])
app.include_router(shop.router, prefix="/api/shop", tags=["Shop"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(diy_projects.router, prefix="/api/diy", tags=["DIY Projects"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Smart Waste Sorter API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/api/docs",
        "features": [
            "AI Waste Detection",
            "User Authentication",
            "Smart Card Management",
            "Eco Shop",
            "Analytics Dashboard",
            "DIY Projects"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_model": "loaded",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
