"""Script to provide feedback on a recipe."""

import logging
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from recipe_value_system.models.base import Base
from recipe_value_system.models.enums import (
    DifficultyLevel,
    InteractionType,
    SkillLevel,
    TasteRating,
)
from recipe_value_system.models.recipes import Recipe
from recipe_value_system.models.user_interactions import UserRecipeInteraction
from recipe_value_system.models.users import User

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Set up SQLite database."""
    engine = create_engine("sqlite:///recipes.db")
    Base.metadata.create_all(engine)
    return engine


def ensure_default_user(session):
    """Ensure default user exists."""
    user = session.query(User).filter_by(username="default").first()
    if not user:
        user = User(
            username="default",
            email="default@example.com",
            display_name="Default User",
            skill_level=SkillLevel.INTERMEDIATE,
        )
        session.add(user)
        session.commit()
    return user


def ensure_default_recipe(session):
    """Ensure default recipe exists."""
    recipe = (
        session.query(Recipe).filter_by(slug="worst-chocolate-chip-cookies").first()
    )
    if not recipe:
        recipe = Recipe(
            title="The WORST Chocolate Chip Cookies",
            slug="worst-chocolate-chip-cookies",
            source_url="https://sugarspunrun.com/worst-chocolate-chip-cookies/",
            author="Sugar Spun Run",
            ingredients=[
                {"item": "unsalted butter", "amount": "1", "unit": "cup"},
                {"item": "brown sugar", "amount": "1", "unit": "cup"},
                {"item": "granulated sugar", "amount": "1/2", "unit": "cup"},
                {"item": "eggs", "amount": "2", "unit": "large"},
                {"item": "vanilla extract", "amount": "1.5", "unit": "teaspoons"},
                {"item": "all-purpose flour", "amount": "2.75", "unit": "cups"},
                {"item": "cornstarch", "amount": "2", "unit": "teaspoons"},
                {"item": "baking soda", "amount": "1", "unit": "teaspoon"},
                {"item": "salt", "amount": "3/4", "unit": "teaspoon"},
                {"item": "chocolate chips", "amount": "2", "unit": "cups"},
            ],
            instructions=[
                "In a large bowl, beat softened butter until creamy.",
                "Add sugars and beat until light and fluffy (about 1 minute).",
                "Add eggs and vanilla extract. Beat until well-combined.",
                "In a separate bowl, whisk together flour, cornstarch, baking soda, and salt.",
                "Gradually add dry ingredients to wet ingredients, mixing until just combined.",
                "Stir in chocolate chips.",
                "Cover and chill dough for at least 30 minutes.",
                "Preheat oven to 350°F (175°C).",
                "Drop rounded 2-3 tablespoon-sized balls onto baking sheet.",
                "Bake for 10-12 minutes until edges are lightly golden brown.",
                "Allow to cool completely on baking sheet.",
            ],
            prep_time=20,
            cook_time=12,
            total_time=62,  # Including 30 min chill time
            serving_size=24,
            difficulty=DifficultyLevel.MODERATE,
        )
        session.add(recipe)
        session.commit()
    return recipe


def provide_feedback(
    recipe_id: int,
    taste_rating: TasteRating,
    cooking_time: int = None,
    difficulty: DifficultyLevel = None,
    notes: str = None,
):
    """Provide feedback for a recipe."""
    try:
        # Set up database
        engine = setup_database()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Ensure default user and recipe exist
        user = ensure_default_user(session)
        recipe = ensure_default_recipe(session)

        # Create interaction
        interaction = UserRecipeInteraction(
            user_id=user.id,
            recipe_id=recipe.id,
            interaction_type=InteractionType.RATE,
            taste_rating=taste_rating,
            cooking_time_actual=cooking_time,
            difficulty_reported=difficulty,
            notes=notes,
        )

        # Add and commit
        session.add(interaction)
        session.commit()

        logger.info(f"Successfully recorded feedback for recipe {recipe.title}")
        logger.info(f"Taste rating: {taste_rating.value}")
        if cooking_time:
            logger.info(f"Cooking time: {cooking_time} minutes")
        if difficulty:
            logger.info(f"Difficulty: {difficulty.value}")
        if notes:
            logger.info(f"Notes: {notes}")

    except Exception as e:
        logger.error(f"Error providing feedback: {str(e)}")
        raise


if __name__ == "__main__":
    # Get taste rating from command line
    if len(sys.argv) < 3:
        print(
            "Usage: python provide_feedback.py <recipe_id> <taste_rating> [cooking_time] [difficulty] [notes]"
        )
        print("\nTaste ratings:")
        for rating in TasteRating:
            print(f"  {rating.value}")
        print("\nDifficulty levels:")
        for level in DifficultyLevel:
            print(f"  {level.value}")
        sys.exit(1)

    recipe_id = int(sys.argv[1])
    taste_rating = TasteRating(sys.argv[2].lower())

    cooking_time = int(sys.argv[3]) if len(sys.argv) > 3 else None
    difficulty = DifficultyLevel(sys.argv[4]) if len(sys.argv) > 4 else None
    notes = sys.argv[5] if len(sys.argv) > 5 else None

    provide_feedback(recipe_id, taste_rating, cooking_time, difficulty, notes)
