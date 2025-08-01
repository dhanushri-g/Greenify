"""
Waste detection and management models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class WasteScan(Base):
    __tablename__ = "waste_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image information
    image_url = Column(String(500), nullable=False)
    image_filename = Column(String(255), nullable=False)
    image_size = Column(Integer, nullable=True)  # in bytes
    
    # Detection results
    detected_category = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    alternative_categories = Column(JSON, nullable=True)  # List of other possible categories
    
    # Classification details
    is_recyclable = Column(Boolean, nullable=True)
    disposal_method = Column(String(255), nullable=True)
    environmental_impact = Column(Text, nullable=True)
    recycling_tips = Column(Text, nullable=True)
    
    # User feedback
    user_confirmed = Column(Boolean, nullable=True)
    user_correction = Column(String(100), nullable=True)
    feedback_notes = Column(Text, nullable=True)
    
    # Location data
    scan_location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Timestamps
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="waste_scans")
    
    def __repr__(self):
        return f"<WasteScan(id={self.id}, category='{self.detected_category}', confidence={self.confidence_score})>"

class WasteCategory(Base):
    __tablename__ = "waste_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Classification properties
    is_recyclable = Column(Boolean, default=False)
    is_compostable = Column(Boolean, default=False)
    is_hazardous = Column(Boolean, default=False)
    
    # Disposal information
    disposal_method = Column(String(255), nullable=True)
    recycling_process = Column(Text, nullable=True)
    environmental_impact = Column(Text, nullable=True)
    
    # Tips and guidelines
    sorting_tips = Column(Text, nullable=True)
    preparation_steps = Column(Text, nullable=True)
    common_mistakes = Column(Text, nullable=True)
    
    # Visual properties
    color_code = Column(String(7), nullable=True)  # Hex color
    icon_name = Column(String(100), nullable=True)
    
    # Statistics
    scan_count = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WasteCategory(id={self.id}, name='{self.name}')>"

class RecyclingTip(Base):
    __tablename__ = "recycling_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Tip properties
    difficulty_level = Column(String(50), default="Easy")  # Easy, Medium, Hard
    estimated_time = Column(String(50), nullable=True)  # e.g., "5 minutes"
    materials_needed = Column(JSON, nullable=True)  # List of materials
    
    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Content metadata
    author = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    
    # Status
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<RecyclingTip(id={self.id}, title='{self.title}')>"
