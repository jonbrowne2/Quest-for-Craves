"""
Site-specific scrapers package initialization.

This package contains specialized scrapers for different recipe websites.
"""

from .allrecipes_scraper import AllRecipesScraper

__all__ = ["AllRecipesScraper"]
