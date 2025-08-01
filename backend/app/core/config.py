"""
Configuration settings for the Smart Waste Sorter API
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Waste Sorter API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_waste_sorter.db")
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ]
    
    # AI Model Settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/waste_classifier.h5")
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    
    # File Upload Settings
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Email Settings (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Redis (for caching and background tasks)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # External APIs
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    MAPS_API_KEY: str = os.getenv("MAPS_API_KEY", "")
    
    # Waste Categories
    WASTE_CATEGORIES: List[str] = [
        "plastic",
        "paper",
        "glass",
        "metal",
        "organic",
        "electronic",
        "hazardous",
        "textile",
        "other"
    ]
    
    # Eco Points System
    POINTS_PER_SCAN: int = 10
    POINTS_PER_CORRECT_SORT: int = 25
    POINTS_PER_DIY_PROJECT: int = 50
    POINTS_PER_SHOP_PURCHASE: int = 5
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

# Create settings instance
settings = Settings()
