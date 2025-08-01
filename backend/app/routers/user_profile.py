"""
User profile management router
"""

import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user, get_password_hash, verify_password
from app.core.config import settings
import aiofiles

router = APIRouter()

# Pydantic models
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class ProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    bio: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    is_premium: bool
    eco_points: int
    total_scans: int
    correct_sorts: int
    eco_level: str
    created_at: str
    last_login: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    # Update fields if provided
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.location is not None:
        current_user.location = profile_data.location
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar"""
    
    # Validate file type
    if avatar.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG images are allowed."
        )
    
    # Validate file size (limit to 2MB for avatars)
    max_avatar_size = 2 * 1024 * 1024  # 2MB
    if avatar.size > max_avatar_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Avatar file too large. Maximum size is 2MB"
        )
    
    try:
        # Generate unique filename
        file_extension = avatar.filename.split('.')[-1]
        unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, "user_avatars", unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Delete old avatar if exists
        if current_user.avatar_url:
            old_filename = current_user.avatar_url.split('/')[-1]
            old_path = os.path.join(settings.UPLOAD_DIR, "user_avatars", old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # Save new avatar
        async with aiofiles.open(file_path, 'wb') as f:
            content = await avatar.read()
            await f.write(content)
        
        # Update user record
        current_user.avatar_url = f"/uploads/user_avatars/{unique_filename}"
        db.commit()
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": current_user.avatar_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading avatar: {str(e)}"
        )

@router.delete("/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user avatar"""
    
    if not current_user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No avatar to delete"
        )
    
    # Delete file
    filename = current_user.avatar_url.split('/')[-1]
    file_path = os.path.join(settings.UPLOAD_DIR, "user_avatars", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Update user record
    current_user.avatar_url = None
    db.commit()
    
    return {"message": "Avatar deleted successfully"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new password (add your own validation rules)
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.get("/eco-progress")
async def get_eco_progress(current_user: User = Depends(get_current_user)):
    """Get detailed eco progress information"""
    
    progress = current_user.eco_level_progress
    
    # Calculate additional metrics
    scan_streak = 7  # This would be calculated from actual scan dates
    weekly_goal = 50  # Points per week goal
    weekly_progress = min(100, (current_user.eco_points % 100))  # Simplified calculation
    
    return {
        "eco_points": current_user.eco_points,
        "eco_level": current_user.eco_level,
        "level_progress": progress,
        "total_scans": current_user.total_scans,
        "correct_sorts": current_user.correct_sorts,
        "accuracy_rate": (current_user.correct_sorts / max(current_user.total_scans, 1)) * 100,
        "scan_streak": scan_streak,
        "weekly_goal": weekly_goal,
        "weekly_progress": weekly_progress,
        "achievements": [
            {
                "id": 1,
                "name": "First Scan",
                "description": "Complete your first waste scan",
                "unlocked": current_user.total_scans >= 1,
                "icon": "camera"
            },
            {
                "id": 2,
                "name": "Eco Warrior",
                "description": "Reach 1000 eco points",
                "unlocked": current_user.eco_points >= 1000,
                "icon": "shield"
            },
            {
                "id": 3,
                "name": "Perfect Sorter",
                "description": "Get 10 correct classifications in a row",
                "unlocked": current_user.correct_sorts >= 10,
                "icon": "target"
            }
        ]
    }

@router.post("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account"""
    
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}

@router.get("/export-data")
async def export_user_data(current_user: User = Depends(get_current_user)):
    """Export user data (GDPR compliance)"""
    
    # In a real implementation, this would generate a comprehensive data export
    return {
        "user_data": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "bio": current_user.bio,
            "location": current_user.location,
            "phone": current_user.phone,
            "eco_points": current_user.eco_points,
            "total_scans": current_user.total_scans,
            "correct_sorts": current_user.correct_sorts,
            "eco_level": current_user.eco_level,
            "created_at": current_user.created_at,
            "last_login": current_user.last_login
        },
        "export_date": "2024-01-01T00:00:00Z",
        "note": "This is a simplified export. Full implementation would include all user data."
    }
