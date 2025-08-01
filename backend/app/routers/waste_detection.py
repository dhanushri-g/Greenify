"""
Waste detection router for AI-powered image classification
"""

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.waste import WasteScan, WasteCategory
from app.core.security import get_current_user
from app.services.ai_detection import waste_detector
from app.core.config import settings
import aiofiles

router = APIRouter()

# Pydantic models
class WasteScanResponse(BaseModel):
    id: int
    detected_category: str
    confidence_score: float
    is_recyclable: bool
    disposal_method: str
    environmental_impact: str
    recycling_tips: str
    image_url: str
    scanned_at: str
    
    class Config:
        from_attributes = True

class DetectionResult(BaseModel):
    detected_category: str
    confidence_score: float
    alternatives: List[dict]
    category_info: dict
    is_confident: bool
    quality_analysis: dict

class FeedbackRequest(BaseModel):
    scan_id: int
    user_confirmed: bool
    user_correction: Optional[str] = None
    feedback_notes: Optional[str] = None

@router.post("/scan", response_model=DetectionResult)
async def scan_waste(
    image: UploadFile = File(...),
    location: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scan waste image and classify using AI"""
    
    # Validate file type
    if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG images are allowed."
        )
    
    # Validate file size
    if image.size > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_IMAGE_SIZE / (1024*1024):.1f}MB"
        )
    
    try:
        # Generate unique filename
        file_extension = image.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, "waste_images", unique_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        # Analyze image quality
        quality_analysis = waste_detector.analyze_image_quality(file_path)
        
        # Perform AI detection
        detection_result = waste_detector.detect_waste(file_path)
        
        # Save scan to database
        waste_scan = WasteScan(
            user_id=current_user.id,
            image_url=f"/uploads/waste_images/{unique_filename}",
            image_filename=unique_filename,
            image_size=image.size,
            detected_category=detection_result["detected_category"],
            confidence_score=detection_result["confidence_score"],
            alternative_categories=detection_result["alternatives"],
            is_recyclable=detection_result["category_info"]["is_recyclable"],
            disposal_method=detection_result["category_info"]["disposal_method"],
            environmental_impact=detection_result["category_info"]["environmental_impact"],
            recycling_tips=detection_result["category_info"]["recycling_tips"],
            scan_location=location,
            latitude=latitude,
            longitude=longitude
        )
        
        db.add(waste_scan)
        
        # Update user statistics
        current_user.total_scans += 1
        current_user.add_eco_points(settings.POINTS_PER_SCAN, "waste_scan")
        
        db.commit()
        db.refresh(waste_scan)
        
        # Combine results
        result = {
            **detection_result,
            "quality_analysis": quality_analysis,
            "scan_id": waste_scan.id,
            "eco_points_earned": settings.POINTS_PER_SCAN
        }
        
        return result
        
    except Exception as e:
        # Clean up file if error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/history", response_model=List[WasteScanResponse])
async def get_scan_history(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's scan history"""
    
    query = db.query(WasteScan).filter(WasteScan.user_id == current_user.id)
    
    if category:
        query = query.filter(WasteScan.detected_category == category)
    
    scans = query.order_by(WasteScan.scanned_at.desc()).offset(skip).limit(limit).all()
    
    return scans

@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on scan results"""
    
    # Get the scan
    scan = db.query(WasteScan).filter(
        WasteScan.id == feedback.scan_id,
        WasteScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Update scan with feedback
    scan.user_confirmed = feedback.user_confirmed
    scan.user_correction = feedback.user_correction
    scan.feedback_notes = feedback.feedback_notes
    
    # Award points for correct classification
    if feedback.user_confirmed:
        current_user.correct_sorts += 1
        current_user.add_eco_points(settings.POINTS_PER_CORRECT_SORT, "correct_classification")
    
    db.commit()
    
    return {
        "message": "Feedback submitted successfully",
        "eco_points_earned": settings.POINTS_PER_CORRECT_SORT if feedback.user_confirmed else 0
    }

@router.get("/categories")
async def get_waste_categories(db: Session = Depends(get_db)):
    """Get all waste categories with information"""
    
    categories = []
    for category_name in settings.WASTE_CATEGORIES:
        category_info = waste_detector._get_category_info(category_name)
        categories.append({
            "name": category_name,
            "display_name": category_name.title(),
            **category_info
        })
    
    return categories

@router.get("/stats")
async def get_detection_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's detection statistics"""
    
    # Get category breakdown
    category_stats = db.query(
        WasteScan.detected_category,
        db.func.count(WasteScan.id).label('count')
    ).filter(
        WasteScan.user_id == current_user.id
    ).group_by(WasteScan.detected_category).all()
    
    # Calculate accuracy
    total_feedback = db.query(WasteScan).filter(
        WasteScan.user_id == current_user.id,
        WasteScan.user_confirmed.isnot(None)
    ).count()
    
    correct_feedback = db.query(WasteScan).filter(
        WasteScan.user_id == current_user.id,
        WasteScan.user_confirmed == True
    ).count()
    
    accuracy = (correct_feedback / total_feedback * 100) if total_feedback > 0 else 0
    
    return {
        "total_scans": current_user.total_scans,
        "correct_sorts": current_user.correct_sorts,
        "accuracy_percentage": round(accuracy, 1),
        "eco_points": current_user.eco_points,
        "eco_level": current_user.eco_level,
        "category_breakdown": [
            {"category": stat.detected_category, "count": stat.count}
            for stat in category_stats
        ],
        "level_progress": current_user.eco_level_progress
    }

@router.delete("/scan/{scan_id}")
async def delete_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scan record"""
    
    scan = db.query(WasteScan).filter(
        WasteScan.id == scan_id,
        WasteScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Delete image file
    image_path = os.path.join(settings.UPLOAD_DIR, "waste_images", scan.image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # Delete database record
    db.delete(scan)
    db.commit()
    
    return {"message": "Scan deleted successfully"}
