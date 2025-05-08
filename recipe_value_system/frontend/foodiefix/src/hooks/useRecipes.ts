import { useState, useEffect, useCallback } from 'react';
import { Recipe, RecipeFilters, RecipeListItem } from '../types/recipe';
import { recipeService } from '../services/recipe-service';

/**
 * Hook for recipe list operations
 */
export function useRecipeList(initialFilters?: RecipeFilters) {
  const [recipes, setRecipes] = useState<RecipeListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [filters, setFilters] = useState<RecipeFilters | undefined>(initialFilters);

  const fetchRecipes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await recipeService.getRecipes(filters);
      setRecipes(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  const updateFilters = useCallback((newFilters: RecipeFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  return {
    recipes,
    loading,
    error,
    filters,
    updateFilters,
    refreshRecipes: fetchRecipes
  };
}

/**
 * Hook for single recipe operations
 */
export function useRecipe(slug: string) {
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [similarRecipes, setSimilarRecipes] = useState<RecipeListItem[]>([]);
  const [variants, setVariants] = useState<RecipeListItem[]>([]);

  const fetchRecipe = useCallback(async () => {
    if (!slug) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await recipeService.getRecipeBySlug(slug);
      setRecipe(data);
      
      // Fetch similar recipes if we have a recipe ID
      if (data.id) {
        const similar = await recipeService.getSimilarRecipes(data.id);
        setSimilarRecipes(similar);
        
        // Fetch variants if this recipe has any
        const recipeVariants = await recipeService.getRecipeVariants(data.id);
        setVariants(recipeVariants);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'));
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    fetchRecipe();
  }, [fetchRecipe]);

  const rateRecipe = useCallback(async (rating: number) => {
    if (!recipe) return;
    
    try {
      const updatedRecipe = await recipeService.rateRecipe(recipe.id, rating);
      setRecipe(updatedRecipe);
      return updatedRecipe;
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to rate recipe'));
      throw err;
    }
  }, [recipe]);

  const favoriteRecipe = useCallback(async (isFavorite: boolean) => {
    if (!recipe) return;
    
    try {
      await recipeService.favoriteRecipe(recipe.id, isFavorite);
      setRecipe(prev => prev ? { ...prev, favoriteCount: isFavorite ? prev.favoriteCount + 1 : Math.max(0, prev.favoriteCount - 1) } : null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to favorite recipe'));
      throw err;
    }
  }, [recipe]);

  return {
    recipe,
    loading,
    error,
    similarRecipes,
    variants,
    rateRecipe,
    favoriteRecipe,
    refreshRecipe: fetchRecipe
  };
}

/**
 * Hook for recipe categories
 */
export function useRecipeCategories() {
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await recipeService.getCategories();
      setCategories(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch categories'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  return {
    categories,
    loading,
    error,
    refreshCategories: fetchCategories
  };
}
