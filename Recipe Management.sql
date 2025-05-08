-- SQL Schema for Recipe Management System
"""
-- Recipes and their core components
CREATE TABLE recipes (
    recipe_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    servings INTEGER,
    difficulty_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id),
    is_published BOOLEAN DEFAULT false
);

CREATE TABLE ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_unit VARCHAR(50),
    category VARCHAR(100)
);

CREATE TABLE recipe_ingredients (
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    ingredient_id INTEGER REFERENCES ingredients(ingredient_id),
    quantity DECIMAL(10,2),
    unit VARCHAR(50),
    notes TEXT,
    PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE recipe_steps (
    step_id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    step_number INTEGER,
    instruction TEXT NOT NULL
);

-- User-related tables
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User engagement tables
CREATE TABLE user_favorites (
    user_id INTEGER REFERENCES users(user_id),
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id)
);

CREATE TABLE recipe_ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    taste_rating VARCHAR(50) CHECK (taste_rating IN (
        'Hate - I would never eat this again, even if paid',
        'Don''t Like - I''d rather eat something else, but could tolerate it',
        'Meh - It''s edible but nothing special', 
        'Like - I enjoy this and would eat it again',
        'Love - This is delicious and I look forward to having it',
        'Crave - I can''t stop thinking about this dish and need to have it again'
    )),
    risk_rating VARCHAR(50) CHECK (risk_rating IN (
        'No Risk - Highly rated recipe with positive reviews and similar to recipes you enjoy',
        'Low Risk - Well-reviewed recipe with some similarity to your preferences',
        'Medium Risk - Mixed reviews or uncertain match to your taste profile',
        'High Risk - Poor reviews or significantly different from your preferred recipes',
        'Extreme Risk - Negative reviews and very different from your typical choices'
    )),
    difficulty_rating VARCHAR(50) CHECK (difficulty_rating IN (
        'Beginner - Basic kitchen skills, simple tools (microwave, toaster)',
        'Easy - Basic techniques, common kitchen tools (pots, pans, measuring cups)',
        'Intermediate - Multiple techniques, specialized tools (food processor, mixer)',
        'Advanced - Complex techniques, precise timing, professional tools (mandoline, thermometer)',
        'Expert - Professional techniques, specialized equipment (sous vide, blast chiller)'
    )),
    time_accuracy DECIMAL(5,2) CHECK (time_accuracy BETWEEN 0 AND 100),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, recipe_id)
);

CREATE TABLE recipe_views (
    view_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_cooking_history (
    history_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    cooked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    servings_made INTEGER,
    notes TEXT
);

-- Optional: Tags for better recipe organization
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE recipe_tags (
    recipe_id INTEGER REFERENCES recipes(recipe_id),
    tag_id INTEGER REFERENCES tags(tag_id),
    PRIMARY KEY (recipe_id, tag_id)
);

CREATE INDEX idx_recipe_ratings_recipe_id ON recipe_ratings(recipe_id);
CREATE INDEX idx_recipe_views_recipe_id ON recipe_views(recipe_id);
CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
"""