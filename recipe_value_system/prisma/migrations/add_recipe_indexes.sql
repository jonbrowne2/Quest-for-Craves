-- Indexes for common queries and analytics
CREATE INDEX IF NOT EXISTS "recipe_value_score_idx" ON "Recipe" USING btree ("valueScore" DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS "recipe_created_at_idx" ON "Recipe" USING btree ("createdAt" DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS "recipe_cuisine_idx" ON "Recipe" USING btree ("cuisine");
CREATE INDEX IF NOT EXISTS "recipe_difficulty_idx" ON "Recipe" USING btree ("difficulty");

-- Composite indexes for analytics queries
CREATE INDEX IF NOT EXISTS "recipe_analytics_composite_idx"
ON "Recipe" USING btree ("valueScore" DESC NULLS LAST, "craveRate" DESC NULLS LAST, "createdAt" DESC NULLS LAST);

-- Indexes for interaction queries
CREATE INDEX IF NOT EXISTS "recipe_interaction_type_idx" ON "RecipeInteraction" USING btree ("type");
CREATE INDEX IF NOT EXISTS "recipe_interaction_created_at_idx" ON "RecipeInteraction" USING btree ("createdAt" DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS "recipe_interaction_composite_idx"
ON "RecipeInteraction" USING btree ("recipeId", "type", "createdAt" DESC NULLS LAST);

-- Full text search index for recipe search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS "recipe_title_trgm_idx" ON "Recipe" USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS "recipe_description_trgm_idx" ON "Recipe" USING gin (description gin_trgm_ops);
