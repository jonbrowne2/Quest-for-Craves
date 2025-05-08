import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List

from services.scraping.recipe_quality import Recipe, RecipeQualityAnalyzer
from services.scraping.recipe_scraper import EliteRecipeScraper


def parse_ingredients(ingredients_text: str) -> List[Dict[str, Any]]:
    """Parse ingredients from text into structured format."""
    ingredients = []
    for line in ingredients_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        # Try to extract amount, unit, and name
        # Common units pattern
        units = r"(?:g|kg|ml|l|cup|tbsp|tsp|tablespoon|teaspoon|oz|pound|lb|piece|slice|pinch)"
        # Match pattern: amount + unit + name
        match = re.match(
            r"^([\d./]+(?:\s*-\s*[\d./]+)?)\s*(" + units + r"s?\b)\s*(.+)$", line, re.I
        )

        if match:
            amount, unit, name = match.groups()
            ingredients.append(
                {
                    "text": line,
                    "amount": amount,
                    "unit": unit.lower(),
                    "name": name.strip(),
                }
            )
        else:
            # If no match, store as is
            ingredients.append(
                {"text": line, "amount": None, "unit": None, "name": line}
            )

    return ingredients


def parse_instructions(instructions_text: str) -> List[Dict[str, Any]]:
    """Parse instructions from text into structured format."""
    instructions = []

    # Split into paragraphs
    paragraphs = instructions_text.strip().split("\n\n")

    for para in paragraphs:
        if not para.strip():
            continue

        # Split long paragraphs into sentences
        if len(para) > 200:
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                if sentence.strip():
                    instructions.append({"text": sentence.strip()})
        else:
            instructions.append({"text": para.strip()})

    return instructions


def scrape_and_save(source, is_url=True):
    scraper = EliteRecipeScraper()
    quality_analyzer = RecipeQualityAnalyzer()

    if is_url:
        recipe = scraper._scrape_from_url(source)
    else:
        # Parse recipe from text
        parts = source.split("\n\n")

        # First part contains title and possibly yield
        title_parts = parts[0].strip().split("\n")
        title = title_parts[0].strip()
        yields = title_parts[1].strip() if len(title_parts) > 1 else None

        # Find ingredients section (list of short lines)
        ingredients_text = ""
        instructions_text = ""

        # Skip title/yield section
        for part in parts[1:]:
            lines = part.strip().split("\n")
            # If most lines are short, it's probably ingredients
            if all(len(line.strip()) < 100 for line in lines) and not ingredients_text:
                ingredients_text = part
            else:
                if instructions_text:
                    instructions_text += "\n\n"
                instructions_text += part

        # Create recipe object
        recipe = Recipe(
            title=title,
            source_text=source,
            ingredients=parse_ingredients(ingredients_text),
            instructions=parse_instructions(instructions_text.strip()),
            yields={"text": yields} if yields else None,
        )

    if recipe:
        # Create filename from recipe title
        filename = recipe.title.lower().replace(" ", "_").replace("-", "_") + ".json"
        # Remove any non-alphanumeric characters except underscores
        filename = re.sub(r"[^a-z0-9_]", "", filename)
        filepath = os.path.join("vault", "recipes", filename)

        # Ensure directory exists
        os.makedirs(os.path.join("vault", "recipes"), exist_ok=True)

        # Get quality metrics
        quality_metrics = quality_analyzer.analyze_recipe(recipe)

        # Convert recipe to dict
        recipe_dict = {
            "title": recipe.title,
            "yields": recipe.yields,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "source_url": source if is_url else None,
            "source_text": None if is_url else source,
            "quality_metrics": {
                "overall_quality": quality_metrics.overall_quality,
                "completeness_score": quality_metrics.completeness_score,
                "instruction_clarity": quality_metrics.instruction_clarity,
                "ingredient_validity": quality_metrics.ingredient_validity,
                "timing_validity": quality_metrics.timing_validity,
                "temperature_validity": quality_metrics.temperature_validity,
                "portion_consistency": quality_metrics.portion_consistency,
                "needs_improvement": not quality_metrics.is_high_quality,
            },
        }

        # Save recipe
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(recipe_dict, f, indent=2, ensure_ascii=False)
        print(f"Saved recipe to {filepath}")
        print("Recipe contents:")
        print(json.dumps(recipe_dict, indent=2, ensure_ascii=False))

        if recipe_dict["quality_metrics"]["needs_improvement"]:
            print("\nNote: This recipe needs improvement in the following areas:")
            if quality_metrics.instruction_clarity < 0.6:
                print("- Instruction clarity")
            if quality_metrics.completeness_score < 0.7:
                print("- Recipe completeness")
            if quality_metrics.ingredient_validity < 0.6:
                print("- Ingredient details")
    else:
        print("Failed to scrape recipe")


# Test recipe text
recipe_text = """Brownie Crinkle Cookies
Makes 10

200g dark chocolate (around 65-70% cocoa solids), finely chopped
125g unsalted butter, diced
150g caster sugar
100g light brown sugar
2 large eggs
130g plain flour
3 tbsp cocoa powder (dutch processed)
1 tsp baking powder
1/4 tsp salt (plus flaked sea salt for sprinkling)

Temperature and timing is very important with this recipe so before you start get all the ingredients weighed out, two baking trays lined with parchment paper and the oven preheated to 180C (160C fan) 350F.

Place the butter and chocolate into a heatproof bowl and set over a pan and gently simmering water. Allow to melt, stirring occasionally until fully melted. Remove the bowl from the heat and set aside for the moment. In the bowl of a stand mixer fitted with the whisk attachment, or using an electric hand mixer, whisk together the eggs and sugars, on medium-high speed, for exactly 5 minutes. Once the eggs have been mixing for exactly 5 minutes pour in the chocolate mixture and mix for a minute or so to combine. Meanwhile mix together the dry ingredients, sieving the cocoa powder if it has lots of lumps. Add the dry ingredients and mix very briefly just until combined. Use your spatula to give one last mix, scraping the bottom of the bowl to make sure everything is evenly combined. Use a ice cream scoop to form the cookies. The batter will be a little on the wet side, so invert the cookie scoop just above the baking tray to avoid spills. Make sure to leave plenty of space between each cookie as they will spread. Sprinkle each cookie with a little flaked sea salt before placing into the oven and baking for 12 minutes. The cookies will come out of the oven with that wonderful crinkled look and slightly domed. They will collapse a little as they cool but this helps form that perfect fudgy centre. The cookies will be very soft so allow them to cool on the baking trays for at least 20-30 minutes before removing from the tray to cool completley.

These cookies will keep for 4-5 days but will be best within the first 3 days."""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # URL provided as argument
        url = sys.argv[1]
        scrape_and_save(url, is_url=True)
    else:
        # Use test recipe text
        scrape_and_save(recipe_text, is_url=False)
