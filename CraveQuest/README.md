# CraveQuest

A simple CLI tool to track recipes and rate them based on multiple factors.

## Features

- Add recipes with ingredients and steps
- Vote on recipes (0-6 scale) for:
  - Taste
  - Health
  - Quickness
  - Cost
  - Ease
- Get recipe suggestions based on:
  - Time since last made
  - Mob Score (taste + health) / (quick + cheap + easy)
- Save/load recipes to JSON file

## Usage

Run the CLI:
```bash
python src/cli.py
```

## Project Structure

```
CraveQuest/
├── src/
│   ├── models/
│   │   └── recipe.py    # Recipe class definition
│   ├── cli.py           # Command-line interface
│   └── __init__.py
├── data/
│   └── recipes.json     # Recipe storage
├── .gitignore
├── README.md
└── requirements.txt
```

## Recipe Rating System

Recipes are rated on a 0-6 scale:
- 0: Hate
- 1: Don't Like
- 2: Meh
- 3: Like
- 4: Love
- 5: Crave
- 6: Legendary

The Mob Score is calculated as: (taste + health) / (quick + cheap + easy)
Higher scores indicate better taste/health relative to effort/cost.
