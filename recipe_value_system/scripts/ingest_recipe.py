"""Script to ingest a recipe from a URL."""

import logging
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from recipe_value_system.models.base import Base
from recipe_value_system.services.ingestion.recipe_ingestion import (
    RecipeIngestionService,
)
from recipe_value_system.services.scraping.recipe_scraper import SugarSpunRunScraper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleConfig:
    """Simple configuration for local development."""

    def __init__(self):
        self.WEIGHT_UPDATE_THRESHOLD = 0.1
        self.MIN_CONFIDENCE_SCORE = 0.6
        self.CACHE_TTL = 3600
        self.MAX_RECIPES_PER_PAGE = 20


def setup_database(db_path: Path) -> None:
    """Set up SQLite database."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)


def main(url: str) -> Optional[dict]:
    """Ingest a recipe from the given URL."""
    try:
        # Set up database
        db_path = Path("recipes.db")
        setup_database(db_path)

        # Initialize database connection
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()

        # Initialize config
        config = SimpleConfig()

        # Initialize scraper based on domain
        if "sugarspunrun.com" in url:
            scraper = SugarSpunRunScraper()
        else:
            raise ValueError(f"No scraper available for URL: {url}")

        # Scrape recipe
        logger.info(f"Scraping recipe from {url}")
        scraped_recipe = scraper.scrape_recipe(url)

        # Initialize ingestion service
        ingestion_service = RecipeIngestionService(session, config)

        # Ingest recipe
        logger.info(f"Ingesting recipe: {scraped_recipe.title}")
        recipe = ingestion_service.ingest_recipe(scraped_recipe)

        if recipe:
            logger.info(f"Successfully ingested recipe: {recipe.title}")
            logger.info("Recipe details:")
            logger.info(f"- Ingredients: {len(recipe.ingredients)}")
            logger.info(f"- Instructions: {len(recipe.instructions)}")
            logger.info(f"- Prep time: {recipe.prep_time} minutes")
            logger.info(f"- Cook time: {recipe.cook_time} minutes")
            logger.info(f"- Total time: {recipe.total_time} minutes")
            logger.info(f"- Difficulty score: {recipe.difficulty_score:.1f}/5.0")
            logger.info(f"- Complexity score: {recipe.complexity_score:.1f}/5.0")

            return {
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "total_time": recipe.total_time,
                "difficulty_score": recipe.difficulty_score,
                "complexity_score": recipe.complexity_score,
            }
        else:
            logger.error("Failed to ingest recipe")
            return None

    except Exception as e:
        logger.error(f"Error ingesting recipe: {str(e)}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_recipe.py <recipe_url>")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
