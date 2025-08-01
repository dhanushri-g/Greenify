"""
User model for authentication and profile management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Eco metrics
    eco_points = Column(Integer, default=0)
    total_scans = Column(Integer, default=0)
    correct_sorts = Column(Integer, default=0)
    eco_level = Column(String(50), default="Eco Beginner")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    waste_scans = relationship("WasteScan", back_populates="user")
    smart_cards = relationship("SmartCard", back_populates="user")
    orders = relationship("Order", back_populates="user")
    diy_projects = relationship("DIYProject", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def eco_level_progress(self):
        """Calculate progress to next eco level"""
        levels = {
            "Eco Beginner": 0,
            "Eco Enthusiast": 500,
            "Eco Warrior": 1500,
            "Eco Champion": 3000,
            "Eco Master": 5000
        }
        
        current_points = self.eco_points
        current_level_points = levels.get(self.eco_level, 0)
        
        # Find next level
        next_level = None
        next_level_points = None
        
        for level, points in levels.items():
            if points > current_points:
                next_level = level
                next_level_points = points
                break
        
        if next_level:
            progress = ((current_points - current_level_points) / 
                       (next_level_points - current_level_points)) * 100
            return {
                "current_level": self.eco_level,
                "next_level": next_level,
                "progress_percentage": min(100, max(0, progress)),
                "points_to_next": next_level_points - current_points
            }
        
        return {
            "current_level": self.eco_level,
            "next_level": None,
            "progress_percentage": 100,
            "points_to_next": 0
        }
    
    def add_eco_points(self, points: int, reason: str = ""):
        """Add eco points and update level if necessary"""
        self.eco_points += points
        
        # Update level based on points
        if self.eco_points >= 5000:
            self.eco_level = "Eco Master"
        elif self.eco_points >= 3000:
            self.eco_level = "Eco Champion"
        elif self.eco_points >= 1500:
            self.eco_level = "Eco Warrior"
        elif self.eco_points >= 500:
            self.eco_level = "Eco Enthusiast"
        else:
            self.eco_level = "Eco Beginner"
