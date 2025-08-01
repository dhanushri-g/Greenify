"""
DIY Projects router for upcycling and creative waste reuse
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel
from app.database import get_db, Base
from app.models.user import User
from app.core.security import get_current_user
from app.core.config import settings
import os
import uuid
import aiofiles

router = APIRouter()

# DIY Project Model
class DIYProject(Base):
    __tablename__ = "diy_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Project details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    
    # Project metadata
    difficulty_level = Column(String(50), default="Easy")  # Easy, Medium, Hard
    estimated_time = Column(String(100), nullable=True)  # e.g., "2 hours"
    waste_categories = Column(JSON, nullable=True)  # List of waste types used
    materials_needed = Column(JSON, nullable=True)  # List of additional materials
    tools_required = Column(JSON, nullable=True)  # List of tools needed
    
    # Media
    image_urls = Column(JSON, nullable=True)  # List of image URLs
    video_url = Column(String(500), nullable=True)
    
    # Engagement
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    # Status
    is_featured = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models
class DIYProjectCreate(BaseModel):
    title: str
    description: str
    instructions: str
    difficulty_level: str = "Easy"
    estimated_time: Optional[str] = None
    waste_categories: List[str] = []
    materials_needed: List[str] = []
    tools_required: List[str] = []
    video_url: Optional[str] = None

class DIYProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty_level: Optional[str] = None
    estimated_time: Optional[str] = None
    waste_categories: Optional[List[str]] = None
    materials_needed: Optional[List[str]] = None
    tools_required: Optional[List[str]] = None
    video_url: Optional[str] = None

class DIYProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    instructions: str
    difficulty_level: str
    estimated_time: Optional[str]
    waste_categories: List[str]
    materials_needed: List[str]
    tools_required: List[str]
    image_urls: List[str]
    video_url: Optional[str]
    likes: int
    views: int
    saves: int
    is_featured: bool
    created_at: str
    author: str
    
    class Config:
        from_attributes = True

# Sample DIY projects
SAMPLE_PROJECTS = [
    {
        "title": "Plastic Bottle Planter",
        "description": "Transform plastic bottles into beautiful hanging planters for your garden",
        "instructions": "1. Clean the plastic bottle thoroughly\n2. Cut the bottle in half\n3. Make drainage holes in the bottom\n4. Decorate with paint or fabric\n5. Add soil and plants\n6. Hang using string or wire",
        "difficulty_level": "Easy",
        "estimated_time": "30 minutes",
        "waste_categories": ["plastic"],
        "materials_needed": ["Paint", "Soil", "Plants", "String"],
        "tools_required": ["Scissors", "Drill"],
        "user_id": 1
    },
    {
        "title": "Cardboard Storage Organizer",
        "description": "Create a multi-compartment organizer from cardboard boxes",
        "instructions": "1. Collect various sized cardboard boxes\n2. Cut boxes to desired heights\n3. Create dividers from cardboard sheets\n4. Glue compartments together\n5. Cover with decorative paper\n6. Label each compartment",
        "difficulty_level": "Medium",
        "estimated_time": "2 hours",
        "waste_categories": ["paper"],
        "materials_needed": ["Glue", "Decorative paper", "Labels"],
        "tools_required": ["Scissors", "Ruler", "Pencil"],
        "user_id": 1
    },
    {
        "title": "Glass Jar Lanterns",
        "description": "Turn glass jars into beautiful outdoor lanterns",
        "instructions": "1. Clean glass jars thoroughly\n2. Wrap wire around jar neck for hanging\n3. Add battery-operated LED lights\n4. Decorate with frosted spray paint\n5. Add decorative elements like stones\n6. Hang in garden or patio",
        "difficulty_level": "Easy",
        "estimated_time": "45 minutes",
        "waste_categories": ["glass"],
        "materials_needed": ["Wire", "LED lights", "Frosted paint", "Decorative stones"],
        "tools_required": ["Wire cutters", "Pliers"],
        "user_id": 1
    }
]

@router.get("/", response_model=List[DIYProjectResponse])
async def get_diy_projects(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    featured: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get DIY projects with optional filtering"""
    
    # Initialize sample projects if empty
    if db.query(DIYProject).count() == 0:
        for project_data in SAMPLE_PROJECTS:
            project = DIYProject(**project_data)
            db.add(project)
        db.commit()
    
    query = db.query(DIYProject).filter(
        DIYProject.is_public == True,
        DIYProject.is_approved == True
    )
    
    if category:
        query = query.filter(DIYProject.waste_categories.contains([category]))
    if difficulty:
        query = query.filter(DIYProject.difficulty_level == difficulty)
    if featured is not None:
        query = query.filter(DIYProject.is_featured == featured)
    
    projects = query.order_by(DIYProject.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add author information
    result = []
    for project in projects:
        user = db.query(User).filter(User.id == project.user_id).first()
        project_dict = {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "instructions": project.instructions,
            "difficulty_level": project.difficulty_level,
            "estimated_time": project.estimated_time,
            "waste_categories": project.waste_categories or [],
            "materials_needed": project.materials_needed or [],
            "tools_required": project.tools_required or [],
            "image_urls": project.image_urls or [],
            "video_url": project.video_url,
            "likes": project.likes,
            "views": project.views,
            "saves": project.saves,
            "is_featured": project.is_featured,
            "created_at": project.created_at.isoformat(),
            "author": user.username if user else "Anonymous"
        }
        result.append(project_dict)
    
    return result

@router.get("/{project_id}", response_model=DIYProjectResponse)
async def get_diy_project(project_id: int, db: Session = Depends(get_db)):
    """Get specific DIY project details"""
    
    project = db.query(DIYProject).filter(
        DIYProject.id == project_id,
        DIYProject.is_public == True,
        DIYProject.is_approved == True
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Increment view count
    project.views += 1
    db.commit()
    
    # Get author info
    user = db.query(User).filter(User.id == project.user_id).first()
    
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "instructions": project.instructions,
        "difficulty_level": project.difficulty_level,
        "estimated_time": project.estimated_time,
        "waste_categories": project.waste_categories or [],
        "materials_needed": project.materials_needed or [],
        "tools_required": project.tools_required or [],
        "image_urls": project.image_urls or [],
        "video_url": project.video_url,
        "likes": project.likes,
        "views": project.views,
        "saves": project.saves,
        "is_featured": project.is_featured,
        "created_at": project.created_at.isoformat(),
        "author": user.username if user else "Anonymous"
    }

@router.post("/", response_model=DIYProjectResponse)
async def create_diy_project(
    project_data: DIYProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new DIY project"""
    
    new_project = DIYProject(
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
        instructions=project_data.instructions,
        difficulty_level=project_data.difficulty_level,
        estimated_time=project_data.estimated_time,
        waste_categories=project_data.waste_categories,
        materials_needed=project_data.materials_needed,
        tools_required=project_data.tools_required,
        video_url=project_data.video_url
    )
    
    db.add(new_project)
    
    # Award eco points for creating project
    current_user.add_eco_points(settings.POINTS_PER_DIY_PROJECT, "diy_project_creation")
    
    db.commit()
    db.refresh(new_project)
    
    return {
        "id": new_project.id,
        "title": new_project.title,
        "description": new_project.description,
        "instructions": new_project.instructions,
        "difficulty_level": new_project.difficulty_level,
        "estimated_time": new_project.estimated_time,
        "waste_categories": new_project.waste_categories or [],
        "materials_needed": new_project.materials_needed or [],
        "tools_required": new_project.tools_required or [],
        "image_urls": new_project.image_urls or [],
        "video_url": new_project.video_url,
        "likes": new_project.likes,
        "views": new_project.views,
        "saves": new_project.saves,
        "is_featured": new_project.is_featured,
        "created_at": new_project.created_at.isoformat(),
        "author": current_user.username
    }

@router.post("/{project_id}/images")
async def upload_project_images(
    project_id: int,
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload images for a DIY project"""
    
    project = db.query(DIYProject).filter(
        DIYProject.id == project_id,
        DIYProject.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or not owned by user"
        )
    
    uploaded_urls = []
    
    for image in images:
        # Validate file type
        if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
            continue
        
        # Validate file size
        if image.size > settings.MAX_IMAGE_SIZE:
            continue
        
        try:
            # Generate unique filename
            file_extension = image.filename.split('.')[-1]
            unique_filename = f"diy_{project_id}_{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, "diy_images", unique_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await image.read()
                await f.write(content)
            
            uploaded_urls.append(f"/uploads/diy_images/{unique_filename}")
            
        except Exception as e:
            continue
    
    # Update project with new image URLs
    current_urls = project.image_urls or []
    project.image_urls = current_urls + uploaded_urls
    db.commit()
    
    return {
        "message": f"Uploaded {len(uploaded_urls)} images successfully",
        "image_urls": uploaded_urls
    }

@router.post("/{project_id}/like")
async def like_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a DIY project"""
    
    project = db.query(DIYProject).filter(DIYProject.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.likes += 1
    db.commit()
    
    return {"message": "Project liked successfully", "total_likes": project.likes}

@router.get("/my/projects", response_model=List[DIYProjectResponse])
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's DIY projects"""
    
    projects = db.query(DIYProject).filter(
        DIYProject.user_id == current_user.id
    ).order_by(DIYProject.created_at.desc()).all()
    
    result = []
    for project in projects:
        project_dict = {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "instructions": project.instructions,
            "difficulty_level": project.difficulty_level,
            "estimated_time": project.estimated_time,
            "waste_categories": project.waste_categories or [],
            "materials_needed": project.materials_needed or [],
            "tools_required": project.tools_required or [],
            "image_urls": project.image_urls or [],
            "video_url": project.video_url,
            "likes": project.likes,
            "views": project.views,
            "saves": project.saves,
            "is_featured": project.is_featured,
            "created_at": project.created_at.isoformat(),
            "author": current_user.username
        }
        result.append(project_dict)
    
    return result

@router.get("/categories/stats")
async def get_category_stats(db: Session = Depends(get_db)):
    """Get statistics for DIY project categories"""
    
    # Get all waste categories used in projects
    all_projects = db.query(DIYProject).filter(DIYProject.is_public == True).all()
    
    category_counts = {}
    for project in all_projects:
        if project.waste_categories:
            for category in project.waste_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        "total_projects": len(all_projects),
        "category_breakdown": [
            {"category": cat, "count": count, "percentage": (count / len(all_projects)) * 100}
            for cat, count in category_counts.items()
        ],
        "difficulty_breakdown": {
            "Easy": db.query(DIYProject).filter(DIYProject.difficulty_level == "Easy").count(),
            "Medium": db.query(DIYProject).filter(DIYProject.difficulty_level == "Medium").count(),
            "Hard": db.query(DIYProject).filter(DIYProject.difficulty_level == "Hard").count()
        }
    }
