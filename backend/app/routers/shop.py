"""
Eco Shop router for sustainable products
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel
from app.database import get_db, Base
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# Shop Models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    eco_points_price = Column(Integer, nullable=True)  # Alternative payment with eco points
    
    # Product details
    category = Column(String(100), nullable=False)
    brand = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Sustainability info
    eco_rating = Column(Integer, default=5)  # 1-5 stars
    carbon_footprint = Column(String(100), nullable=True)
    recyclable = Column(Boolean, default=True)
    sustainable_materials = Column(Boolean, default=True)
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order details
    total_amount = Column(Float, nullable=False)
    eco_points_used = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, confirmed, shipped, delivered, cancelled
    
    # Shipping
    shipping_address = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    eco_points_price: Optional[int]
    category: str
    brand: Optional[str]
    image_url: Optional[str]
    eco_rating: int
    carbon_footprint: Optional[str]
    recyclable: bool
    sustainable_materials: bool
    stock_quantity: int
    is_available: bool
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    product_ids: List[int]
    quantities: List[int]
    use_eco_points: bool = False
    shipping_address: str

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    eco_points_used: int
    status: str
    shipping_address: str
    tracking_number: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True

# Sample products data
SAMPLE_PRODUCTS = [
    {
        "name": "Bamboo Toothbrush Set",
        "description": "Eco-friendly bamboo toothbrushes with biodegradable bristles",
        "price": 15.99,
        "eco_points_price": 320,
        "category": "personal_care",
        "brand": "EcoClean",
        "eco_rating": 5,
        "carbon_footprint": "Low",
        "recyclable": True,
        "sustainable_materials": True,
        "stock_quantity": 50
    },
    {
        "name": "Reusable Water Bottle",
        "description": "Stainless steel water bottle with temperature retention",
        "price": 24.99,
        "eco_points_price": 500,
        "category": "drinkware",
        "brand": "HydroEco",
        "eco_rating": 5,
        "carbon_footprint": "Medium",
        "recyclable": True,
        "sustainable_materials": True,
        "stock_quantity": 30
    },
    {
        "name": "Organic Cotton Tote Bag",
        "description": "Durable organic cotton shopping bag",
        "price": 12.99,
        "eco_points_price": 260,
        "category": "bags",
        "brand": "GreenCarry",
        "eco_rating": 4,
        "carbon_footprint": "Low",
        "recyclable": True,
        "sustainable_materials": True,
        "stock_quantity": 75
    },
    {
        "name": "Solar Power Bank",
        "description": "Portable solar charger for mobile devices",
        "price": 49.99,
        "eco_points_price": 1000,
        "category": "electronics",
        "brand": "SolarTech",
        "eco_rating": 5,
        "carbon_footprint": "Medium",
        "recyclable": True,
        "sustainable_materials": False,
        "stock_quantity": 20
    },
    {
        "name": "Beeswax Food Wraps",
        "description": "Natural alternative to plastic wrap",
        "price": 18.99,
        "eco_points_price": 380,
        "category": "kitchen",
        "brand": "BeeGreen",
        "eco_rating": 5,
        "carbon_footprint": "Very Low",
        "recyclable": True,
        "sustainable_materials": True,
        "stock_quantity": 40
    }
]

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    eco_rating: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get products with optional filtering"""
    
    # Initialize products if empty (for demo)
    if db.query(Product).count() == 0:
        for product_data in SAMPLE_PRODUCTS:
            product = Product(**product_data)
            db.add(product)
        db.commit()
    
    query = db.query(Product).filter(Product.is_available == True)
    
    if category:
        query = query.filter(Product.category == category)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if eco_rating is not None:
        query = query.filter(Product.eco_rating >= eco_rating)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get specific product details"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all product categories"""
    
    categories = db.query(Product.category).distinct().all()
    category_list = [cat[0] for cat in categories]
    
    # Add category info
    category_info = {
        "personal_care": {"name": "Personal Care", "icon": "user"},
        "drinkware": {"name": "Drinkware", "icon": "coffee"},
        "bags": {"name": "Bags & Accessories", "icon": "shopping-bag"},
        "electronics": {"name": "Electronics", "icon": "smartphone"},
        "kitchen": {"name": "Kitchen & Home", "icon": "home"}
    }
    
    return [
        {
            "id": cat,
            "name": category_info.get(cat, {}).get("name", cat.title()),
            "icon": category_info.get(cat, {}).get("icon", "package"),
            "count": db.query(Product).filter(Product.category == cat).count()
        }
        for cat in category_list
    ]

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    
    if len(order_data.product_ids) != len(order_data.quantities):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product IDs and quantities must have the same length"
        )
    
    total_amount = 0
    eco_points_needed = 0
    
    # Calculate total and check availability
    for product_id, quantity in zip(order_data.product_ids, order_data.quantities):
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        if product.stock_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
        
        if order_data.use_eco_points and product.eco_points_price:
            eco_points_needed += product.eco_points_price * quantity
        else:
            total_amount += product.price * quantity
    
    # Check eco points if using them
    if order_data.use_eco_points and eco_points_needed > current_user.eco_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient eco points"
        )
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        eco_points_used=eco_points_needed if order_data.use_eco_points else 0,
        shipping_address=order_data.shipping_address,
        status="confirmed"
    )
    
    db.add(new_order)
    
    # Update stock and user points
    for product_id, quantity in zip(order_data.product_ids, order_data.quantities):
        product = db.query(Product).filter(Product.id == product_id).first()
        product.stock_quantity -= quantity
    
    if order_data.use_eco_points:
        current_user.eco_points -= eco_points_needed
    else:
        # Award eco points for purchase
        points_earned = int(total_amount * settings.POINTS_PER_SHOP_PURCHASE)
        current_user.add_eco_points(points_earned, "shop_purchase")
    
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's order history"""
    
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order details"""
    
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized product recommendations"""
    
    # Simple recommendation based on eco level
    if current_user.eco_level in ["Eco Master", "Eco Champion"]:
        recommended_categories = ["electronics", "kitchen"]
    elif current_user.eco_level == "Eco Warrior":
        recommended_categories = ["drinkware", "bags"]
    else:
        recommended_categories = ["personal_care", "bags"]
    
    recommendations = db.query(Product).filter(
        Product.category.in_(recommended_categories),
        Product.is_available == True
    ).limit(6).all()
    
    return {
        "message": f"Recommendations for {current_user.eco_level}",
        "products": recommendations
    }
