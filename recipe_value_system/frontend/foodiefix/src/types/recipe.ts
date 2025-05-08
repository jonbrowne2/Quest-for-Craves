// Recipe status
export enum RecipeStatusEnum {
  Draft = 'Draft',
  Published = 'Published',
  Verified = 'Verified',
  Excellent = 'Excellent',
  Legendary = 'Legendary'
}
export type RecipeStatus = keyof typeof RecipeStatusEnum;

// Recipe difficulty levels
export enum DifficultyLevelEnum {
  Easy = 'Easy',
  Medium = 'Medium',
  Advanced = 'Advanced'
}
export type DifficultyLevel = keyof typeof DifficultyLevelEnum;

// Cuisine types
export enum CuisineTypeEnum {
  Italian = 'Italian',
  Chinese = 'Chinese',
  Indian = 'Indian',
  Mexican = 'Mexican',
  Japanese = 'Japanese',
  Thai = 'Thai',
  Vietnamese = 'Vietnamese',
  French = 'French',
  Mediterranean = 'Mediterranean',
  Greek = 'Greek',
  Spanish = 'Spanish',
  Korean = 'Korean',
  MiddleEastern = 'Middle Eastern',
  Brazilian = 'Brazilian',
  Caribbean = 'Caribbean',
  Moroccan = 'Moroccan',
  Filipino = 'Filipino',
  Malay = 'Malay',
  Singaporean = 'Singaporean',
  Indonesian = 'Indonesian',
  Polynesian = 'Polynesian',
  Nordic = 'Nordic',
  German = 'German',
  American = 'American',
  Other = 'Other'
}
export type CuisineType = keyof typeof CuisineTypeEnum;

// Dietary restrictions
export enum DietaryRestrictionEnum {
  Vegan = 'Vegan',
  Vegetarian = 'Vegetarian',
  GlutenFree = 'Gluten-Free',
  DairyFree = 'Dairy-Free',
  NutFree = 'Nut-Free',
  SoyFree = 'Soy-Free',
  EggFree = 'Egg-Free',
  ShellfishFree = 'Shellfish-Free',
  FishFree = 'Fish-Free',
  PorkFree = 'Pork-Free',
  BeefFree = 'Beef-Free',
  Halal = 'Halal',
  Kosher = 'Kosher'
}
export type DietaryRestriction = keyof typeof DietaryRestrictionEnum;

// Dietary preferences
export enum DietaryPreferenceEnum {
  HighProtein = 'High Protein',
  LowCalorie = 'Low Calorie',
  MuscleGain = 'Muscle Gain',
  WeightLoss = 'Weight Loss',
  DiabeticFriendly = 'Diabetic Friendly',
  HeartHealthy = 'Heart Healthy'
}
export type DietaryPreference = keyof typeof DietaryPreferenceEnum;

// Interaction types
export enum InteractionTypeEnum {
  CREATE = 'CREATE',
  UPDATE = 'UPDATE',
  VIEW = 'VIEW',
  LIKE = 'LIKE',
  SAVE = 'SAVE',
  SHARE = 'SHARE',
  COMMENT = 'COMMENT'
}
export type InteractionType = keyof typeof InteractionTypeEnum;

// Recipe ingredient with measurements
export interface Ingredient {
  name: string;
  amount: number;
  unit: string;
  notes?: string;
}

// Recipe step with detailed instructions
export interface Step {
  instruction: string;
}

// Recipe title with language
export interface RecipeTitle {
  title: string;
  isPrimary: boolean;
  languageCode: string;
}

// Recipe category
export interface RecipeCategory {
  id: string;
  name: string;
  description?: string;
  parentCategoryId?: string;
}

// Recipe category assignment
export interface RecipeCategoryAssignment {
  categoryId: string;
  categoryName: string;
  isPrimary: boolean;
  confidenceScore: number;
}

// Recipe signature
export interface RecipeSignature {
  keyIngredients: {
    required: string[];
    proportions?: Record<string, number>;
  };
  methodSignature: string[];
  textureProfile?: Record<string, string>;
  timingProfile?: Record<string, { min: number; max: number }>;
  confidenceScore: number;
}

// Nutritional information
export interface NutritionalInfo {
  protein?: number;
  carbohydrates?: number;
  fat?: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
  cholesterol?: number;
  calories?: number;
}

// Recipe list item (card view)
export interface RecipeListItem {
  id: string;
  title: string;
  slug: string;
  imageUrl?: string;
  prepTime: number;
  cookTime: number;
  totalTime: number;
  difficultyScore: number;
  complexityScore: number;
  cuisineType?: CuisineType;
  rating?: number;
  reviewCount: number;
  favoriteCount: number;
  estimatedCost: number;
  servingSize: number;
  caloriesPerServing?: number;
  status: RecipeStatus;
  createdAt: string;
  updatedAt?: string;
}

// Complete recipe details
export interface Recipe extends RecipeListItem {
  sourceUrl?: string;
  dietaryRestrictions?: DietaryRestriction[];
  dietaryPreferences?: Record<string, any>;
  ingredients: Ingredient[];
  instructions: string[];
  equipmentNeeded?: string[];
  macronutrients?: NutritionalInfo;
  micronutrients?: Record<string, any>;
  seasonalScore?: number;
  sustainabilityScore?: number;
  aiConfidenceScore?: number;
  titles: RecipeTitle[];
  categoryAssignments: RecipeCategoryAssignment[];
  parentRecipeId?: string;
  similarityThreshold?: number;
  signature?: RecipeSignature;
  isDeleted: boolean;
  deletedAt?: string;
}

// Recipe filters
export interface RecipeFilters {
  sortBy?: 'rating' | 'newest' | 'popular' | 'valueScore' | 'cost' | 'time' | 'difficulty';
  difficulty?: number;
  cuisine?: CuisineType;
  minRating?: number;
  maxCost?: number;
  maxTime?: number;
  dietaryRestrictions?: DietaryRestriction[];
  dietaryPreferences?: DietaryPreference[];
  categoryId?: string;
  searchQuery?: string;
}
