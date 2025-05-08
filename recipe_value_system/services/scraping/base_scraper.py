"""
Base scraper module for the recipe value system.

This module provides the abstract base class that all scrapers must implement,
with common utility methods for web scraping.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .recipe_quality import Recipe, RecipeQualityAnalyzer


class BaseScraper:
    """Base class for recipe scraping with common functionality."""

    def __init__(self) -> None:
        """Initialize the scraper with quality analyzer and session."""
        self.session = self._create_session()
        self.quality_analyzer = RecipeQualityAnalyzer()
        self.logger = logging.getLogger(__name__)

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy."""
        session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def fetch_url(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch content from URL and return BeautifulSoup object.

        Args:
            url: The URL to fetch

        Returns:
            BeautifulSoup object or None if fetch failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            self.logger.error(f"Error fetching URL {url}: {e}")
            return None

    def analyze_recipe_quality(self, recipe: Recipe) -> Dict[str, Any]:
        """
        Analyze recipe quality using the quality analyzer.

        Args:
            recipe: Recipe object to analyze

        Returns:
            Quality metrics dictionary
        """
        return self.quality_analyzer.analyze(recipe)

    def _extract_text_content(self, element: Any) -> str:
        """
        Extract clean text content from an HTML element.

        Args:
            element: BeautifulSoup Tag

        Returns:
            Cleaned text content
        """
        if element is None:
            return ""

        if hasattr(element, "get_text"):
            text = element.get_text(strip=True)
        elif isinstance(element, str):
            text = element
        else:
            return ""

        import re

        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        import re

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
