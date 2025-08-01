"""
Smart Card management router
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel
from app.database import get_db, Base
from app.models.user import User
from app.core.security import get_current_user
import uuid
from datetime import datetime, timedelta

router = APIRouter()

# Smart Card Model
class SmartCard(Base):
    __tablename__ = "smart_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(String(20), unique=True, nullable=False)
    
    # Card details
    full_name = Column(String(255), nullable=False)
    valid_until = Column(DateTime, nullable=False)
    status = Column(String(50), default="Active")
    card_type = Column(String(50), default="Standard")
    
    # Customization
    background_color = Column(String(7), default="#10b981")
    text_color = Column(String(7), default="#ffffff")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_digital = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models
class SmartCardCreate(BaseModel):
    full_name: str
    card_type: str = "Standard"
    background_color: str = "#10b981"
    text_color: str = "#ffffff"

class SmartCardUpdate(BaseModel):
    full_name: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    status: Optional[str] = None

class SmartCardResponse(BaseModel):
    id: int
    card_number: str
    full_name: str
    valid_until: str
    status: str
    card_type: str
    background_color: str
    text_color: str
    is_active: bool
    is_digital: bool
    eco_points: int
    eco_level: str
    total_scans: int
    created_at: str
    
    class Config:
        from_attributes = True

def generate_card_number() -> str:
    """Generate unique card number"""
    prefix = "GRN"
    suffix = str(uuid.uuid4().int)[:6]
    return f"{prefix}-{suffix}"

@router.post("/create", response_model=SmartCardResponse)
async def create_smart_card(
    card_data: SmartCardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new smart card for user"""
    
    # Check if user already has an active card
    existing_card = db.query(SmartCard).filter(
        SmartCard.user_id == current_user.id,
        SmartCard.is_active == True
    ).first()
    
    if existing_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active smart card"
        )
    
    # Generate card number
    card_number = generate_card_number()
    
    # Ensure unique card number
    while db.query(SmartCard).filter(SmartCard.card_number == card_number).first():
        card_number = generate_card_number()
    
    # Create card with 2-year validity
    valid_until = datetime.utcnow() + timedelta(days=730)
    
    new_card = SmartCard(
        user_id=current_user.id,
        card_number=card_number,
        full_name=card_data.full_name,
        valid_until=valid_until,
        card_type=card_data.card_type,
        background_color=card_data.background_color,
        text_color=card_data.text_color
    )
    
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    
    # Add card data to response
    card_response = SmartCardResponse(
        id=new_card.id,
        card_number=new_card.card_number,
        full_name=new_card.full_name,
        valid_until=new_card.valid_until.isoformat(),
        status=new_card.status,
        card_type=new_card.card_type,
        background_color=new_card.background_color,
        text_color=new_card.text_color,
        is_active=new_card.is_active,
        is_digital=new_card.is_digital,
        eco_points=current_user.eco_points,
        eco_level=current_user.eco_level,
        total_scans=current_user.total_scans,
        created_at=new_card.created_at.isoformat()
    )
    
    return card_response

@router.get("/", response_model=SmartCardResponse)
async def get_smart_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active smart card"""
    
    card = db.query(SmartCard).filter(
        SmartCard.user_id == current_user.id,
        SmartCard.is_active == True
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active smart card found"
        )
    
    # Determine status based on eco points and activity
    if current_user.eco_points >= 3000:
        status = "Excellent"
    elif current_user.eco_points >= 1500:
        status = "Good"
    elif current_user.eco_points >= 500:
        status = "Moderate"
    else:
        status = "Poor"
    
    # Update status if changed
    if card.status != status:
        card.status = status
        db.commit()
    
    card_response = SmartCardResponse(
        id=card.id,
        card_number=card.card_number,
        full_name=card.full_name,
        valid_until=card.valid_until.isoformat(),
        status=card.status,
        card_type=card.card_type,
        background_color=card.background_color,
        text_color=card.text_color,
        is_active=card.is_active,
        is_digital=card.is_digital,
        eco_points=current_user.eco_points,
        eco_level=current_user.eco_level,
        total_scans=current_user.total_scans,
        created_at=card.created_at.isoformat()
    )
    
    return card_response

@router.put("/", response_model=SmartCardResponse)
async def update_smart_card(
    card_data: SmartCardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update smart card details"""
    
    card = db.query(SmartCard).filter(
        SmartCard.user_id == current_user.id,
        SmartCard.is_active == True
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active smart card found"
        )
    
    # Update fields if provided
    if card_data.full_name is not None:
        card.full_name = card_data.full_name
    if card_data.background_color is not None:
        card.background_color = card_data.background_color
    if card_data.text_color is not None:
        card.text_color = card_data.text_color
    if card_data.status is not None:
        card.status = card_data.status
    
    db.commit()
    db.refresh(card)
    
    card_response = SmartCardResponse(
        id=card.id,
        card_number=card.card_number,
        full_name=card.full_name,
        valid_until=card.valid_until.isoformat(),
        status=card.status,
        card_type=card.card_type,
        background_color=card.background_color,
        text_color=card.text_color,
        is_active=card.is_active,
        is_digital=card.is_digital,
        eco_points=current_user.eco_points,
        eco_level=current_user.eco_level,
        total_scans=current_user.total_scans,
        created_at=card.created_at.isoformat()
    )
    
    return card_response

@router.post("/renew")
async def renew_smart_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Renew smart card (extend validity)"""
    
    card = db.query(SmartCard).filter(
        SmartCard.user_id == current_user.id,
        SmartCard.is_active == True
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active smart card found"
        )
    
    # Extend validity by 2 years
    card.valid_until = datetime.utcnow() + timedelta(days=730)
    db.commit()
    
    return {
        "message": "Smart card renewed successfully",
        "new_valid_until": card.valid_until.isoformat()
    }

@router.delete("/")
async def deactivate_smart_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate smart card"""
    
    card = db.query(SmartCard).filter(
        SmartCard.user_id == current_user.id,
        SmartCard.is_active == True
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active smart card found"
        )
    
    card.is_active = False
    db.commit()
    
    return {"message": "Smart card deactivated successfully"}

@router.get("/validate/{card_number}")
async def validate_card_number(card_number: str, db: Session = Depends(get_db)):
    """Validate card number (public endpoint for verification)"""
    
    card = db.query(SmartCard).filter(
        SmartCard.card_number == card_number,
        SmartCard.is_active == True
    ).first()
    
    if not card:
        return {"valid": False, "message": "Invalid card number"}
    
    # Check if card is expired
    if card.valid_until < datetime.utcnow():
        return {"valid": False, "message": "Card has expired"}
    
    return {
        "valid": True,
        "card_holder": card.full_name,
        "status": card.status,
        "valid_until": card.valid_until.isoformat()
    }
