"""Recipe signature model for version control."""

from typing import Any, Dict

from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class RecipeSignature(Base, TimestampMixin):
    """Model for tracking recipe versions and changes.

    Stores hash signatures of recipe components to detect and track changes.
    Used for version control and change detection.

    Attributes:
        id: Unique identifier
        recipe_id: Associated recipe ID
        ingredients_hash: Hash of ingredients list
        instructions_hash: Hash of instructions
        metadata_hash: Hash of recipe metadata
        version: Version number
        changes: Description of changes
    """

    __tablename__ = "recipe_signatures"

    id: int = Column(Integer, primary_key=True)
    recipe_id: int = Column(
        Integer, ForeignKey("vault_recipes.id", ondelete="CASCADE"), nullable=False
    )
    ingredients_hash: str = Column(String(64), nullable=False)
    instructions_hash: str = Column(String(64), nullable=False)
    metadata_hash: str = Column(String(64), nullable=False)
    version: int = Column(Integer, nullable=False, default=1)
    changes: Dict[str, Any] = Column(JSON)

    # Relationships
    recipe = relationship("Recipe", back_populates="signature")

    def __init__(
        self,
        recipe_id: int,
        ingredients_hash: str,
        instructions_hash: str,
        metadata_hash: str,
        version: int,
        changes: Dict[str, Any],
    ) -> None:
        """Initialize a new recipe signature.

        Args:
            recipe_id: ID of the recipe
            ingredients_hash: Hash of ingredients list
            instructions_hash: Hash of instructions
            metadata_hash: Hash of recipe metadata
            version: Version number
            changes: Description of changes
        """
        self.recipe_id = recipe_id
        self.ingredients_hash = ingredients_hash
        self.instructions_hash = instructions_hash
        self.metadata_hash = metadata_hash
        self.version = version
        self.changes = changes

    def __repr__(self) -> str:
        """Get string representation of the signature.

        Returns:
            String with recipe ID and version.
        """
        return f"<RecipeSignature(recipe_id={self.recipe_id}, version={self.version})>"
