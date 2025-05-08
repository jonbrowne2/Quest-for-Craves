"""Recipe review model for managing user feedback and ratings."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from .recipe import Recipe


class RecipeReview(Base, TimestampMixin, SoftDeleteMixin):
    """Model for managing recipe reviews and ratings.

    This model stores user feedback about recipes, including:
    - Overall rating
    - Detailed ratings for taste, health, effort
    - Text review and comments
    - Review helpfulness votes
    - Review status (published, flagged, etc.)

    Attributes:
        id (int): Primary key for the review.
        recipe_id (int): Foreign key to the reviewed recipe.
        user_id (int): ID of the user who wrote the review.
        rating (float): Overall rating from 1 to 5.
        title (str): Optional review title.
        content (str): Optional review content.
        helpful_votes (int): Number of users who found this review helpful.
        recipe (Recipe): Relationship to the reviewed Recipe.
    """

    __tablename__ = "recipe_reviews"

    id: Mapped[int] = Column(Integer, primary_key=True)
    recipe_id: Mapped[int] = Column(
        Integer, ForeignKey("vault_recipes.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = Column(Integer, nullable=False)
    rating: Mapped[float] = Column(Float, nullable=False)
    title: Mapped[Optional[str]] = Column(String(200))
    content: Mapped[Optional[str]] = Column(Text)
    helpful_votes: Mapped[int] = Column(Integer, default=0)

    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="reviews")

    def __repr__(self) -> str:
        """Return string representation of the recipe review.

        Returns:
            str: String representation including ID, recipe ID, and rating.
        """
        return (
            f"<RecipeReview(id={self.id}, recipe_id={self.recipe_id}, "
            f"rating={self.rating})>"
        )
