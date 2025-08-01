"""
AI-powered waste detection service using TensorFlow
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from PIL import Image
import tensorflow as tf
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WasteDetectionService:
    """AI service for waste classification and detection"""
    
    def __init__(self):
        self.model = None
        self.class_names = [
            "plastic", "paper", "glass", "metal", "organic", 
            "electronic", "hazardous", "textile", "other"
        ]
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained waste classification model"""
        try:
            if os.path.exists(settings.MODEL_PATH):
                self.model = tf.keras.models.load_model(settings.MODEL_PATH)
                logger.info(f"Model loaded successfully from {settings.MODEL_PATH}")
            else:
                # Create a simple mock model for demonstration
                self.model = self._create_mock_model()
                logger.warning("Using mock model - train and save a real model for production")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration purposes"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(224, 224, 3)),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(len(self.class_names), activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for model prediction"""
        try:
            # Load and resize image
            image = Image.open(image_path)
            image = image.convert('RGB')
            image = image.resize((224, 224))
            
            # Convert to numpy array and normalize
            image_array = np.array(image) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def detect_waste(self, image_path: str) -> Dict:
        """Detect waste category from image"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Make prediction
            predictions = self.model.predict(processed_image)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            
            # Get predicted category
            predicted_category = self.class_names[predicted_class_idx]
            
            # Get alternative predictions
            alternatives = []
            sorted_indices = np.argsort(predictions[0])[::-1]
            for i in sorted_indices[1:4]:  # Top 3 alternatives
                alternatives.append({
                    "category": self.class_names[i],
                    "confidence": float(predictions[0][i])
                })
            
            # Get category information
            category_info = self._get_category_info(predicted_category)
            
            result = {
                "detected_category": predicted_category,
                "confidence_score": confidence,
                "alternatives": alternatives,
                "category_info": category_info,
                "is_confident": confidence >= settings.CONFIDENCE_THRESHOLD
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in waste detection: {e}")
            raise
    
    def _get_category_info(self, category: str) -> Dict:
        """Get detailed information about waste category"""
        category_data = {
            "plastic": {
                "is_recyclable": True,
                "disposal_method": "Recycling bin (clean containers only)",
                "environmental_impact": "Takes 450+ years to decompose. Causes marine pollution.",
                "recycling_tips": "Clean containers, remove labels, separate by type",
                "color_code": "#FF6B6B",
                "preparation_steps": [
                    "Rinse containers thoroughly",
                    "Remove all labels and caps",
                    "Check recycling number",
                    "Separate by plastic type"
                ]
            },
            "paper": {
                "is_recyclable": True,
                "disposal_method": "Paper recycling bin",
                "environmental_impact": "Decomposes in 2-6 weeks. Saves trees when recycled.",
                "recycling_tips": "Keep dry, remove staples, no wax coating",
                "color_code": "#4ECDC4",
                "preparation_steps": [
                    "Remove any plastic coating",
                    "Take out staples and clips",
                    "Keep paper dry",
                    "Separate by paper type"
                ]
            },
            "glass": {
                "is_recyclable": True,
                "disposal_method": "Glass recycling bin",
                "environmental_impact": "Takes 1 million years to decompose. 100% recyclable.",
                "recycling_tips": "Separate by color, remove caps and lids",
                "color_code": "#45B7D1",
                "preparation_steps": [
                    "Remove all caps and lids",
                    "Rinse containers",
                    "Separate by color",
                    "Remove any metal parts"
                ]
            },
            "metal": {
                "is_recyclable": True,
                "disposal_method": "Metal recycling bin",
                "environmental_impact": "Takes 50-200 years to decompose. Highly valuable for recycling.",
                "recycling_tips": "Clean cans, separate aluminum from steel",
                "color_code": "#96CEB4",
                "preparation_steps": [
                    "Clean all food residue",
                    "Remove labels if possible",
                    "Separate aluminum from steel",
                    "Flatten cans to save space"
                ]
            },
            "organic": {
                "is_recyclable": False,
                "disposal_method": "Compost bin or organic waste",
                "environmental_impact": "Decomposes in 2-5 months. Creates methane in landfills.",
                "recycling_tips": "Compost at home or use organic waste collection",
                "color_code": "#FECA57",
                "preparation_steps": [
                    "Remove any packaging",
                    "Cut into smaller pieces",
                    "Mix with brown materials",
                    "Keep compost moist"
                ]
            },
            "electronic": {
                "is_recyclable": True,
                "disposal_method": "E-waste collection center",
                "environmental_impact": "Contains toxic materials. Valuable metals can be recovered.",
                "recycling_tips": "Take to certified e-waste recycler, remove batteries",
                "color_code": "#FF9FF3",
                "preparation_steps": [
                    "Remove all batteries",
                    "Delete personal data",
                    "Keep original packaging if possible",
                    "Take to certified recycler"
                ]
            },
            "hazardous": {
                "is_recyclable": False,
                "disposal_method": "Hazardous waste facility",
                "environmental_impact": "Extremely harmful to environment and health.",
                "recycling_tips": "Never put in regular trash. Use special collection events.",
                "color_code": "#FF6B6B",
                "preparation_steps": [
                    "Keep in original container",
                    "Do not mix with other materials",
                    "Label clearly",
                    "Take to hazardous waste facility"
                ]
            },
            "textile": {
                "is_recyclable": True,
                "disposal_method": "Textile recycling or donation",
                "environmental_impact": "Takes 200+ years to decompose. Fast fashion increases waste.",
                "recycling_tips": "Donate if usable, recycle if damaged",
                "color_code": "#A8E6CF",
                "preparation_steps": [
                    "Clean and dry items",
                    "Separate by condition",
                    "Remove non-textile parts",
                    "Donate or recycle appropriately"
                ]
            },
            "other": {
                "is_recyclable": False,
                "disposal_method": "General waste bin",
                "environmental_impact": "Varies by material type.",
                "recycling_tips": "Check local guidelines for specific items",
                "color_code": "#95A5A6",
                "preparation_steps": [
                    "Check local recycling guidelines",
                    "Consider if item can be reused",
                    "Separate any recyclable components",
                    "Dispose according to local rules"
                ]
            }
        }
        
        return category_data.get(category, category_data["other"])
    
    def analyze_image_quality(self, image_path: str) -> Dict:
        """Analyze image quality for better detection"""
        try:
            image = cv2.imread(image_path)
            
            # Calculate blur score
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast
            contrast = gray.std()
            
            quality_score = min(100, (blur_score / 100 + brightness / 255 + contrast / 128) * 33.33)
            
            return {
                "blur_score": float(blur_score),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "quality_score": float(quality_score),
                "recommendations": self._get_quality_recommendations(blur_score, brightness, contrast)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image quality: {e}")
            return {
                "blur_score": 0,
                "brightness": 0,
                "contrast": 0,
                "quality_score": 0,
                "recommendations": ["Unable to analyze image quality"]
            }
    
    def _get_quality_recommendations(self, blur: float, brightness: float, contrast: float) -> List[str]:
        """Get recommendations for improving image quality"""
        recommendations = []
        
        if blur < 100:
            recommendations.append("Image appears blurry. Hold camera steady and focus on the object.")
        
        if brightness < 50:
            recommendations.append("Image is too dark. Try better lighting or move closer to a light source.")
        elif brightness > 200:
            recommendations.append("Image is too bright. Reduce lighting or move away from direct light.")
        
        if contrast < 30:
            recommendations.append("Low contrast detected. Ensure good lighting and clear background.")
        
        if not recommendations:
            recommendations.append("Image quality is good for detection.")
        
        return recommendations

# Global instance
waste_detector = WasteDetectionService()
