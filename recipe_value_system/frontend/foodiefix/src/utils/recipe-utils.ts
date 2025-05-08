import { Recipe, RecipeListItem, RecipeTitle, RecipeCategoryAssignment, CuisineType, RecipeStatus } from '../types/recipe';

/**
 * Formats a recipe's time (prep, cook, total) into a human-readable string
 * @param minutes Time in minutes
 * @returns Formatted time string
 */
export function formatTime(minutes: number): string {
  if (!minutes) return 'N/A';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours > 0) {
    return `${hours}h ${mins > 0 ? `${mins}m` : ''}`;
  }
  
  return `${mins}m`;
}

/**
 * Get the primary title from a recipe's titles array
 * @param titles Array of recipe titles
 * @returns Primary title or first title if no primary is found
 */
export function getPrimaryTitle(titles: RecipeTitle[]): string {
  if (!titles || titles.length === 0) return '';
  
  const primaryTitle = titles.find(title => title.isPrimary);
  return primaryTitle ? primaryTitle.title : titles[0].title;
}

/**
 * Get the primary category from a recipe's category assignments
 * @param assignments Array of category assignments
 * @returns Primary category name or first category if no primary is found
 */
export function getPrimaryCategory(assignments: RecipeCategoryAssignment[]): string {
  if (!assignments || assignments.length === 0) return '';
  
  const primaryAssignment = assignments.find(assignment => assignment.isPrimary);
  return primaryAssignment ? primaryAssignment.categoryName : assignments[0].categoryName;
}

/**
 * Convert a backend recipe object to a frontend RecipeListItem
 * @param backendRecipe Backend recipe object
 * @returns Frontend RecipeListItem
 */
export function toRecipeListItem(backendRecipe: any): RecipeListItem {
  return {
    id: backendRecipe.id.toString(),
    title: backendRecipe.title,
    slug: backendRecipe.slug,
    imageUrl: backendRecipe.image_url,
    prepTime: backendRecipe.prep_time || 0,
    cookTime: backendRecipe.cook_time || 0,
    totalTime: backendRecipe.total_time || 0,
    difficultyScore: backendRecipe.difficulty_score || 0,
    complexityScore: backendRecipe.complexity_score || 0,
    cuisineType: backendRecipe.cuisine_type as CuisineType,
    rating: backendRecipe.community_rating,
    reviewCount: backendRecipe.review_count || 0,
    favoriteCount: backendRecipe.favorite_count || 0,
    estimatedCost: backendRecipe.estimated_cost || 0,
    servingSize: backendRecipe.serving_size || 0,
    caloriesPerServing: backendRecipe.calories_per_serving,
    status: backendRecipe.status as RecipeStatus,
    createdAt: backendRecipe.created_at,
    updatedAt: backendRecipe.updated_at
  };
}

/**
 * Convert a backend recipe object to a frontend Recipe (full details)
 * @param backendRecipe Backend recipe object
 * @returns Frontend Recipe
 */
export function toRecipe(backendRecipe: any): Recipe {
  // First convert to list item
  const baseRecipe = toRecipeListItem(backendRecipe);
  
  // Parse JSON fields if they're strings
  const ingredients = typeof backendRecipe.ingredients === 'string' 
    ? JSON.parse(backendRecipe.ingredients) 
    : backendRecipe.ingredients;
    
  const instructions = typeof backendRecipe.instructions === 'string'
    ? JSON.parse(backendRecipe.instructions)
    : backendRecipe.instructions;
    
  const equipmentNeeded = backendRecipe.equipment_needed && typeof backendRecipe.equipment_needed === 'string'
    ? JSON.parse(backendRecipe.equipment_needed)
    : backendRecipe.equipment_needed;
    
  const macronutrients = backendRecipe.macronutrients && typeof backendRecipe.macronutrients === 'string'
    ? JSON.parse(backendRecipe.macronutrients)
    : backendRecipe.macronutrients;
    
  const micronutrients = backendRecipe.micronutrients && typeof backendRecipe.micronutrients === 'string'
    ? JSON.parse(backendRecipe.micronutrients)
    : backendRecipe.micronutrients;
    
  const dietaryRestrictions = backendRecipe.dietary_restrictions && typeof backendRecipe.dietary_restrictions === 'string'
    ? JSON.parse(backendRecipe.dietary_restrictions)
    : backendRecipe.dietary_restrictions;
    
  const dietaryPreferences = backendRecipe.dietary_preferences && typeof backendRecipe.dietary_preferences === 'string'
    ? JSON.parse(backendRecipe.dietary_preferences)
    : backendRecipe.dietary_preferences;
  
  // Add full recipe details
  return {
    ...baseRecipe,
    sourceUrl: backendRecipe.source_url,
    dietaryRestrictions,
    dietaryPreferences,
    ingredients,
    instructions,
    equipmentNeeded,
    macronutrients,
    micronutrients,
    seasonalScore: backendRecipe.seasonal_score,
    sustainabilityScore: backendRecipe.sustainability_score,
    aiConfidenceScore: backendRecipe.ai_confidence_score,
    titles: backendRecipe.titles || [],
    categoryAssignments: backendRecipe.category_assignments || [],
    parentRecipeId: backendRecipe.parent_recipe_id ? backendRecipe.parent_recipe_id.toString() : undefined,
    similarityThreshold: backendRecipe.similarity_threshold,
    signature: backendRecipe.signature,
    isDeleted: backendRecipe.is_deleted === 1 || backendRecipe.is_deleted === true,
    deletedAt: backendRecipe.deleted_at
  };
}

/**
 * Calculate a recipe's value score based on multiple factors
 * @param recipe Recipe to calculate value for
 * @returns Value score between 0-100
 */
export function calculateValueScore(recipe: RecipeListItem): number {
  if (!recipe) return 0;
  
  // Base factors with weights
  const factors = {
    rating: { value: recipe.rating || 0, weight: 0.3 },
    costEfficiency: { value: 0, weight: 0.25 },
    timeEfficiency: { value: 0, weight: 0.2 },
    nutritionalValue: { value: 0, weight: 0.15 },
    sustainability: { value: recipe.sustainabilityScore || 0, weight: 0.1 }
  };
  
  // Calculate cost efficiency (lower cost = higher value)
  if (recipe.estimatedCost > 0) {
    // Invert so lower cost = higher value (1-10 scale)
    factors.costEfficiency.value = Math.max(0, 10 - recipe.estimatedCost);
  }
  
  // Calculate time efficiency (faster = higher value, but with diminishing returns)
  if (recipe.totalTime > 0) {
    // Time efficiency on a 0-10 scale, with diminishing returns for very quick recipes
    factors.timeEfficiency.value = 10 * Math.exp(-recipe.totalTime / 120);
  }
  
  // Calculate nutritional value if we have calories
  if (recipe.caloriesPerServing) {
    // Simple heuristic - assume better nutrition for moderate calorie counts
    const optimalCalories = 500; // Assumption for a balanced meal
    const calorieDeviation = Math.abs(recipe.caloriesPerServing - optimalCalories) / optimalCalories;
    factors.nutritionalValue.value = 10 * Math.max(0, 1 - calorieDeviation);
  }
  
  // Calculate weighted average (0-10 scale)
  let totalValue = 0;
  let totalWeight = 0;
  
  for (const factor of Object.values(factors)) {
    totalValue += factor.value * factor.weight;
    totalWeight += factor.weight;
  }
  
  // Normalize to 0-100 scale
  return Math.round((totalValue / totalWeight) * 10);
}
