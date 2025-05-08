"""Recipe category assignment model for managing recipe categorization."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .category import RecipeCategory
    from .recipe import Recipe


class RecipeCategoryAssignment(Base, TimestampMixin):
    """Model for managing recipe category assignments.

    This model handles the many-to-many relationship between recipes and categories,
    storing additional metadata such as:
    - Confidence score of the categorization
    - Whether the assignment was manually verified
    - Primary category designation
    """

    __tablename__ = "recipe_category_assignments"

    recipe_id: Mapped[int] = Column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = Column(
        Integer,
        ForeignKey("recipe_categories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    confidence: Mapped[Optional[float]] = Column(Float, nullable=True)
    is_verified: Mapped[bool] = Column(Boolean, default=False)
    is_primary: Mapped[bool] = Column(Boolean, default=False)

    # Relationships
    recipe: Mapped["Recipe"] = relationship(
        "Recipe", back_populates="category_assignments"
    )
    category: Mapped["RecipeCategory"] = relationship(
        "RecipeCategory", back_populates="recipe_assignments"
    )

    def __repr__(self) -> str:
        """Return string representation of the category assignment.

        Returns:
            str: String representation including recipe ID and category ID.
        """
        return (
            f"<RecipeCategoryAssignment(recipe_id={self.recipe_id}, "
            f"category_id={self.category_id})>"
        )
