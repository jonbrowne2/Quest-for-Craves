"""Category model for recipe classification."""

from enum import Enum
from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from recipe_value_system.models.base import Base


class CategoryType(str, Enum):
    """Types of recipe categories.

    Attributes:
        CUISINE: Cuisine type categories (e.g., Italian, Mexican)
        DIET: Dietary categories (e.g., Vegetarian, Keto)
        MEAL: Meal type categories (e.g., Breakfast, Dinner)
        COURSE: Course categories (e.g., Appetizer, Dessert)
        INGREDIENT: Main ingredient categories (e.g., Chicken, Pasta)
        COOKING_METHOD: Cooking method categories (e.g., Grilled, Baked)
        OTHER: Other miscellaneous categories
    """

    CUISINE = "cuisine"
    DIET = "diet"
    MEAL = "meal"
    COURSE = "course"
    INGREDIENT = "ingredient"
    COOKING_METHOD = "cooking_method"
    OTHER = "other"


class Category(Base):
    """Model for recipe categories.

    This model represents a category that can be assigned to recipes for
    classification and organization purposes.

    Attributes:
        id: Unique identifier for the category
        name: Category name
        type: Type of category (cuisine, diet, etc.)
        description: Optional category description
        parent_id: ID of parent category if this is a subcategory
        children: List of child categories
        parent: Parent category if this is a subcategory
    """

    __tablename__ = "categories"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), nullable=False)
    type: CategoryType = Column(String(50), nullable=False)
    description: str = Column(String(500))
    parent_id: int = Column(Integer, ForeignKey("categories.id"))

    # Relationships
    children: List["Category"] = relationship(
        "Category",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Get string representation of the category.

        Returns:
            String representation including name and type.
        """
        return f"<Category(name={self.name}, type={self.type})>"
