from typing import List
import json
import os
from datetime import datetime

from models.recipe import Recipe
from models.user import User
from constants import SCORE_LEVELS, CLEANUP_LEVELS
from scraper import scrape_recipe

def get_multiline_input(prompt: str) -> List[str]:
    print(prompt, "(Enter twice to finish)")
    lines = []
    while True:
        line = input("> ").strip()
        if not line and lines: break
        if line: lines.append(line)
    return lines or ["None"]

def onboard_user(user: User) -> None:
    print("\n=== Welcome to Epicurean Edge! Let's set your preferences ===")
    print("Rank these from most to least important (1-5): Taste, Risk, Time, Effort, Sacrifice")
    ranks = {}
    for factor in ["Taste", "Risk", "Time", "Effort", "Sacrifice"]:
        rank = int(input(f"Where does {factor} rank (1-5, 1=most important)? "))
        while rank < 1 or rank > 5 or rank in ranks.values():
            rank = int(input(f"Try again (1-5, unique): "))
        ranks[factor] = rank
    for factor, rank in ranks.items():
        user.coefficients[f"C_{factor.lower()}"] = 1.0 - (rank - 1) * 0.2

def add_recipe(user: User) -> Recipe:
    print("\n=== Add Recipe ===")
    while True:
        name = input("Name: ").strip()
        if name: break
        print("Name can't be empty!")
    ingred_input = input("Ingredients (comma-separated, e.g., '2 cups flour, 1 tsp salt'): ").strip()
    ingredients = [i.strip() for i in ingred_input.split(",") if i.strip()] or ["None"]
    steps = get_multiline_input("Steps (e.g., 'Mix flour and salt'):")
    prep_time = int(input("Prep time (minutes): "))
    cook_time = int(input("Cook time (minutes): "))
    servings = int(input("Servings: "))
    owner = input("Your name (owner): ").strip() or "User"
    recipe = Recipe(name, ingredients, steps, prep_time, cook_time, servings, owner)
    if recipe.has_allergy_or_dislike(user):
        print("Warning: Contains allergies or dislikes!")
    return recipe

def add_recipe_from_url(recipes: List[Recipe], user: User) -> None:
    print("\n=== Add Recipe from URL ===")
    url = input("Enter recipe URL: ").strip()
    if not url:
        print("URL can't be empty!")
        return
    recipe = scrape_recipe(url)
    if recipe:
        if recipe.has_allergy_or_dislike(user):
            print("Warning: Contains allergies or dislikes!")
        recipes.append(recipe)
        print(f"Added {recipe.name} ({recipe.owner}) from {url}!")
    else:
        print("Failed to scrape recipe. Check the URL or try another site.")

def vote_recipe(recipe: Recipe, user: User) -> None:
    print("\n=== Vote on Taste ===")
    taste_keys = list(SCORE_LEVELS.keys())
    for i, (rank, desc) in enumerate(SCORE_LEVELS.items(), 1):
        print(f"{i}. {rank}: {desc}")
    while True:
        try:
            taste_num = int(input(f"What would you rate {recipe.name} taste-wise? (1-7): "))
            if 1 <= taste_num <= 7:
                taste = taste_keys[taste_num - 1]
                break
            print("Please enter a number between 1 and 7!")
        except ValueError:
            print("Invalid input! Enter a number between 1 and 7.")

    print("\n=== Vote on Cleanup ===")
    cleanup_keys = list(CLEANUP_LEVELS.keys())
    for i, (rank, desc) in enumerate(CLEANUP_LEVELS.items(), 1):
        print(f"{i}. {rank}: {desc}")
    while True:
        try:
            cleanup_num = int(input(f"How bad was cleanup for {recipe.name}? (1-4): "))
            if 1 <= cleanup_num <= 4:
                cleanup = cleanup_keys[cleanup_num - 1]
                break
            print("Please enter a number between 1 and 4!")
        except ValueError:
            print("Invalid input! Enter a number between 1 and 4.")

    recipe.add_feedback(taste, cleanup)
    user.adjust_coefficients(recipe, taste, cleanup)
    print(f"\nVoted! Taste: {taste}, Cleanup: {cleanup}")

def remove_recipe(recipes: List[Recipe]) -> None:
    if not recipes:
        print("No recipes to remove!")
        return
    print("\n=== Remove Recipe ===")
    for i, r in enumerate(recipes, 1):
        print(f"{i}. {r.name} ({r.owner})")
    while True:
        try:
            idx = int(input("Which recipe to remove (0 to cancel): ")) - 1
            if idx == -1:
                print("Cancelled!")
                return
            if 0 <= idx < len(recipes):
                removed = recipes.pop(idx)
                print(f"Removed {removed.name}!")
                return
            print(f"Please enter a number between 0 and {len(recipes)}!")
        except ValueError:
            print("Invalid input! Enter a number.")

def edit_ingredients(current_ingredients: List[str]) -> List[str]:
    ingredients = current_ingredients.copy()
    while True:
        print("\nCurrent Ingredients:")
        for i, ingred in enumerate(ingredients, 1):
            print(f"{i}. {ingred}")
        print("\nOptions: (a)dd, (r)emove, (e)dit, (f)inish")
        choice = input("What to do? ").lower().strip()
        
        if choice == "a":
            new_ingred = input("New ingredient: ").strip()
            if new_ingred:
                ingredients.append(new_ingred)
                print(f"Added {new_ingred}")
        
        elif choice == "r":
            if not ingredients:
                print("Nothing to remove!")
                continue
            idx = int(input("Number to remove (1-{}): ".format(len(ingredients)))) - 1
            if 0 <= idx < len(ingredients):
                removed = ingredients.pop(idx)
                print(f"Removed {removed}")
            else:
                print("Invalid number!")
        
        elif choice == "e":
            if not ingredients:
                print("Nothing to edit!")
                continue
            idx = int(input("Number to edit (1-{}): ".format(len(ingredients)))) - 1
            if 0 <= idx < len(ingredients):
                new_value = input(f"New value for '{ingredients[idx]}': ").strip()
                if new_value:
                    ingredients[idx] = new_value
                    print(f"Updated to {new_value}")
            else:
                print("Invalid number!")
        
        elif choice == "f":
            return ingredients if ingredients else ["None"]
        
        else:
            print("Invalid option! Use a, r, e, or f.")

def edit_recipe(recipes: List[Recipe], user: User) -> None:
    if not recipes:
        print("No recipes to edit!")
        return
    print("\n=== Edit Recipe ===")
    for i, r in enumerate(recipes, 1):
        print(f"{i}. {r.name} ({r.owner})")
    while True:
        try:
            idx = int(input("Which recipe to edit (0 to cancel): ")) - 1
            if idx == -1:
                print("Cancelled!")
                return
            if 0 <= idx < len(recipes):
                recipe = recipes[idx]
                break
            print(f"Please enter a number between 0 and {len(recipes)}!")
        except ValueError:
            print("Invalid input! Enter a number.")
    
    print(f"\nEditing {recipe.name} (leave blank to keep current)")
    name = input(f"Name [{recipe.name}]: ").strip() or recipe.name
    print("Edit ingredients? (y/n): ")
    if input().lower() == "y":
        ingredients = edit_ingredients(recipe.ingredients)
    else:
        ingredients = recipe.ingredients
    print(f"Steps [{', '.join(recipe.steps)}]:")
    steps = get_multiline_input("New steps:") if input("Edit steps? (y/n): ").lower() == "y" else recipe.steps
    prep_time = int(input(f"Prep time (minutes) [{recipe.prep_time}]: ") or recipe.prep_time)
    cook_time = int(input(f"Cook time (minutes) [{recipe.cook_time}]: ") or recipe.cook_time)
    servings = int(input(f"Servings [{recipe.servings}]: ") or recipe.servings)
    owner = input("Your name (new owner): ").strip() or "User" if any([
        name != recipe.name, ingredients != recipe.ingredients, steps != recipe.steps,
        prep_time != recipe.prep_time, cook_time != recipe.cook_time, servings != recipe.servings
    ]) else recipe.owner
    recipes[idx] = Recipe(name, ingredients, steps, prep_time, cook_time, servings, owner)
    if recipes[idx].has_allergy_or_dislike(user):
        print("Warning: Contains allergies or dislikes!")
    print(f"Updated {name} ({recipes[idx].owner})!")

def edit_user(user: User) -> None:
    print("\n=== Edit Profile ===")
    ability = input(f"Cook-ability (Beginner/Home Cook/Chef, current {user.cook_ability}): ").capitalize() or user.cook_ability
    if ability in ["Beginner", "Home Cook", "Chef"]:
        user.cook_ability = ability
    user.novelty_push = float(input(f"Novelty push (0-1, current {user.novelty_push}): ") or user.novelty_push)
    user.nostalgia_sensitivity = float(input(f"Nostalgia sensitivity (0-1, current {user.nostalgia_sensitivity}): ") or user.nostalgia_sensitivity)
    user.allergies = input(f"Allergies (comma-separated, current {user.allergies}): ").split(",") or user.allergies
    user.likes = input(f"Likes (comma-separated, current {user.likes}): ").split(",") or user.likes
    user.dislikes = input(f"Dislikes (comma-separated, current {user.dislikes}): ").split(",") or user.dislikes

def get_grocery_list(recipes: List[Recipe]) -> None:
    if not recipes:
        print("No recipes to shop for!")
        return
    print("\n=== Get Grocery List ===")
    for i, r in enumerate(recipes, 1):
        print(f"{i}. {r.name} ({r.owner})")
    while True:
        try:
            idx = int(input("Which recipe to shop for (0 to cancel): ")) - 1
            if idx == -1:
                print("Cancelled!")
                return
            if 0 <= idx < len(recipes):
                recipe = recipes[idx]
                print(f"\nGrocery List for {recipe.name}:")
                for item in recipe.get_grocery_list():
                    print(f"- {item}")
                return
        except ValueError:
            print("Invalid input! Enter a number.")

def save_recipes(recipes: List[Recipe], filename: str = "data/recipes.json") -> None:
    base_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_path, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = [{"name": r.name, "ingredients": r.ingredients, "steps": r.steps,
             "prep_time": r.prep_time, "cook_time": r.cook_time, "servings": r.servings,
             "owner": r.owner, "votes": r.votes, "cleanups": r.cleanups,
             "last_made": r.last_made.isoformat() if r.last_made else None,
             "made_count": r.made_count, "health_rating": r.health_rating, "macros_fit": r.macros_fit,
             "difficulty": r.difficulty} 
            for r in recipes]
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(recipes)} recipes to {os.path.abspath(filepath)}")
    except Exception as e:
        print(f"Failed to save recipes: {e}")

def load_recipes(filename: str = "data/recipes.json") -> List[Recipe]:
    base_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_path, filename)
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        recipes = []
        for r in data:
            recipe = Recipe(r["name"], r["ingredients"], r["steps"], 
                          r["prep_time"], r["cook_time"], r["servings"], r.get("owner", "Unknown"))
            recipe.votes = r["votes"]
            recipe.cleanups = r["cleanups"]
            recipe.last_made = datetime.fromisoformat(r["last_made"]) if r["last_made"] else None
            recipe.made_count = r["made_count"]
            recipe.health_rating = r["health_rating"]
            recipe.macros_fit = r["macros_fit"]
            recipe.difficulty = r["difficulty"]
            recipes.append(recipe)
        print(f"Loaded {len(recipes)} recipes from {os.path.abspath(filepath)}")
        return recipes
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"No recipes found or invalid JSON ({e}), starting fresh")
        return []

def main() -> None:
    recipes = load_recipes()
    user = User.load()
    if not user.coefficients["C_taste"]:
        onboard_user(user)
    while True:
        print("\n=== Epicurean Edge ===")
        print("1. Add Recipe", "2. Vote", "3. Suggest Recipe", "4. Edit Profile", 
              "5. Exit", "6. Remove Recipe", "7. Add from URL", "8. Edit Recipe", 
              "9. Get Grocery List", sep="\n")
        choice = input("Choice: ").strip()

        if choice == "1":
            recipes.append(add_recipe(user))
            print("Added!")
        
        elif choice == "2":
            if not recipes:
                print("No recipes yet!")
                continue
            for i, r in enumerate(recipes, 1):
                print(f"{i}. {r.name} ({r.owner})")
            idx = int(input("Vote on (0 to cancel): ")) - 1
            if 0 <= idx < len(recipes):
                vote_recipe(recipes[idx], user)
                recipes[idx].mark_made()

        elif choice == "3":
            if not recipes:
                print("No recipes yet!")
                continue
            options = [r for r in recipes if (not r.last_made or (datetime.now() - r.last_made).days > 7) and
                      not r.has_allergy_or_dislike(user)]
            if not options:
                print("No fresh suggestions!")
            else:
                suggestion = max(options, key=lambda r: r.calculate_value(user) if r.votes else 0)
                print(f"\nTry: {suggestion.name} (Top pick for your taste!)")
                if any(vote in ["Love", "Crave", "Legendary"] for vote in suggestion.votes):
                    print("This one's a winner! Future experiments could make it faster, easier, or cheaper.")

        elif choice == "4":
            edit_user(user)
            user.save()

        elif choice == "5":
            save_recipes(recipes)
            user.save()
            print("Goodbye!")
            break

        elif choice == "6":
            remove_recipe(recipes)
            save_recipes(recipes)

        elif choice == "7":
            add_recipe_from_url(recipes, user)
            save_recipes(recipes)

        elif choice == "8":
            edit_recipe(recipes, user)
            save_recipes(recipes)

        elif choice == "9":
            get_grocery_list(recipes)

if __name__ == "__main__":
    main()
