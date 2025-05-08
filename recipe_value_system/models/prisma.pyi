"""Type stubs for Prisma database models."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

class Prisma:
    """Prisma database client."""

    def __init__(self) -> None:
        """Initialize Prisma client."""
        ...
    async def connect(self) -> None:
        """Connect to the database."""
        ...
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        ...
    async def rollback(self) -> None:
        """Rollback current transaction."""
        ...

    class Recipe:
        """Recipe model operations."""

        async def find_many(
            self,
            where: Optional[Dict[str, Any]] = None,
            order_by: Optional[Dict[str, str]] = None,
            skip: Optional[int] = None,
            take: Optional[int] = None,
        ) -> List[Dict[str, Any]]:
            """Find multiple recipes matching criteria."""
            ...
        async def find_first(
            self, where: Optional[Dict[str, Any]] = None
        ) -> Optional[Dict[str, Any]]:
            """Find first recipe matching criteria."""
            ...
        async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new recipe."""
            ...
        async def update(
            self, where: Dict[str, Any], data: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Update an existing recipe."""
            ...
        async def delete(self, where: Dict[str, Any]) -> Dict[str, Any]:
            """Delete a recipe."""
            ...
        async def count(self, where: Optional[Dict[str, Any]] = None) -> int:
            """Count recipes matching criteria."""
            ...

    class Interaction:
        """User interaction model operations."""

        async def find_many(
            self,
            where: Optional[Dict[str, Any]] = None,
            order_by: Optional[Dict[str, str]] = None,
        ) -> List[Dict[str, Any]]:
            """Find multiple interactions matching criteria."""
            ...
        async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new interaction."""
            ...

    class RecipeReview:
        """Recipe review model operations."""

        async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new recipe review."""
            ...

    class RestaurantReview:
        """Restaurant review model operations."""

        async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new restaurant review."""
            ...
    recipe: Recipe
    interaction: Interaction
    recipe_review: RecipeReview
    restaurant_review: RestaurantReview
