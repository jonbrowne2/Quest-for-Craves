"""Recipe title model module.

This module defines the RecipeTitle model and related functionality.
"""

from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from models.base import Base


class RecipeTitle(Base):
    """Recipe title model class.

    This class represents a recipe title in the system, including its
    normalized form and search-friendly variations.
    """

    __tablename__ = "recipe_titles"

    id = Column(Integer, primary_key=True)
    original: Mapped[str] = Column(String(255), nullable=False)
    normalized: Mapped[str] = Column(String(255), nullable=False)
    search_key: Mapped[str] = Column(String(255), nullable=False, index=True)
    variations: Mapped[Optional[str]] = Column(String(1000))

    # Relationships
    recipes = relationship(
        "Recipe",
        back_populates="title",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Get string representation of RecipeTitle.

        Returns:
            String representation
        """
        return f"<RecipeTitle(id={self.id}, original='{self.original}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert RecipeTitle to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "original": self.original,
            "normalized": self.normalized,
            "search_key": self.search_key,
            "variations": self.variations,
        }
