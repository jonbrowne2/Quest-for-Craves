"""Script for storing recipe data in a simple format."""

from datetime import datetime
from typing import Dict, List, Optional, Union

import numpy as np
from numpy.typing import NDArray
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..models.recipe import Recipe, RecipeIngredient, RecipeStep
from ..services.data_export import DataExporter
from ..value.recipe_value import RecipeValueCalculator


def create_recipe(
    title: str,
    ingredients: List[Dict[str, Union[str, float]]],
    instructions: List[str],
    description: Optional[str] = None,
    prep_time: Optional[int] = None,
    cook_time: Optional[int] = None,
) -> Recipe:
    """Create a new recipe with the given parameters.

    Args:
        title: Recipe title
        ingredients: List of ingredient dictionaries
        instructions: List of instruction steps
        description: Optional recipe description
        prep_time: Optional preparation time in minutes
        cook_time: Optional cooking time in minutes

    Returns:
        New Recipe instance
    """
    recipe = Recipe(
        title=title,
        description=description or "",
        prep_time=prep_time or 0,
        cook_time=cook_time or 0,
        created_at=datetime.now(),
        modified_at=datetime.now(),
    )

    # Add ingredients
    for ingredient_data in ingredients:
        ingredient = RecipeIngredient(
            name=str(ingredient_data.get("name", "")),
            amount=float(ingredient_data.get("amount", 0.0)),
            unit=str(ingredient_data.get("unit", "")),
            notes=str(ingredient_data.get("notes", "")),
        )
        recipe.ingredients.append(ingredient)

    # Add instructions
    for step_number, instruction in enumerate(instructions, 1):
        step = RecipeStep(
            step_number=step_number,
            instruction=instruction,
        )
        recipe.steps.append(step)

    return recipe


def store_recipe(recipe: Recipe, session: Session) -> None:
    """Store a recipe in the database.

    Args:
        recipe: Recipe to store
        session: Database session
    """
    try:
        session.add(recipe)
        session.commit()
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Failed to store recipe: {e}") from e


def main() -> None:
    """Main function for storing a sample recipe."""
    # Create database engine and session
    engine = create_engine("sqlite:///recipes.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Sample recipe data
        ingredients = [
            {"name": "Flour", "amount": 2.0, "unit": "cups"},
            {"name": "Sugar", "amount": 1.0, "unit": "cup"},
            {"name": "Eggs", "amount": 2.0, "unit": ""},
            {"name": "Milk", "amount": 1.0, "unit": "cup"},
            {"name": "Vanilla Extract", "amount": 1.0, "unit": "tsp"},
        ]

        instructions = [
            "Preheat oven to 350°F (175°C)",
            "Mix dry ingredients in a large bowl",
            "Beat eggs and milk in a separate bowl",
            "Combine wet and dry ingredients",
            "Pour into a greased baking pan",
            "Bake for 30-35 minutes",
        ]

        # Create and store recipe
        recipe = create_recipe(
            title="Simple Cake",
            ingredients=ingredients,
            instructions=instructions,
            description="A simple and delicious cake recipe",
            prep_time=15,
            cook_time=35,
        )

        store_recipe(recipe, session)
        print("Recipe stored successfully!")

        # Export recipe data
        exporter = DataExporter(session)
        export_data: NDArray[np.float64] = exporter.export_recipe_data(recipe.id)
        print("Recipe data exported successfully!")
        print(f"Export data shape: {export_data.shape}")

        # Calculate recipe value
        calculator = RecipeValueCalculator(session)
        value = calculator.calculate_value(recipe.id)
        print(f"Recipe value: {value:.2f}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
