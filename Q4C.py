from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Standard library imports
import json
import xml.etree.ElementTree as ET
from sqlalchemy import Boolean, ARRAY, JSON, UUID
from sqlalchemy.dialects.postgresql import JSONB
from datetime import timedelta
import uuid
import numpy as np
from typing import Dict, List

# Third-party imports
import pandas as pd
import pickle
import yaml
import pyarrow.parquet as pq  # Better than raw parquet import

# Required packages:
# pandas>=1.5.0
# PyYAML>=6.0
# pyarrow>=12.0.0

## To get the best prompts, Use this structure: 
# Role (What the AI is) 
# Task (What you want it to do)
# Context (What you want it to know going in)
## About the , avatar, goal
## Our system
# Examples
### Example 1  Keep inputs/outputs in mind
### Example 2: etc. 
# Notes

# Optional: Add error handling for critical packages
try:
    import yaml
except ImportError:
    print("PyYAML is required. Please install it using: pip install PyYAML")
    raise

try:
    import pyarrow.parquet as pq
except ImportError:
    print("pyarrow is required. Please install it using: pip install pyarrow")
    raise

Base = declarative_base()

class SubscriptionTier(Enum):
    FREE = "Free"
    BASIC = "Basic"
    PREMIUM = "Premium"
    BUSINESS = "Business"

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    source = Column(String(100))
    ingredients = Column(JSONB)  # Changed to JSONB for better querying
    instructions = Column(JSONB)  # Changed to structured steps
    active_time = Column(Integer)
    passive_time = Column(Integer)
    cost_per_serving = Column(Float)
    health_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New fields
    source_url = Column(String(500))
    source_rating = Column(Float)
    community_rating = Column(Float)
    ai_confidence_score = Column(Float)
    nutrition_info = Column(JSONB)
    tags = Column(ARRAY(String))
    is_published = Column(Boolean, default=False)
    complexity_score = Column(Integer)
    seasonal_score = Column(Float)
    
    # Relationships
    ratings = relationship("UserRating", back_populates="recipe")
    value_metrics = relationship("RecipeValueMetrics", back_populates="recipe")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New fields
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_start = Column(DateTime)
    feedback_points = Column(Integer, default=0)
    dietary_restrictions = Column(ARRAY(String))
    preferred_cuisines = Column(ARRAY(String))
    cooking_skill_level = Column(Integer)
    household_size = Column(Integer)
    budget_preference = Column(String(20))
    last_active_at = Column(DateTime)
    preference_weights = Column(JSONB)
    
    # Relationships
    ratings = relationship("UserRating", back_populates="user")
    cooking_history = relationship("CookingHistory", back_populates="user")
    rewards = relationship("UserRewards", back_populates="user")

# New Models
class RecipeValueMetrics(Base):
    __tablename__ = 'recipe_value_metrics'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    health_score = Column(Float)
    cost_efficiency_score = Column(Float)
    time_efficiency_score = Column(Float)
    taste_score = Column(Float)
    complexity_match_score = Column(Float)
    dietary_match_score = Column(Float)
    seasonal_relevance_score = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    recipe = relationship("Recipe", back_populates="value_metrics")

class CookingHistory(Base):
    __tablename__ = 'cooking_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    cooked_at = Column(DateTime, default=datetime.utcnow)
    modifications = Column(JSONB)
    success_rating = Column(Integer)
    notes = Column(String(500))
    
    user = relationship("User", back_populates="cooking_history")

class UserRewards(Base):
    __tablename__ = 'user_rewards'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    points_earned = Column(Integer)
    monetary_value = Column(Float)
    earned_at = Column(DateTime, default=datetime.utcnow)
    applied_to_subscription = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="rewards")

class BusinessClient(Base):
    __tablename__ = 'business_clients'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(255))
    api_key = Column(UUID, default=uuid.uuid4)
    subscription_tier = Column(String(20))
    preferred_export_format = Column(String(50))
    integration_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# Recipe Value Calculator
class RecipeValueCalculator:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.weights = self._load_user_weights()
        self.user = self._get_user_profile()  # Get user's skill level, preferences, etc.
    
    def calculate_recipe_value(self, recipe_id: int) -> float:
        """
        Recipe Value = (Taste * Risk) / (Time + Effort + Sacrifice)
        
        Where:
        Taste = weighted combination of taste factors
        Risk = probability of success based on user's skill and recipe difficulty
        Time = weighted combination of active and passive time
        Effort = complexity factors like dish count and technique difficulty
        Sacrifice = monetary and health costs
        """
        recipe = self._get_recipe(recipe_id)
        metrics = self._get_recipe_metrics(recipe_id)
        
        # Calculate Taste Component
        taste_score = self._calculate_taste_score(
            user_ratings=metrics['user_ratings'],
            source_rating=recipe.source_rating,
            health_score=recipe.health_score,
            community_rating=recipe.community_rating,
            weight_taste=self.weights['taste_importance'],
            weight_health=self.weights['health_importance']
        )
        
        # Calculate Risk Component
        risk_score = self._calculate_risk_score(
            recipe_difficulty=recipe.complexity_score,
            user_skill=self.user.cooking_skill_level,
            similar_recipe_success=self._get_similar_recipe_success_rate(),
            recipe_confidence=recipe.ai_confidence_score
        )
        
        # Calculate Time Component
        time_score = self._calculate_time_score(
            active_time=recipe.active_time,
            passive_time=recipe.passive_time,
            weight_active=self.weights['active_time_weight'],
            weight_passive=self.weights['passive_time_weight']
        )
        
        # Calculate Effort Component
        effort_score = self._calculate_effort_score(
            dish_count=metrics['dish_count'],
            technique_complexity=recipe.complexity_score,
            prep_complexity=metrics['prep_complexity']
        )
        
        # Calculate Sacrifice Component
        sacrifice_score = self._calculate_sacrifice_score(
            cost_per_serving=recipe.cost_per_serving,
            health_deviation=self._calculate_health_deviation(recipe.nutrition_info),
            budget_preference=self.user.budget_preference
        )
        
        # Final Value Equation
        numerator = taste_score * risk_score
        denominator = time_score + effort_score + sacrifice_score
        
        recipe_value = numerator / max(denominator, 0.1)  # Prevent division by zero
        
        # Store calculation for learning
        self._store_calculation_metrics(
            recipe_id=recipe_id,
            taste_score=taste_score,
            risk_score=risk_score,
            time_score=time_score,
            effort_score=effort_score,
            sacrifice_score=sacrifice_score,
            final_value=recipe_value
        )
        
        return recipe_value

    def _calculate_taste_score(self, **kwargs) -> float:
        """
        Weighted combination of taste factors including:
        - Previous user ratings
        - Source website rating
        - Health score
        - Community rating
        """
        return (
            kwargs['user_ratings'] * kwargs['weight_taste'] +
            kwargs['source_rating'] * 0.2 +
            kwargs['health_score'] * kwargs['weight_health'] +
            kwargs['community_rating'] * 0.3
        )

    def _calculate_risk_score(self, **kwargs) -> float:
        """
        Calculate probability of recipe success based on:
        - Recipe difficulty vs user skill level
        - Success rate with similar recipes
        - AI confidence in recipe match
        """
        skill_match = 1 - (abs(kwargs['recipe_difficulty'] - kwargs['user_skill']) / 5)
        return (
            skill_match * 0.4 +
            kwargs['similar_recipe_success'] * 0.4 +
            kwargs['recipe_confidence'] * 0.2
        )

    def _calculate_time_score(self, **kwargs) -> float:
        """
        Weighted time score giving more weight to active time
        """
        return (
            kwargs['active_time'] * kwargs['weight_active'] +
            kwargs['passive_time'] * kwargs['weight_passive']
        )

    def _calculate_effort_score(self, **kwargs) -> float:
        """
        Effort score based on:
        - Number of dishes/utensils required
        - Technique complexity
        - Preparation complexity
        """
        return (
            kwargs['dish_count'] * 0.3 +
            kwargs['technique_complexity'] * 0.4 +
            kwargs['prep_complexity'] * 0.3
        )

    def _calculate_sacrifice_score(self, **kwargs) -> float:
        """
        Sacrifice score based on:
        - Cost per serving relative to user's budget preference
        - Deviation from preferred health metrics
        """
        cost_factor = kwargs['cost_per_serving'] / kwargs['budget_preference']
        return cost_factor + kwargs['health_deviation']

    def update_weights_from_feedback(self, recipe_id: int, user_feedback: dict):
        """
        Update weight coefficients based on user feedback using gradient descent
        """
        current_value = self.calculate_recipe_value(recipe_id)
        target_value = user_feedback['overall_satisfaction']
        learning_rate = 0.01

        # Update weights based on the difference
        error = target_value - current_value
        for weight_name, weight_value in self.weights.items():
            gradient = self._calculate_weight_gradient(weight_name, error)
            self.weights[weight_name] += learning_rate * gradient

        self._save_weights()

    def _store_calculation_metrics(self, **kwargs):
        """
        Store calculation components for machine learning and optimization
        """
        # Store in database for later analysis and weight optimization
        pass

# Data Export Handler
class DataExporter:
    @staticmethod
    def export_data(format_type: str, data: Dict) -> bytes:
        if format_type == 'parquet':
            return DataExporter._to_parquet(data)
        elif format_type == 'json':
            return json.dumps(data).encode()
        elif format_type == 'yaml':
            return yaml.dump(data).encode()
        elif format_type == 'xml':
            return DataExporter._to_xml(data)
        raise ValueError(f"Unsupported format: {format_type}")

    @staticmethod
    def _to_parquet(data: Dict) -> bytes:
        df = pd.DataFrame(data)
        return df.to_parquet()

    @staticmethod
    def _to_xml(data: Dict) -> bytes:
        root = ET.Element('data')
        # ... XML conversion logic ...
        return ET.tostring(root)

class TasteRating(Enum):
    HATE = "Hate - I would never eat this again, even if paid"
    DONT_LIKE = "Don't Like - I'd rather eat something else, but could tolerate it"
    MEH = "Meh - It's edible but nothing special"
    LIKE = "Like - I enjoy this and would eat it again" 
    LOVE = "Love - This is delicious and I look forward to having it"
    CRAVE = "Crave - I can't stop thinking about this dish and need to have it again"

class RiskLevel(Enum):
    NONE = "No Risk - Highly rated recipe with positive reviews and similar to recipes you enjoy"
    LOW = "Low Risk - Well-reviewed recipe with some similarity to your preferences"
    MEDIUM = "Medium Risk - Mixed reviews or uncertain match to your taste profile"
    HIGH = "High Risk - Poor reviews or significantly different from your preferred recipes"
    EXTREME = "Extreme Risk - Negative reviews and very different from your typical choices"

class DifficultyLevel(Enum):
    BEGINNER = "Beginner - Basic kitchen skills, simple tools (microwave, toaster)"
    EASY = "Easy - Basic techniques, common kitchen tools (pots, pans, measuring cups)"
    INTERMEDIATE = "Intermediate - Multiple techniques, specialized tools (food processor, mixer)"
    ADVANCED = "Advanced - Complex techniques, precise timing, professional tools (mandoline, thermometer)"
    EXPERT = "Expert - Professional techniques, specialized equipment (sous vide, blast chiller)"

class DishCount(Enum):
    MINIMAL = "Minimal - 1-2 dishes (one pot/pan)"
    LIGHT = "Light - 3-4 dishes (pot, pan, cutting board)"
    MODERATE = "Moderate - 5-7 dishes (multiple pots/pans, bowls)"
    HEAVY = "Heavy - 8-10 dishes (full sink load)"
    EXTENSIVE = "Extensive - 11+ dishes (multiple sink loads)"

class HealthLevel(Enum):
    TREAT = "Treat - Meant to be enjoyed in moderation"
    COMFORT = "Comfort - Focus on satisfaction rather than nutrition"
    BALANCED = "Balanced - Mix of nutrition and enjoyment"
    NOURISHING = "Nourishing - Emphasis on whole, nutrient-rich ingredients"
    WHOLESOME = "Wholesome - Optimized for both nutrition and satisfaction"

class TimeCommitment(Enum):
    QUICK = "Quick - Under 5 minutes per serving"
    SHORT = "Short - 5-10 minutes per serving"
    MEDIUM = "Medium - 10-20 minutes per serving" 
    LONG = "Long - 20-40 minutes per serving"
    EXTENDED = "Extended - Over 40 minutes per serving"

class CostLevel(Enum):
    BUDGET = "Budget - Under $2 per serving"
    ECONOMICAL = "Economical - $2-5 per serving"
    MODERATE = "Moderate - $5-10 per serving"
    EXPENSIVE = "Expensive - $10-20 per serving"
    LUXURY = "Luxury - Over $20 per serving"

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    source = Column(String(100))  # Either 'web_scraper' or 'user_submission'
    ingredients = Column(String(2000))
    instructions = Column(String(5000))
    active_time = Column(Integer)  # in minutes
    passive_time = Column(Integer)  # in minutes
    cost_per_serving = Column(Float)
    health_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = relationship("UserRating", back_populates="recipe")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = relationship("UserRating", back_populates="user")

class UserRating(Base):
    __tablename__ = 'user_ratings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    taste_rating = Column(SQLEnum(TasteRating))
    risk_rating = Column(SQLEnum(RiskLevel))
    difficulty_rating = Column(SQLEnum(DifficultyLevel))
    time_accuracy = Column(Float)  # percentage of how accurate the recipe time estimates were
    notes = Column(String(500))
    rated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    recipe = relationship("Recipe", back_populates="ratings")

# 