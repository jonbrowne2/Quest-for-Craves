"""
Instruction parsing module for the recipe value system.

This module provides utilities for parsing and standardizing recipe instructions.
"""

import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag


class InstructionParser:
    """Parser for extracting and normalizing recipe instructions."""

    @staticmethod
    def extract_from_html(soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract cooking instructions from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of instruction dictionaries
        """
        instruction_selectors = [
            ".recipe-instructions li",
            ".instructions li",
            '[itemprop="recipeInstructions"]',
            ".instruction-list li",
            ".instruction",
            "#instructions li",
            ".steps li",
            ".recipe-method li",
            ".recipe-steps li",
            "[data-instruction]",
        ]

        instructions = []

        # Try specific instruction selectors
        for selector in instruction_selectors:
            elements = soup.select(selector)
            if elements:
                for i, element in enumerate(elements):
                    text = InstructionParser.extract_text_content(element)
                    if text and len(text) > 5:  # Avoid very short instructions
                        instructions.append({"text": text, "position": i + 1})
                return instructions

        # Fallback to JSON-LD data
        script_tags = soup.find_all("script", {"type": "application/ld+json"})
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if data.get("@type") == "Recipe" and "recipeInstructions" in data:
                    instructions_data = data["recipeInstructions"]
                    if isinstance(instructions_data, list):
                        return [
                            {
                                "text": InstructionParser.extract_instruction_text(
                                    item
                                ),
                                "position": i + 1,
                            }
                            for i, item in enumerate(instructions_data)
                        ]
            except (json.JSONDecodeError, AttributeError):
                continue

        return instructions

    @staticmethod
    def extract_text_content(element: Tag) -> str:
        """
        Extract clean text content from an HTML element.

        Args:
            element: BeautifulSoup Tag

        Returns:
            Cleaned text content
        """
        text = element.get_text(strip=True)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def extract_instruction_text(instruction: Any) -> str:
        """
        Extract instruction text from various formats.

        Args:
            instruction: Instruction data (string or dict)

        Returns:
            Instruction text
        """
        if isinstance(instruction, str):
            return instruction
        elif isinstance(instruction, dict):
            return instruction.get("text", "")
        return ""
