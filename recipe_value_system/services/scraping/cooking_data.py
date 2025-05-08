"""Common cooking data and knowledge base."""

# Common cooking ingredients by category
INGREDIENTS = {
    "grains": {
        "flour": [
            "all-purpose flour",
            "bread flour",
            "cake flour",
            "whole wheat flour",
            "self-rising flour",
        ],
        "rice": [
            "white rice",
            "brown rice",
            "jasmine rice",
            "basmati rice",
            "arborio rice",
        ],
        "pasta": ["spaghetti", "penne", "fettuccine", "linguine", "macaroni"],
        "other": ["quinoa", "oats", "cornmeal", "breadcrumbs"],
    },
    "dairy": {
        "milk": [
            "whole milk",
            "skim milk",
            "2% milk",
            "buttermilk",
            "heavy cream",
            "half-and-half",
        ],
        "cheese": ["cheddar", "mozzarella", "parmesan", "cream cheese", "ricotta"],
        "other": ["butter", "yogurt", "sour cream", "eggs"],
    },
    "proteins": {
        "meat": ["chicken", "beef", "pork", "turkey", "lamb"],
        "seafood": ["salmon", "tuna", "shrimp", "cod", "tilapia"],
        "vegetarian": ["tofu", "tempeh", "seitan", "lentils", "chickpeas"],
    },
    "produce": {
        "vegetables": [
            "onion",
            "garlic",
            "carrot",
            "celery",
            "bell pepper",
            "tomato",
            "potato",
            "broccoli",
            "spinach",
            "lettuce",
            "cucumber",
            "zucchini",
        ],
        "fruits": [
            "apple",
            "banana",
            "orange",
            "lemon",
            "lime",
            "strawberry",
            "blueberry",
            "raspberry",
            "grape",
            "pineapple",
            "mango",
            "avocado",
        ],
        "herbs": [
            "basil",
            "parsley",
            "cilantro",
            "thyme",
            "rosemary",
            "oregano",
            "mint",
        ],
    },
}

# Common cooking equipment
EQUIPMENT = [
    "oven",
    "stove",
    "microwave",
    "blender",
    "food processor",
    "mixer",
    "knife",
    "cutting board",
    "measuring cups",
    "measuring spoons",
    "pot",
    "pan",
    "baking sheet",
    "baking dish",
    "bowl",
    "whisk",
    "spatula",
    "spoon",
    "colander",
    "grater",
]

# Common cooking methods
COOKING_METHODS = [
    "bake",
    "broil",
    "grill",
    "roast",
    "fry",
    "sauté",
    "simmer",
    "boil",
    "steam",
    "poach",
    "braise",
    "stir-fry",
    "deep-fry",
    "blanch",
    "reduce",
]

# Standard cooking temperatures (°F)
TEMPERATURE_RANGES = {
    "low": (170, 250),
    "medium-low": (251, 300),
    "medium": (301, 375),
    "medium-high": (376, 450),
    "high": (451, 550),
}

# Flatten ingredients for easy lookup
ALL_INGREDIENTS = set()
for category in INGREDIENTS.values():
    for subcategory in category.values():
        ALL_INGREDIENTS.update(subcategory)

ALL_EQUIPMENT = set(EQUIPMENT)
ALL_COOKING_METHODS = set(COOKING_METHODS)


def normalize_unit(unit: str) -> str:
    """Normalize a unit string to its standard form."""
    unit = unit.lower().strip()
    # Common unit mappings
    mappings = {
        "tbsp": "tablespoon",
        "tbs": "tablespoon",
        "tsp": "teaspoon",
        "oz": "ounce",
        "lb": "pound",
        "c": "cup",
        "g": "gram",
        "kg": "kilogram",
        "ml": "milliliter",
        "l": "liter",
    }
    return mappings.get(unit, unit)


def is_valid_temperature(temp: float) -> bool:
    """Check if a temperature is within valid cooking ranges."""
    return any(low <= temp <= high for low, high in TEMPERATURE_RANGES.values())


def is_valid_time(minutes: int) -> bool:
    """Check if a cooking time is within valid ranges."""
    return 0 < minutes < 1440  # Max 24 hours


def is_valid_serving_size(servings: int) -> bool:
    """Check if a serving size is within valid ranges."""
    return 1 <= servings <= 100  # Reasonable range for most recipes
