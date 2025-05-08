/**
 * Recipe API Route Handler
 * 
 * This module implements the core recipe management API endpoints following REST principles.
 * It provides functionality for creating, reading, and updating recipes with proper validation,
 * caching, and error handling.
 * 
 * @module recipes/route
 */

import { z } from 'zod';
import { prisma } from '@/lib/prisma';
import { handleApiError, ValidationError, DatabaseError } from '@/lib/errors';
import { 
  DifficultyLevelEnum, 
  CuisineTypeEnum, 
  InteractionTypeEnum,
  Recipe,
  Step,
  Ingredient 
} from '@/types/recipe';
import { IAnalyticsJob } from '@/types/analytics';
import { PrismaClient } from '@prisma/client';
import { CacheService } from '@/services/cache';
import { MonitoringService } from '@/services/monitoring';
import { SecurityService } from '@/services/security';
import { FeatureTrackingService } from '@/services/feature-tracking';
import { ContentManagerService } from '@/services/content-manager';
import { FeedbackService } from '@/services/feedback';
import { ExperimentationService } from '@/services/experimentation';
import { ContentGenerationService } from '@/services/content-generation';
import { ContentTypeEnum, ContentFormatEnum } from '@/types/content';

// Type for Prisma transaction client
type TransactionClient = Omit<PrismaClient, '$connect' | '$disconnect' | '$on' | '$transaction' | '$use'>;

// Get analytics instance from DI container
declare const analytics: IAnalyticsJob;

// Recipe validation schema
const recipeSchema = z.object({
  title: z.string().min(3).max(100),
  description: z.string().min(10).max(1000),
  difficulty: z.nativeEnum(DifficultyLevelEnum),
  cuisine: z.nativeEnum(CuisineTypeEnum),
  prepTime: z.number().min(1),
  cookTime: z.number().min(1),
  servings: z.number().min(1),
  ingredients: z.array(z.object({
    name: z.string(),
    amount: z.number(),
    unit: z.string()
  })),
  steps: z.array(z.object({
    instruction: z.string()
  })),
  userId: z.string()
});

type RecipeInput = z.infer<typeof recipeSchema>;
type RecipeUpdate = Partial<RecipeInput>;

// Helper function for response wrapping
function wrapResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify({ data }), {
    status,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Helper function for error wrapping
function wrapError(message: string, status = 400) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Helper function for event tracking
async function trackEvent(
  eventName: string,
  data: Record<string, unknown>,
  metadata: { path: string; method: string }
): Promise<void> {
  await MonitoringService.trackEvent(eventName, data, metadata);
}

/**
 * Helper function for tracking errors consistently across the API
 * @param error - The error to track
 * @param context - Additional context about where the error occurred
 * @returns The tracked error for further handling
 */
async function trackError(error: unknown, context: { path: string; method: string }): Promise<Error> {
  if (error instanceof Error) {
    await MonitoringService.trackError(error, context);
    return error;
  }
  const wrappedError = new Error('Unknown error occurred');
  await MonitoringService.trackError(wrappedError, context);
  return wrappedError;
}

/**
 * Creates a new recipe
 * 
 * @param request - The incoming HTTP request
 * @returns Response with the created recipe or error details
 * 
 * @throws {ValidationError} When recipe data is invalid
 * @throws {DatabaseError} When database operations fail
 * 
 * @example
 * POST /api/recipes
 * {
 *   "title": "Spaghetti Carbonara",
 *   "description": "Classic Italian pasta dish",
 *   "difficulty": "Medium",
 *   "cuisine": "Italian",
 *   "prepTime": 15,
 *   "cookTime": 20,
 *   "servings": 4,
 *   "ingredients": [
 *     { "name": "Spaghetti", "amount": 1, "unit": "pound" }
 *   ],
 *   "steps": [
 *     { "instruction": "Boil the pasta" }
 *   ],
 *   "userId": "user123"
 * }
 */
export async function POST(request: Request) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();
  
  MonitoringService.logRequest({
    id: requestId,
    method: 'POST',
    path: '/recipes',
    timestamp: new Date().toISOString()
  });

  try {
    const validation = await SecurityService.validateRequest(request, { 
      requireAuth: true,
      rateLimit: { window: 60000, max: 10 }
    });
    
    if (!validation.allowed) {
      return wrapError(validation.reason || 'Unauthorized', 401);
    }

    const recipeData: unknown = await request.json();
    const validatedRecipe = await recipeSchema.parseAsync(recipeData);

    const result = await prisma.$transaction(async (tx: TransactionClient) => {
      const savedRecipe = await tx.recipe.create({
        data: {
          ...validatedRecipe,
          interactions: {
            create: {
              type: InteractionTypeEnum.CREATE,
              userId: validatedRecipe.userId
            }
          },
          ingredients: {
            create: validatedRecipe.ingredients
          },
          steps: {
            create: validatedRecipe.steps
          }
        },
        include: {
          ingredients: true,
          steps: true,
          interactions: true
        }
      });

      // Queue content generation jobs
      await Promise.all([
        ContentGenerationService.generateMakeWithMeVideo(savedRecipe, validatedRecipe.userId),
        ContentGenerationService.generateAudioCompanion(savedRecipe, validatedRecipe.userId)
      ]).catch(error => {
        // Log error but don't fail the recipe creation
        MonitoringService.trackError(error, {
          path: '/recipes',
          method: 'POST',
          context: 'content_generation'
        });
      });

      return savedRecipe;
    });

    await CacheService.setRecipe(result.id, result, { ttl: 3600 });
    await CacheService.invalidateRecipeLists();

    await trackEvent('recipe_submission_completed', {
      recipeId: result.id,
      userId: validatedRecipe.userId
    }, { 
      timestamp: new Date().toISOString(),
      source: 'api'
    });
    
    MonitoringService.trackRequest('POST', '/recipes', 201, Date.now() - startTime);
    
    MonitoringService.logResponse({
      id: requestId,
      status: 201,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    return wrapResponse(result, 201);
  } catch (error) {
    const trackedError = await trackError(error, { path: '/recipes', method: 'POST' });
    
    MonitoringService.logResponse({
      id: requestId,
      status: error instanceof ValidationError ? 400 : 500,
      error: trackedError.message,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    if (error instanceof z.ZodError) {
      return wrapError('Invalid recipe data: ' + error.errors.map(e => e.message).join(', '), 422);
    }
    if (error instanceof ValidationError) {
      return wrapError(error.message, 400);
    }
    return handleApiError(trackedError);
  }
}

/**
 * Retrieves recipes, either a single recipe by ID or a paginated list
 * 
 * @param request - The incoming HTTP request
 * @returns Response with the requested recipe(s) or error details
 * 
 * @throws {ValidationError} When recipe is not found or parameters are invalid
 * @throws {DatabaseError} When database operations fail
 * 
 * @example
 * GET /api/recipes?id=recipe123&userId=user123 // Get single recipe
 * GET /api/recipes?userId=user123&page=1&limit=10 // Get recipe list
 */
export async function GET(request: Request) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();
  
  MonitoringService.logRequest({
    id: requestId,
    method: 'GET',
    path: '/recipes',
    timestamp: new Date().toISOString()
  });

  let journey: { id: string } | null = null;
  
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    const userId = searchParams.get('userId');
    
    if (!userId) {
      return wrapError('User ID is required', 400);
    }
    
    const page = parseInt(searchParams.get('page') || '1', 10);
    const limit = parseInt(searchParams.get('limit') || '10', 10);

    journey = await ExperimentationService.startJourney(userId, 'recipe_view', {
      recipeId: id || 'list',
      isDetailView: !!id,
    });

    const validation = await SecurityService.validateRequest(request, {
      requireAuth: true,
      rateLimit: { window: 60000, max: 100 }
    });

    if (!validation.allowed) {
      return wrapError(validation.reason || 'Unauthorized', 401);
    }

    if (id) {
      const tracking = await FeatureTrackingService.trackFeatureUsage('recipe_detail_view', userId, {
        recipeId: id,
      });

      const cachedRecipe = await CacheService.getRecipe(id);
      if (cachedRecipe) {
        MonitoringService.trackCacheHit('recipe');
        await ExperimentationService.recordStep(journey.id, 'cache_hit', true);
        await FeatureTrackingService.completeFeatureUsage(tracking.trackingId, true);
        MonitoringService.logResponse({
          id: requestId,
          status: 200,
          duration: Date.now() - startTime,
          timestamp: new Date().toISOString()
        });
        return wrapResponse(cachedRecipe);
      }

      MonitoringService.trackCacheMiss('recipe');
      await ExperimentationService.recordStep(journey.id, 'cache_miss', true);

      const result = await prisma.$transaction(async (tx: TransactionClient) => {
        const recipe = await tx.recipe.findUnique({
          where: { id },
          include: {
            ingredients: true,
            steps: true,
            interactions: {
              orderBy: { createdAt: 'desc' },
              take: 1,
            },
          },
        });

        if (!recipe) {
          throw new ValidationError('Recipe not found');
        }

        await tx.recipeInteraction.create({
          data: {
            type: InteractionTypeEnum.VIEW,
            userId,
            recipeId: id,
          },
        });

        return recipe;
      });

      if (!result.content?.some(c => c.type === ContentTypeEnum.MAKE_WITH_ME)) {
        // Queue video generation if not already present
        ContentGenerationService.generateMakeWithMeVideo(result, userId).catch(console.error);
      }

      if (!result.content?.some(c => c.type === ContentTypeEnum.COMPANION)) {
        // Queue audio companion if not already present
        ContentGenerationService.generateAudioCompanion(result, userId).catch(console.error);
      }

      await CacheService.setRecipe(id, result, { ttl: 3600 });

      if (!result.content?.some((c: { format: string }) => c.format === 'COMPANION')) {
        ContentManagerService.generateCompanionContent(id).catch(console.error);
      }

      await ExperimentationService.recordStep(journey.id, 'recipe_loaded', true);
      await FeatureTrackingService.completeFeatureUsage(tracking.trackingId, true);

      setTimeout(() => {
        FeedbackService.collectFeedback(userId, id, {
          interactionType: InteractionTypeEnum.VIEW,
          timestamp: new Date().toISOString(),
        }).catch(console.error);
      }, 5000);

      MonitoringService.logResponse({
        id: requestId,
        status: 200,
        duration: Date.now() - startTime,
        timestamp: new Date().toISOString()
      });
      return wrapResponse(result);
    } else {
      const tracking = await FeatureTrackingService.trackFeatureUsage('recipe_list_view', userId, {
        page,
        limit,
      });

      const cachedList = await CacheService.getRecipeList(page, limit);
      if (cachedList) {
        MonitoringService.trackCacheHit('recipe_list');
        await ExperimentationService.recordStep(journey.id, 'cache_hit', true);
        await FeatureTrackingService.completeFeatureUsage(tracking.trackingId, true);
        MonitoringService.logResponse({
          id: requestId,
          status: 200,
          duration: Date.now() - startTime,
          timestamp: new Date().toISOString()
        });
        return wrapResponse(cachedList);
      }

      MonitoringService.trackCacheMiss('recipe_list');
      await ExperimentationService.recordStep(journey.id, 'cache_miss', true);

      const [recipes, total] = await prisma.$transaction([
        prisma.recipe.findMany({
          skip: (page - 1) * limit,
          take: limit,
          orderBy: { createdAt: 'desc' },
          include: {
            ingredients: true,
            steps: true,
            interactions: {
              orderBy: { createdAt: 'desc' },
              take: 1,
            },
          },
        }),
        prisma.recipe.count(),
      ]);

      const result = {
        recipes,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit),
        },
      };

      await CacheService.setRecipeList(page, limit, result);
      await ExperimentationService.recordStep(journey.id, 'list_loaded', true);
      await FeatureTrackingService.completeFeatureUsage(tracking.trackingId, true);

      MonitoringService.logResponse({
        id: requestId,
        status: 200,
        duration: Date.now() - startTime,
        timestamp: new Date().toISOString()
      });
      return wrapResponse(result);
    }
  } catch (error) {
    const trackedError = await trackError(error, { path: '/recipes', method: 'GET' });
    
    MonitoringService.logResponse({
      id: requestId,
      status: error instanceof ValidationError ? 400 : 500,
      error: trackedError.message,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    if (journey) {
      await ExperimentationService.recordStep(journey.id, 'error', false, {
        error: trackedError.message,
      });
    }
    
    if (error instanceof ValidationError) {
      return wrapError(error.message, 400);
    }
    return handleApiError(trackedError);
  } finally {
    if (journey) {
      await ExperimentationService.completeJourney(journey.id, true);
    }
    MonitoringService.trackRequest('GET', '/recipes', 200, Date.now() - startTime);
  }
}

/**
 * Updates an existing recipe
 * 
 * @param request - The incoming HTTP request
 * @returns Response with the updated recipe or error details
 * 
 * @throws {ValidationError} When recipe is not found or data is invalid
 * @throws {DatabaseError} When database operations fail
 * 
 * @example
 * PUT /api/recipes?id=recipe123
 * {
 *   "title": "Updated Spaghetti Carbonara",
 *   "description": "Updated classic Italian pasta dish"
 * }
 */
export async function PUT(request: Request) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();
  
  MonitoringService.logRequest({
    id: requestId,
    method: 'PUT',
    path: '/recipes',
    timestamp: new Date().toISOString()
  });

  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    if (!id) {
      return wrapError('Recipe ID is required', 400);
    }

    const validation = await SecurityService.validateRequest(request, {
      requireAuth: true,
      rateLimit: { window: 60000, max: 10 }
    });

    if (!validation.allowed) {
      return wrapError(validation.reason || 'Unauthorized', 401);
    }

    const updateData: unknown = await request.json();
    const validatedUpdate = await recipeSchema.partial().parseAsync(updateData);

    const recipe = await prisma.$transaction(async (tx: TransactionClient) => {
      const existing = await tx.recipe.findUnique({
        where: { id },
        include: {
          ingredients: true,
          steps: true,
        },
      });

      if (!existing) {
        throw new ValidationError('Recipe not found');
      }

      const updated = await tx.recipe.update({
        where: { id },
        data: {
          ...validatedUpdate,
          interactions: {
            create: {
              type: InteractionTypeEnum.UPDATE,
              userId: validatedUpdate.userId!,
            },
          },
          ...(validatedUpdate.ingredients && {
            ingredients: {
              deleteMany: {},
              create: validatedUpdate.ingredients,
            },
          }),
          ...(validatedUpdate.steps && {
            steps: {
              deleteMany: {},
              create: validatedUpdate.steps,
            },
          }),
        },
        include: {
          ingredients: true,
          steps: true,
          interactions: {
            orderBy: { createdAt: 'desc' },
            take: 1,
          },
        },
      });

      return updated;
    });

    await CacheService.invalidateRecipe(id);
    
    await trackEvent('recipe_update_completed', {
      recipeId: id,
      userId: validatedUpdate.userId
    }, { 
      timestamp: new Date().toISOString(),
      source: 'api'
    });
    
    MonitoringService.trackRequest('PUT', '/recipes', 200, Date.now() - startTime);
    
    MonitoringService.logResponse({
      id: requestId,
      status: 200,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    return wrapResponse(recipe);
  } catch (error) {
    const trackedError = await trackError(error, { path: '/recipes', method: 'PUT' });

    MonitoringService.logResponse({
      id: requestId,
      status: error instanceof ValidationError ? 400 : 500,
      error: trackedError.message,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });
    
    if (error instanceof z.ZodError) {
      return wrapError('Invalid update data: ' + error.errors.map(e => e.message).join(', '), 422);
    }
    if (error instanceof ValidationError) {
      return wrapError(error.message, 400);
    }
    return handleApiError(trackedError);
  }
}
