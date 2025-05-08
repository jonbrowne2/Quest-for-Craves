"""Tests for data export functionality."""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

from recipe_value_system.models.recipe import CuisineType, Recipe
from recipe_value_system.models.user_interactions import (
    InteractionType,
    UserRecipeInteraction,
)
from recipe_value_system.services.export.data_exporter import DataExporter


@pytest.fixture
def sample_recipe(db_session):
    """Create a sample recipe for testing."""
    recipe = Recipe(
        title="Test Recipe",
        slug="test-recipe",
        cuisine_type=CuisineType.ITALIAN,
        ingredients=[
            {"amount": 1, "unit": "cup", "name": "flour"},
            {"amount": 2, "unit": "tbsp", "name": "sugar"},
        ],
        instructions=[
            {"step": 1, "text": "Mix ingredients"},
            {"step": 2, "text": "Bake at 350F"},
        ],
        prep_time=15,
        cook_time=30,
        total_time=45,
        serving_size=4,
        calories_per_serving=300,
        difficulty_score=2.5,
        community_rating=4.5,
        review_count=10,
    )
    db_session.add(recipe)
    db_session.commit()
    return recipe


@pytest.fixture
def sample_interaction(db_session, sample_recipe):
    """Create a sample user interaction for testing."""
    interaction = UserRecipeInteraction(
        user_id=1,
        recipe_id=sample_recipe.id,
        interaction_type=InteractionType.COOKED,
        rating=4.5,
        cooking_time_actual=40,
        taste_rating=4.0,
        would_cook_again=True,
        notes="Great recipe!",
    )
    db_session.add(interaction)
    db_session.commit()
    return interaction


@pytest.fixture
def export_dir(tmp_path):
    """Create temporary export directory."""
    return tmp_path / "exports"


def test_export_recipes(db_session, sample_recipe, export_dir):
    """Test exporting recipes in all formats."""
    exporter = DataExporter(db_session, export_dir)
    paths = exporter.export_recipes()

    # Check CSV export
    df = pd.read_csv(paths["csv"])
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Test Recipe"

    # Check JSON export
    with open(paths["json"]) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["title"] == "Test Recipe"

    # Check Parquet export
    table = pq.read_table(paths["parquet"])
    df = table.to_pandas()
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Test Recipe"

    # Check Excel export
    df = pd.read_excel(paths["excel"])
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Test Recipe"

    # Check Pickle export
    with open(paths["pickle"], "rb") as f:
        data = pickle.load(f)
    assert len(data) == 1
    assert data[0]["title"] == "Test Recipe"


def test_export_recipes_with_filters(db_session, sample_recipe, export_dir):
    """Test exporting recipes with filters."""
    exporter = DataExporter(db_session, export_dir)

    # Test cuisine filter
    paths = exporter.export_recipes({"cuisine_type": CuisineType.ITALIAN})
    with open(paths["json"]) as f:
        data = json.load(f)
    assert len(data) == 1

    # Test rating filter
    paths = exporter.export_recipes({"community_rating": 4.0})
    with open(paths["json"]) as f:
        data = json.load(f)
    assert len(data) == 1

    # Test non-matching filter
    paths = exporter.export_recipes({"community_rating": 5.0})
    with open(paths["json"]) as f:
        data = json.load(f)
    assert len(data) == 0


def test_export_interactions(db_session, sample_interaction, export_dir):
    """Test exporting user interactions."""
    exporter = DataExporter(db_session, export_dir)

    # Test date range filter
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow() + timedelta(days=1)

    paths = exporter.export_user_interactions(start_date, end_date)

    # Check JSON export
    with open(paths["json"]) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["rating"] == 4.5
    assert data[0]["would_cook_again"] is True


def test_excel_formatting(db_session, sample_recipe, export_dir):
    """Test Excel export formatting."""
    exporter = DataExporter(db_session, export_dir)
    paths = exporter.export_recipes()

    # Load workbook
    wb = pd.ExcelFile(paths["excel"])

    # Check sheets
    assert "recipes" in wb.sheet_names
    assert "Summary" in wb.sheet_names

    # Check data
    df = pd.read_excel(paths["excel"], sheet_name="recipes")
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Test Recipe"

    # Check summary
    summary = pd.read_excel(paths["excel"], sheet_name="Summary")
    assert len(summary) == 4  # Total rows, columns, export date, file path
