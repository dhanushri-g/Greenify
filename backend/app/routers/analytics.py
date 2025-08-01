"""
Analytics router for waste management insights
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.waste import WasteScan
from app.core.security import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

# Pydantic models
class WasteStats(BaseModel):
    total_scans: int
    categories_detected: int
    accuracy_rate: float
    eco_points_earned: int
    carbon_footprint_saved: float

class CategoryBreakdown(BaseModel):
    category: str
    count: int
    percentage: float
    eco_impact: str

class TimeSeriesData(BaseModel):
    date: str
    scans: int
    eco_points: int

class EnvironmentalImpact(BaseModel):
    plastic_items_recycled: int
    trees_saved: float
    water_saved_liters: float
    co2_reduced_kg: float

@router.get("/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics overview"""
    
    # Basic stats
    total_scans = current_user.total_scans
    correct_sorts = current_user.correct_sorts
    accuracy_rate = (correct_sorts / max(total_scans, 1)) * 100
    
    # Category breakdown
    category_stats = db.query(
        WasteScan.detected_category,
        func.count(WasteScan.id).label('count')
    ).filter(
        WasteScan.user_id == current_user.id
    ).group_by(WasteScan.detected_category).all()
    
    total_categorized = sum(stat.count for stat in category_stats)
    
    category_breakdown = [
        {
            "category": stat.detected_category,
            "count": stat.count,
            "percentage": (stat.count / max(total_categorized, 1)) * 100,
            "eco_impact": get_category_impact(stat.detected_category)
        }
        for stat in category_stats
    ]
    
    # Environmental impact calculation
    environmental_impact = calculate_environmental_impact(category_stats)
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_scans = db.query(WasteScan).filter(
        WasteScan.user_id == current_user.id,
        WasteScan.scanned_at >= thirty_days_ago
    ).count()
    
    # Time series data (last 7 days)
    time_series = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        day_scans = db.query(WasteScan).filter(
            WasteScan.user_id == current_user.id,
            func.date(WasteScan.scanned_at) == date.date()
        ).count()
        
        time_series.append({
            "date": date.strftime("%Y-%m-%d"),
            "scans": day_scans,
            "eco_points": day_scans * 10  # Simplified calculation
        })
    
    return {
        "overview": {
            "total_scans": total_scans,
            "correct_sorts": correct_sorts,
            "accuracy_rate": round(accuracy_rate, 1),
            "eco_points": current_user.eco_points,
            "eco_level": current_user.eco_level,
            "recent_activity": recent_scans
        },
        "category_breakdown": category_breakdown,
        "environmental_impact": environmental_impact,
        "time_series": list(reversed(time_series)),
        "achievements": get_user_achievements(current_user),
        "goals": get_user_goals(current_user)
    }

@router.get("/environmental-impact")
async def get_environmental_impact(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed environmental impact metrics"""
    
    category_stats = db.query(
        WasteScan.detected_category,
        func.count(WasteScan.id).label('count')
    ).filter(
        WasteScan.user_id == current_user.id
    ).group_by(WasteScan.detected_category).all()
    
    impact = calculate_environmental_impact(category_stats)
    
    # Additional metrics
    monthly_impact = calculate_monthly_impact(current_user, db)
    
    return {
        "total_impact": impact,
        "monthly_trends": monthly_impact,
        "comparisons": {
            "vs_average_user": {
                "scans": "+25%",
                "recycling_rate": "+15%",
                "eco_points": "+30%"
            },
            "vs_last_month": {
                "scans": "+10%",
                "accuracy": "+5%",
                "impact": "+12%"
            }
        },
        "projections": {
            "yearly_co2_reduction": impact["co2_reduced_kg"] * 12,
            "yearly_water_saved": impact["water_saved_liters"] * 12,
            "yearly_trees_saved": impact["trees_saved"] * 12
        }
    }

@router.get("/leaderboard")
async def get_leaderboard(
    period: str = Query("monthly", regex="^(weekly|monthly|all_time)$"),
    db: Session = Depends(get_db)
):
    """Get leaderboard rankings"""
    
    # Calculate date filter based on period
    if period == "weekly":
        date_filter = datetime.utcnow() - timedelta(days=7)
    elif period == "monthly":
        date_filter = datetime.utcnow() - timedelta(days=30)
    else:
        date_filter = datetime.min
    
    # Get top users by eco points
    top_users = db.query(User).filter(
        User.is_active == True,
        User.created_at >= date_filter if period != "all_time" else True
    ).order_by(User.eco_points.desc()).limit(10).all()
    
    leaderboard = []
    for i, user in enumerate(top_users, 1):
        leaderboard.append({
            "rank": i,
            "username": user.username,
            "eco_points": user.eco_points,
            "eco_level": user.eco_level,
            "total_scans": user.total_scans,
            "accuracy_rate": (user.correct_sorts / max(user.total_scans, 1)) * 100
        })
    
    return {
        "period": period,
        "leaderboard": leaderboard,
        "user_rank": get_user_rank(db, period),
        "total_participants": len(leaderboard)
    }

@router.get("/trends")
async def get_waste_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get waste detection trends over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily scan counts
    daily_scans = db.query(
        func.date(WasteScan.scanned_at).label('date'),
        func.count(WasteScan.id).label('count')
    ).filter(
        WasteScan.user_id == current_user.id,
        WasteScan.scanned_at >= start_date
    ).group_by(func.date(WasteScan.scanned_at)).all()
    
    # Category trends
    category_trends = db.query(
        WasteScan.detected_category,
        func.date(WasteScan.scanned_at).label('date'),
        func.count(WasteScan.id).label('count')
    ).filter(
        WasteScan.user_id == current_user.id,
        WasteScan.scanned_at >= start_date
    ).group_by(WasteScan.detected_category, func.date(WasteScan.scanned_at)).all()
    
    return {
        "period": f"Last {days} days",
        "daily_scans": [
            {"date": str(scan.date), "count": scan.count}
            for scan in daily_scans
        ],
        "category_trends": organize_category_trends(category_trends),
        "insights": generate_trend_insights(daily_scans, category_trends)
    }

def get_category_impact(category: str) -> str:
    """Get environmental impact description for category"""
    impacts = {
        "plastic": "High impact - reduces ocean pollution",
        "paper": "Medium impact - saves trees",
        "glass": "High impact - infinitely recyclable",
        "metal": "High impact - valuable resource recovery",
        "organic": "Medium impact - reduces methane emissions",
        "electronic": "Very high impact - prevents toxic waste",
        "hazardous": "Critical impact - prevents environmental damage",
        "textile": "Medium impact - reduces fast fashion waste",
        "other": "Variable impact"
    }
    return impacts.get(category, "Positive impact")

def calculate_environmental_impact(category_stats) -> dict:
    """Calculate environmental impact based on waste categories"""
    
    # Impact factors per item (simplified calculations)
    impact_factors = {
        "plastic": {"co2": 0.5, "water": 2.0, "trees": 0.001},
        "paper": {"co2": 0.3, "water": 1.5, "trees": 0.01},
        "glass": {"co2": 0.2, "water": 0.5, "trees": 0.0},
        "metal": {"co2": 0.8, "water": 3.0, "trees": 0.002},
        "organic": {"co2": 0.1, "water": 0.2, "trees": 0.0},
        "electronic": {"co2": 2.0, "water": 5.0, "trees": 0.005},
        "hazardous": {"co2": 1.0, "water": 2.0, "trees": 0.001},
        "textile": {"co2": 0.4, "water": 1.0, "trees": 0.002},
        "other": {"co2": 0.2, "water": 0.5, "trees": 0.001}
    }
    
    total_co2 = 0
    total_water = 0
    total_trees = 0
    plastic_items = 0
    
    for stat in category_stats:
        category = stat.detected_category
        count = stat.count
        
        if category in impact_factors:
            factors = impact_factors[category]
            total_co2 += count * factors["co2"]
            total_water += count * factors["water"]
            total_trees += count * factors["trees"]
            
            if category == "plastic":
                plastic_items += count
    
    return {
        "plastic_items_recycled": plastic_items,
        "trees_saved": round(total_trees, 2),
        "water_saved_liters": round(total_water, 1),
        "co2_reduced_kg": round(total_co2, 1)
    }

def calculate_monthly_impact(user: User, db: Session) -> list:
    """Calculate monthly environmental impact trends"""
    
    monthly_data = []
    for i in range(6):  # Last 6 months
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_scans = db.query(WasteScan).filter(
            WasteScan.user_id == user.id,
            WasteScan.scanned_at >= month_start,
            WasteScan.scanned_at < month_end
        ).count()
        
        monthly_data.append({
            "month": month_start.strftime("%Y-%m"),
            "scans": month_scans,
            "estimated_impact": month_scans * 0.5  # Simplified
        })
    
    return list(reversed(monthly_data))

def get_user_achievements(user: User) -> list:
    """Get user achievements based on activity"""
    
    achievements = []
    
    if user.total_scans >= 1:
        achievements.append({
            "id": "first_scan",
            "name": "First Steps",
            "description": "Completed your first waste scan",
            "unlocked": True,
            "date_unlocked": "2024-01-01"
        })
    
    if user.total_scans >= 50:
        achievements.append({
            "id": "scanner_pro",
            "name": "Scanner Pro",
            "description": "Completed 50 waste scans",
            "unlocked": True,
            "date_unlocked": "2024-01-15"
        })
    
    if user.eco_points >= 1000:
        achievements.append({
            "id": "eco_warrior",
            "name": "Eco Warrior",
            "description": "Earned 1000 eco points",
            "unlocked": True,
            "date_unlocked": "2024-01-20"
        })
    
    return achievements

def get_user_goals(user: User) -> list:
    """Get user goals and progress"""
    
    return [
        {
            "id": "weekly_scans",
            "name": "Weekly Scanner",
            "description": "Complete 10 scans this week",
            "target": 10,
            "current": min(user.total_scans % 10, 10),
            "progress": min((user.total_scans % 10) / 10 * 100, 100)
        },
        {
            "id": "accuracy_goal",
            "name": "Accuracy Master",
            "description": "Achieve 90% accuracy rate",
            "target": 90,
            "current": (user.correct_sorts / max(user.total_scans, 1)) * 100,
            "progress": min((user.correct_sorts / max(user.total_scans, 1)) * 100 / 90 * 100, 100)
        }
    ]

def get_user_rank(db: Session, period: str) -> int:
    """Get user's rank in leaderboard"""
    # Simplified - would need actual user context
    return 42

def organize_category_trends(category_trends) -> dict:
    """Organize category trends by category"""
    organized = {}
    for trend in category_trends:
        category = trend.detected_category
        if category not in organized:
            organized[category] = []
        organized[category].append({
            "date": str(trend.date),
            "count": trend.count
        })
    return organized

def generate_trend_insights(daily_scans, category_trends) -> list:
    """Generate insights from trend data"""
    insights = []
    
    if len(daily_scans) > 1:
        recent_avg = sum(scan.count for scan in daily_scans[-7:]) / 7
        older_avg = sum(scan.count for scan in daily_scans[:-7]) / max(len(daily_scans) - 7, 1)
        
        if recent_avg > older_avg:
            insights.append("Your scanning activity has increased recently!")
        elif recent_avg < older_avg:
            insights.append("Your scanning activity has decreased. Try to scan more items!")
    
    insights.append("Keep up the great work contributing to environmental sustainability!")
    
    return insights
