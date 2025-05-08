"""Simple CLI for recipe management and value metrics."""
from datetime import datetime
from typing import List, Dict, Tuple

from ..models.recipe import Recipe
from ..storage.recipe_store import RecipeStore
from ..calculators.value_calculator import ValueCalculator
from ..db.database import get_session

# Score descriptions customized for each metric
METRIC_SCORES: Dict[str, Dict[int, str]] = {
    "taste": {
        0: "Inedible—You couldn't pay me to eat this",
        1: "Terrible—Even though I'm hungry, I won't eat this",
        2: "Poor—I think it's ok but not a fan",
        3: "Good—I like this recipe",
        4: "Great—I love this recipe",
        5: "Amazing—I want to eat this recipe all the time",
        6: "Legendary—This is top 5 things I've ever eaten"
    },
    "health": {
        0: "Extremely Unhealthy—Pure junk food, zero nutritional value",
        1: "Very Unhealthy—Mostly empty calories",
        2: "Unhealthy—Some redeeming qualities but mostly unhealthy",
        3: "Moderate—Balance of healthy and unhealthy elements",
        4: "Healthy—Good nutritional value with some indulgence",
        5: "Very Healthy—Excellent nutrition with great balance",
        6: "Super Healthy—Perfect nutritional profile"
    },
    "quick": {
        0: "Endless—Takes all day or multiple days",
        1: "Very Slow—3+ hours total time",
        2: "Slow—2-3 hours total time",
        3: "Medium—1-2 hours total time",
        4: "Quick—30-60 minutes total time",
        5: "Very Quick—15-30 minutes total time",
        6: "Super Quick—Under 15 minutes total time"
    },
    "cheap": {
        0: "Extremely Expensive—Luxury ingredients only",
        1: "Very Expensive—Many specialty ingredients",
        2: "Expensive—Several premium ingredients",
        3: "Moderate—Mix of basic and premium ingredients",
        4: "Affordable—Mostly basic ingredients",
        5: "Very Affordable—All common ingredients",
        6: "Super Affordable—Minimal, basic ingredients"
    },
    "easy": {
        0: "Impossible—Requires professional chef skills",
        1: "Very Hard—Advanced cooking techniques required",
        2: "Hard—Some challenging techniques needed",
        3: "Medium—Basic cooking skills sufficient",
        4: "Easy—Simple techniques only",
        5: "Very Easy—Minimal cooking required",
        6: "Super Easy—Anyone can make this"
    }
}

METRIC_DESCRIPTIONS: Dict[str, Tuple[str, str]] = {
    "taste": ("Taste", "How good does it taste?"),
    "health": ("Health", "How healthy and nutritious is it?"),
    "quick": ("Speed", "How quick is it to prepare and cook?"),
    "cheap": ("Cost", "How affordable are the ingredients?"),
    "easy": ("Ease", "How easy is it to make?")
}

def get_multiline_input(prompt: str) -> List[str]:
    """Get multiple lines of input, handling paste operations better."""
    print(prompt)
    print("(Paste your text, then press Enter twice to finish)")
    lines = []
    empty_lines = 0
    
    while empty_lines < 2:
        try:
            line = input("> ").strip()
            if not line:
                empty_lines += 1
            else:
                empty_lines = 0
                lines.append(line)
        except EOFError:
            break
    
    return [line for line in lines if line]

def get_recipe_input() -> Recipe:
    """Get recipe information from user input."""
    print("\n=== Add New Recipe ===")
    name = input("Recipe name: ").strip()
    description = input("Description: ").strip()
    
    ingredients = get_multiline_input("\nIngredients (one per line):")
    steps = get_multiline_input("\nSteps (one per line):")
    
    return Recipe(
        name=name,
        description=description,
        ingredients=ingredients,
        steps=steps,
        created_at=datetime.now()
    )

def get_metric_vote(metric: str, recipe_name: str) -> int:
    """Get a vote for a specific metric."""
    name, description = METRIC_DESCRIPTIONS[metric]
    print(f"\n{name} Rating - {description}")
    print("Score levels:")
    for score, desc in METRIC_SCORES[metric].items():
        print(f"{score}: {desc}")
    
    while True:
        try:
            score = int(input(f"\nRate {recipe_name}'s {name.lower()} (0-6): "))
            if 0 <= score <= 6:
                return score
            print("Score must be between 0 and 6")
        except ValueError:
            print("Please enter a number between 0 and 6")

def add_vote(recipe: Recipe, store: RecipeStore, recipes: List[Recipe]) -> None:
    """Add comprehensive votes for a recipe."""
    print(f"\n=== Rate {recipe.name} ===")
    print("You'll rate this recipe on 5 metrics:")
    for name, (metric, desc) in METRIC_DESCRIPTIONS.items():
        print(f"- {metric}: {desc}")
    
    votes = {
        metric: get_metric_vote(metric, recipe.name)
        for metric in METRIC_DESCRIPTIONS
    }
    
    recipe.add_vote(
        taste=votes["taste"],
        health=votes["health"],
        quick=votes["quick"],
        cheap=votes["cheap"],
        easy=votes["easy"]
    )
    
    # Save after voting
    store.save_recipes(recipes)
    
    print("\nVote recorded! Updated metrics:")
    print(f"Rating (Taste/Health): {recipe.rating:.2f}")
    print(f"Complexity (Speed/Cost/Ease): {recipe.complexity:.2f}")
    print(f"Overall Mob Score: {recipe.mob_score:.2f}")

def display_metrics(recipe: Recipe, calculator: ValueCalculator) -> None:
    """Display value metrics for a recipe."""
    metrics = calculator.calculate_value_metrics(recipe)
    
    print(f"\nValue Metrics for {recipe.name}:")
    print("\nBase Scores (0-6):")
    if recipe.mob_score is not None:
        print(f"Rating: {recipe.rating:.2f}")
        print(f"Complexity: {recipe.complexity:.2f}")
        print(f"Mob Score: {recipe.mob_score:.2f}")
    else:
        print("No votes yet")
    
    print("\nValue Analysis (0-100%):")
    print(f"Quality: {metrics['quality']*100:.1f}% - Based on rating and completeness")
    print(f"Complexity: {metrics['complexity']*100:.1f}% - Higher means easier/faster/cheaper")
    print(f"Rating Impact: {metrics['rating']*100:.1f}% - Rating weighted by time value")
    print(f"Time Value: {metrics['time_value']*100:.1f}% - Value for time invested")
    
    if recipe.prep_time is not None and recipe.cook_time is not None:
        total_time = recipe.get_total_time()
        print(f"\nTime Investment:")
        print(f"Prep Time: {recipe.prep_time} minutes")
        print(f"Cook Time: {recipe.cook_time} minutes")
        print(f"Total Time: {total_time} minutes")
    
    if recipe.votes["taste"]:
        print("\nVote Distribution:")
        for metric, (name, _) in METRIC_DESCRIPTIONS.items():
            votes = recipe.votes[metric]
            avg = sum(votes) / len(votes)
            print(f"{name}: {avg:.2f}/6.0 ({len(votes)} votes)")

def display_recipe(recipe: Recipe, calculator: ValueCalculator) -> None:
    """Display recipe details and metrics."""
    print(f"\n=== {recipe.name} ===")
    print(f"Description: {recipe.description}")
    
    print("\nIngredients:")
    for ingredient in recipe.ingredients:
        print(f"- {ingredient}")
    
    print("\nSteps:")
    for i, step in enumerate(recipe.steps, 1):
        print(f"{i}. {step}")
    
    if recipe.mob_score is not None:
        display_metrics(recipe, calculator)
    else:
        print("\nNo votes yet")

def main() -> None:
    """Main CLI interface."""
    store = RecipeStore()
    recipes = store.load_recipes()
    
    # Set up database session and calculator
    session = get_session()
    calculator = ValueCalculator(session)
    
    while True:
        print("\n=== FoodieMob Recipe System ===")
        print("1. Add Recipe")
        print("2. View Recipes")
        print("3. Vote on Recipe")
        print("4. Calculate Metrics")
        print("5. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            recipe = get_recipe_input()
            recipes.append(recipe)
            store.save_recipes(recipes)
            print("\nRecipe added successfully!")
            
        elif choice == "2":
            if not recipes:
                print("\nNo recipes yet!")
                continue
            print("\n=== Recipes ===")
            for i, recipe in enumerate(recipes, 1):
                print(f"{i}. {recipe.name} ", end="")
                if recipe.mob_score is not None:
                    metrics = calculator.calculate_value_metrics(recipe)
                    print(f"(Mob: {recipe.mob_score:.1f}/6.0, Quality: {metrics['quality']*100:.0f}%)")
                else:
                    print("(No votes)")
            
            try:
                idx = int(input("\nSelect recipe number to view (0 to cancel): ")) - 1
                if 0 <= idx < len(recipes):
                    display_recipe(recipes[idx], calculator)
            except (ValueError, IndexError):
                print("Invalid selection")
                
        elif choice == "3":
            if not recipes:
                print("\nNo recipes to vote on!")
                continue
            print("\n=== Vote on Recipe ===")
            for i, recipe in enumerate(recipes, 1):
                print(f"{i}. {recipe.name}")
            
            try:
                idx = int(input("\nSelect recipe number to vote (0 to cancel): ")) - 1
                if 0 <= idx < len(recipes):
                    add_vote(recipes[idx], store, recipes)
            except (ValueError, IndexError):
                print("Invalid selection")
                
        elif choice == "4":
            if not recipes:
                print("\nNo recipes to analyze!")
                continue
            print("\n=== Calculate Metrics ===")
            for i, recipe in enumerate(recipes, 1):
                print(f"{i}. {recipe.name}")
            
            try:
                idx = int(input("\nSelect recipe number (0 to cancel): ")) - 1
                if 0 <= idx < len(recipes):
                    display_metrics(recipes[idx], calculator)
            except (ValueError, IndexError):
                print("Invalid selection")
                
        elif choice == "5":
            store.save_recipes(recipes)
            session.close()  # Clean up database session
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()
