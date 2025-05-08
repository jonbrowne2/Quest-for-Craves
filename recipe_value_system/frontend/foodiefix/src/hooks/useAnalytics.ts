import { useCallback } from 'react';
import { trackRecipeEvent, RecipeEventType } from '../services/analytics-service';
import { FeatureTrackingService, FeatureCategory } from '../services/feature-tracking';
import { FeedbackService, FeedbackType } from '../services/feedback';
import { Recipe } from '../types/recipe';

/**
 * Hook for tracking analytics, feature usage, and collecting feedback
 * Implements the "Simplicity Through Usage" philosophy
 */
export function useAnalytics(userId: string = 'anonymous') {
  // Track recipe view
  const trackRecipeView = useCallback((recipe: Recipe) => {
    trackRecipeEvent(RecipeEventType.VIEW, {
      recipeId: recipe.id,
      recipeSlug: recipe.slug,
      recipeTitle: recipe.title,
      categoryId: recipe.category?.id,
      categoryName: recipe.category?.name,
      isVariant: !!recipe.parentRecipeId,
      parentRecipeId: recipe.parentRecipeId
    });
  }, []);

  // Track recipe search
  const trackRecipeSearch = useCallback((searchQuery: string, filters?: Record<string, any>) => {
    trackRecipeEvent(RecipeEventType.SEARCH, {
      searchQuery,
      filters
    });
  }, []);

  // Track recipe rating
  const rateRecipe = useCallback((recipeId: string, rating: number, comment?: string) => {
    return FeedbackService.rateRecipe(userId, recipeId, rating, comment);
  }, [userId]);

  // Track feature usage
  const trackFeature = useCallback((
    featureName: string, 
    category: FeatureCategory = FeatureCategory.CORE,
    context: any = {}
  ) => {
    return FeatureTrackingService.trackFeatureUsage(featureName, userId, context, category);
  }, [userId]);

  // Complete feature tracking
  const completeFeature = useCallback((
    trackingId: string,
    success: boolean,
    additionalData: any = {}
  ) => {
    return FeatureTrackingService.completeFeatureUsage(trackingId, success, additionalData);
  }, []);

  // Track feature abandonment
  const abandonFeature = useCallback((
    trackingId: string,
    abandonmentPoint: string,
    additionalData: any = {}
  ) => {
    return FeatureTrackingService.abandonFeatureUsage(trackingId, abandonmentPoint, additionalData);
  }, []);

  // Track feature satisfaction
  const rateFeature = useCallback((
    featureId: string,
    rating: number,
    comment?: string
  ) => {
    return FeedbackService.rateFeature(userId, featureId, rating, comment);
  }, [userId]);

  // Submit NPS rating
  const submitNPS = useCallback((
    rating: number,
    comment?: string
  ) => {
    return FeedbackService.submitNPS(userId, rating, comment);
  }, [userId]);

  // Track recipe cooking
  const trackRecipeCooking = useCallback((recipe: Recipe) => {
    trackRecipeEvent(RecipeEventType.COOK, {
      recipeId: recipe.id,
      recipeSlug: recipe.slug,
      recipeTitle: recipe.title
    });
  }, []);

  // Track recipe sharing
  const trackRecipeSharing = useCallback((recipe: Recipe, platform: string) => {
    trackRecipeEvent(RecipeEventType.SHARE, {
      recipeId: recipe.id,
      recipeSlug: recipe.slug,
      recipeTitle: recipe.title,
      platform
    });
  }, []);

  // Track recipe printing
  const trackRecipePrinting = useCallback((recipe: Recipe) => {
    trackRecipeEvent(RecipeEventType.PRINT, {
      recipeId: recipe.id,
      recipeSlug: recipe.slug,
      recipeTitle: recipe.title
    });
  }, []);

  // Track category view
  const trackCategoryView = useCallback((categoryId: string, categoryName: string) => {
    trackRecipeEvent(RecipeEventType.CATEGORY_VIEW, {
      categoryId,
      categoryName
    });
  }, []);

  // Track variant view
  const trackVariantView = useCallback((recipe: Recipe, parentRecipe: Recipe) => {
    trackRecipeEvent(RecipeEventType.VARIANT_VIEW, {
      recipeId: recipe.id,
      recipeSlug: recipe.slug,
      recipeTitle: recipe.title,
      parentRecipeId: parentRecipe.id,
      parentRecipeSlug: parentRecipe.slug,
      parentRecipeTitle: parentRecipe.title,
      similarityThreshold: recipe.similarityThreshold
    });
  }, []);

  // Track similar recipe click
  const trackSimilarRecipeClick = useCallback((
    sourceRecipeId: string,
    targetRecipeId: string,
    similarityScore?: number
  ) => {
    trackRecipeEvent(RecipeEventType.SIMILAR_RECIPE_CLICK, {
      sourceRecipeId,
      targetRecipeId,
      similarityScore
    });
  }, []);

  return {
    // Recipe tracking
    trackRecipeView,
    trackRecipeSearch,
    rateRecipe,
    trackRecipeCooking,
    trackRecipeSharing,
    trackRecipePrinting,
    trackCategoryView,
    trackVariantView,
    trackSimilarRecipeClick,
    
    // Feature tracking
    trackFeature,
    completeFeature,
    abandonFeature,
    rateFeature,
    
    // General feedback
    submitNPS
  };
}

export default useAnalytics;
