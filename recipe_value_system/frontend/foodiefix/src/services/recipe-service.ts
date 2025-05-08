import { Recipe, RecipeFilters, RecipeListItem, RecipeStatus, CuisineType } from '../types/recipe';
import { trackFeatureUsage } from './feature-tracking';

/**
 * Service for recipe-related operations
 */
export class RecipeService {
  private apiBaseUrl: string;

  constructor() {
    this.apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '/api';
  }

  /**
   * Fetch recipes with optional filters
   * @param filters Optional filters to apply
   * @returns Promise with recipe list items
   */
  async getRecipes(filters?: RecipeFilters): Promise<RecipeListItem[]> {
    try {
      // Track feature usage
      trackFeatureUsage('recipe_list_view', { filters });

      // Build query parameters
      const queryParams = new URLSearchParams();
      if (filters) {
        if (filters.sortBy) queryParams.append('sortBy', filters.sortBy);
        if (filters.difficulty) queryParams.append('difficulty', filters.difficulty.toString());
        if (filters.cuisine) queryParams.append('cuisine', filters.cuisine);
        if (filters.minRating) queryParams.append('minRating', filters.minRating.toString());
        if (filters.maxCost) queryParams.append('maxCost', filters.maxCost.toString());
        if (filters.maxTime) queryParams.append('maxTime', filters.maxTime.toString());
        if (filters.categoryId) queryParams.append('categoryId', filters.categoryId);
        if (filters.searchQuery) queryParams.append('search', filters.searchQuery);
        
        // Handle arrays
        if (filters.dietaryRestrictions?.length) {
          filters.dietaryRestrictions.forEach(restriction => {
            queryParams.append('dietaryRestrictions', restriction);
          });
        }
        
        if (filters.dietaryPreferences?.length) {
          filters.dietaryPreferences.forEach(preference => {
            queryParams.append('dietaryPreferences', preference);
          });
        }
      }

      // Make the API call
      const response = await fetch(`${this.apiBaseUrl}/recipes?${queryParams.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recipes: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.recipes;
    } catch (error) {
      console.error('Error fetching recipes:', error);
      throw error;
    }
  }

  /**
   * Get a recipe by its slug
   * @param slug Recipe slug
   * @returns Promise with recipe details
   */
  async getRecipeBySlug(slug: string): Promise<Recipe> {
    try {
      // Track feature usage
      trackFeatureUsage('recipe_detail_view', { slug });
      
      const response = await fetch(`${this.apiBaseUrl}/recipes/${slug}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recipe: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.recipe;
    } catch (error) {
      console.error(`Error fetching recipe with slug ${slug}:`, error);
      throw error;
    }
  }

  /**
   * Get recipe categories
   * @returns Promise with recipe categories
   */
  async getCategories() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/categories`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch categories: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.categories;
    } catch (error) {
      console.error('Error fetching recipe categories:', error);
      throw error;
    }
  }

  /**
   * Get similar recipes
   * @param recipeId Recipe ID
   * @param limit Number of similar recipes to return
   * @returns Promise with similar recipes
   */
  async getSimilarRecipes(recipeId: string, limit: number = 4): Promise<RecipeListItem[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/recipes/${recipeId}/similar?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch similar recipes: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.recipes;
    } catch (error) {
      console.error(`Error fetching similar recipes for ${recipeId}:`, error);
      throw error;
    }
  }

  /**
   * Get recipe variants
   * @param recipeId Recipe ID
   * @returns Promise with recipe variants
   */
  async getRecipeVariants(recipeId: string): Promise<RecipeListItem[]> {
    try {
      const response = await fetch(`${this.apiBaseUrl}/recipes/${recipeId}/variants`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recipe variants: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.variants;
    } catch (error) {
      console.error(`Error fetching variants for recipe ${recipeId}:`, error);
      throw error;
    }
  }

  /**
   * Rate a recipe
   * @param recipeId Recipe ID
   * @param rating Rating value (1-5)
   * @returns Promise with updated recipe
   */
  async rateRecipe(recipeId: string, rating: number): Promise<Recipe> {
    try {
      // Track feature usage
      trackFeatureUsage('recipe_rating', { recipeId, rating });
      
      const response = await fetch(`${this.apiBaseUrl}/recipes/${recipeId}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rating }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to rate recipe: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.recipe;
    } catch (error) {
      console.error(`Error rating recipe ${recipeId}:`, error);
      throw error;
    }
  }

  /**
   * Favorite a recipe
   * @param recipeId Recipe ID
   * @param isFavorite Whether to favorite or unfavorite
   * @returns Promise with success status
   */
  async favoriteRecipe(recipeId: string, isFavorite: boolean): Promise<{ success: boolean }> {
    try {
      // Track feature usage
      trackFeatureUsage('recipe_favorite', { recipeId, isFavorite });
      
      const response = await fetch(`${this.apiBaseUrl}/recipes/${recipeId}/favorite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isFavorite }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to ${isFavorite ? 'favorite' : 'unfavorite'} recipe: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error ${isFavorite ? 'favoriting' : 'unfavoriting'} recipe ${recipeId}:`, error);
      throw error;
    }
  }
}

// Export a singleton instance
export const recipeService = new RecipeService();
