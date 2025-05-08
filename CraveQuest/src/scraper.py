import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import re
from typing import Optional, List, Dict, Any
import logging
import time

from .models.recipe import Recipe

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def setup_session() -> requests.Session:
    """Create a session with retries for robustness."""
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_page(url: str) -> Optional[str]:
    """Fetch page content with robust error handling."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        session = setup_session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

def parse_time(time_str: str) -> int:
    """Parse ISO 8601 or plain text times (e.g., 'PT1H30M', '1 hour 30 minutes') to minutes."""
    if not time_str:
        return 0
    # ISO 8601 (e.g., PT1H30M)
    if "PT" in time_str:
        minutes = 0
        if "H" in time_str:
            hours = int(re.search(r"(\d+)H", time_str).group(1))
            minutes += hours * 60
        if "M" in time_str:
            mins = int(re.search(r"(\d+)M", time_str).group(1))
            minutes += mins
        return minutes
    # Plain text (e.g., "1 hour 30 minutes")
    hours = re.search(r"(\d+)\s*h(?:our)?", time_str, re.I)
    mins = re.search(r"(\d+)\s*m(?:inute)?", time_str, re.I)
    minutes = 0
    if hours:
        minutes += int(hours.group(1)) * 60
    if mins:
        minutes += int(mins.group(1))
    return minutes or 0

def clean_text(text: str) -> str:
    """Remove ads, extra whitespace, and junk from text."""
    return re.sub(r"\s+", " ", text.strip()).replace("Advertisement", "")

def extract_recipe_data(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract recipe data from JSON-LD object."""
    if isinstance(data, list):
        data = next((item for item in data if item.get("@type") == "Recipe"), None)
    if not data or data.get("@type") != "Recipe":
        return None
    
    return {
        "name": clean_text(data.get("name", "Unknown Recipe")),
        "ingredients": [clean_text(i) for i in data.get("recipeIngredient", [])],
        "steps": [clean_text(step["text"]) if isinstance(step, dict) else clean_text(step)
                 for step in data.get("recipeInstructions", [])],
        "prep_time": parse_time(data.get("prepTime", "")),
        "cook_time": parse_time(data.get("cookTime", "")),
        "servings": data.get("recipeYield", 4)
    }

def scrape_recipe(url: str) -> Optional[Recipe]:
    """Scrape a recipe from a URL with elite precision."""
    html = fetch_page(url)
    if not html:
        logger.error(f"Couldn't fetch {url}")
        return None
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Try JSON-LD (Schema.org/Recipe)
    script_tags = soup.find_all("script", type="application/ld+json")
    for script in script_tags:
        try:
            data = json.loads(script.string)
            recipe_data = extract_recipe_data(data)
            if recipe_data:
                return Recipe(
                    name=recipe_data["name"],
                    ingredients=recipe_data["ingredients"],
                    steps=recipe_data["steps"],
                    prep_time=recipe_data["prep_time"],
                    cook_time=recipe_data["cook_time"],
                    servings=recipe_data["servings"],
                    owner=recipe_data.get("author", "Web Import")  # Use author if available
                )
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse JSON-LD: {e}")
    
    # Fallback to HTML parsing with multiple attempts
    try:
        # Try to find recipe name
        name = None
        name_candidates = [
            soup.find("h1"),  # Most common for recipe titles
            soup.find(class_=re.compile(r"recipe.*title|title.*recipe|entry-title", re.I)),
            soup.find(id=re.compile(r"recipe.*title|title.*recipe", re.I))
        ]
        for candidate in name_candidates:
            if candidate:
                name = clean_text(candidate.text)
                break
        if not name:
            logger.error("Could not find recipe name")
            return None

        # Try to find author
        author = "Web Import"
        author_elements = soup.find_all(text=re.compile(r"author|by", re.I))
        for elem in author_elements:
            parent = elem.parent
            if parent:
                author_text = parent.text
                if "by" in author_text.lower():
                    author = clean_text(author_text.split("by")[-1])
                    break

        # Try to find ingredients
        ingredients = []
        ingredient_lists = soup.find_all(["ul", "ol"], class_=re.compile(r"ingredient", re.I))
        if not ingredient_lists:
            ingredient_lists = soup.find_all(class_=re.compile(r"ingredient", re.I))
        
        for ing_list in ingredient_lists:
            items = ing_list.find_all("li")
            if items:
                ingredients.extend([clean_text(i.text) for i in items])
            else:
                ingredients.extend([clean_text(i.text) for i in ing_list.find_all(recursive=False)])
        
        if not ingredients:
            # Try finding ingredients in paragraphs or spans
            ingredients = [clean_text(i.text) for i in soup.find_all(["p", "span"], 
                class_=re.compile(r"ingredient", re.I))]
        
        # Try to find steps
        steps = []
        instruction_lists = soup.find_all(["ul", "ol"], 
            class_=re.compile(r"instruction|direction|step|method", re.I))
        if not instruction_lists:
            instruction_lists = soup.find_all(class_=re.compile(r"instruction|direction|step|method", re.I))
        
        for inst_list in instruction_lists:
            items = inst_list.find_all("li")
            if items:
                steps.extend([clean_text(i.text) for i in items])
            else:
                steps.extend([clean_text(i.text) for i in inst_list.find_all(recursive=False)])
        
        if not steps:
            # Try finding steps in paragraphs
            steps = [clean_text(s.text) for s in soup.find_all("p", 
                class_=re.compile(r"instruction|direction|step|method", re.I))]
        
        # Filter out empty or invalid steps/ingredients
        ingredients = [i for i in ingredients if i and len(i) > 1 and not i.isspace()]
        steps = [s for s in steps if s and len(s) > 1 and not s.isspace()]
        
        if not ingredients or not steps:
            logger.error("Could not find ingredients or steps")
            return None
        
        # Try to find times in various formats
        prep_time = cook_time = 0
        time_elements = soup.find_all(text=re.compile(r"prep.*time|preparation.*time|cook.*time", re.I))
        for elem in time_elements:
            parent = elem.parent
            if parent:
                text = parent.text.lower()
                if "prep" in text or "preparation" in text:
                    prep_time = parse_time(text)
                elif "cook" in text:
                    cook_time = parse_time(text)
        
        # Try to find servings
        servings = 4  # Default
        servings_elements = soup.find_all(text=re.compile(r"serv(ing|e)s|yield", re.I))
        for elem in servings_elements:
            parent = elem.parent
            if parent:
                servings_text = parent.text
                servings_match = re.search(r"(\d+)", servings_text)
                if servings_match:
                    servings = int(servings_match.group(1))
                    break
        
        return Recipe(name, ingredients, steps, prep_time, cook_time, servings, author)
        
    except (AttributeError, ValueError) as e:
        logger.error(f"Failed to parse HTML: {e}")
    
    return None

def scrape_recipes_from_list(url: str) -> List[Recipe]:
    """Scrape multiple recipes from a list page."""
    html = fetch_page(url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    recipe_links = []
    
    # Find recipe links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "recipe" in href.lower():
            if not href.startswith("http"):
                # Make relative URLs absolute
                href = requests.compat.urljoin(url, href)
            recipe_links.append(href)
    
    # Scrape each recipe
    recipes = []
    for link in recipe_links:
        logger.info(f"Scraping recipe from {link}")
        recipe = scrape_recipe(link)
        if recipe:
            recipes.append(recipe)
            time.sleep(1)  # Be nice to the server
    
    return recipes
