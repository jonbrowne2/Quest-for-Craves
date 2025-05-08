import pytest
from sqlalchemy.exc import IntegrityError

from recipe_value_system.models.recipe import CuisineType, DietaryRestriction, Recipe


def test_recipe_creation(db_session):
    """Test basic recipe creation"""
    recipe = Recipe(
        title="Test Recipe",
        slug="test-recipe",
        cuisine_type=CuisineType.ITALIAN,
        ingredients=["ingredient1", "ingredient2"],
        instructions=["step1", "step2"],
        serving_size=4,
    )
    db_session.add(recipe)
    db_session.commit()

    assert recipe.id is not None
    assert recipe.title == "Test Recipe"
    assert recipe.cuisine_type == CuisineType.ITALIAN


def test_recipe_duplicate_slug(db_session):
    """Test that duplicate slugs are not allowed"""
    recipe1 = Recipe(
        title="Recipe 1",
        slug="same-slug",
        ingredients=["ingredient"],
        instructions=["instruction"],
    )
    recipe2 = Recipe(
        title="Recipe 2",
        slug="same-slug",
        ingredients=["ingredient"],
        instructions=["instruction"],
    )

    db_session.add(recipe1)
    db_session.commit()

    db_session.add(recipe2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_recipe_invalid_cuisine_type(db_session):
    """Test that invalid cuisine types are not allowed"""
    with pytest.raises(ValueError):
        Recipe(
            title="Test Recipe",
            slug="test-recipe",
            cuisine_type="INVALID_CUISINE",
            ingredients=["ingredient"],
            instructions=["instruction"],
        )


def test_recipe_dietary_restrictions(db_session):
    """Test adding dietary restrictions to a recipe"""
    recipe = Recipe(
        title="Vegan Pasta",
        slug="vegan-pasta",
        cuisine_type=CuisineType.ITALIAN,
        ingredients=["pasta", "tomatoes", "basil"],
        instructions=["Cook pasta", "Add sauce"],
        dietary_restrictions=[
            DietaryRestriction.VEGAN.value,
            DietaryRestriction.DAIRY_FREE.value,
        ],
    )
    db_session.add(recipe)
    db_session.commit()

    assert DietaryRestriction.VEGAN.value in recipe.dietary_restrictions
    assert DietaryRestriction.DAIRY_FREE.value in recipe.dietary_restrictions
