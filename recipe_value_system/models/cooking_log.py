"""Cooking log model module.

This module defines the CookingLog model for tracking recipe cooking sessions.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from models.recipe import Recipe

from .base import Base
from .user import User


class CookingLog(Base):
    """Model for tracking recipe cooking sessions.

    This model stores information about each cooking session, including:
    - User who cooked the recipe
    - Recipe being cooked
    - Start and completion times
    - Duration of the cooking session
    - User notes about the cooking session

    Attributes:
        id (int): Unique identifier for the cooking log.
        user_id (int): Foreign key referencing the User model.
        recipe_id (int): Foreign key referencing the Recipe model.
        started_at (datetime): Timestamp when the cooking session started.
        completed_at (datetime): Timestamp when the cooking session completed.
        duration (float): Duration of the cooking session in minutes.
        notes (str): User notes about the cooking session.
    """

    __tablename__ = "cooking_logs"

    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id: Mapped[int] = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    started_at: Mapped[datetime] = Column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime)
    duration: Mapped[Optional[float]] = Column(Float)
    notes: Mapped[Optional[str]] = Column(String(1000))

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="cooking_logs")
    recipe: Mapped[Recipe] = relationship("Recipe", back_populates="cooking_logs")

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of the cooking log
        """
        return (
            f"<CookingLog(id={self.id}, "
            f"user_id={self.user_id}, "
            f"recipe_id={self.recipe_id})>"
        )
