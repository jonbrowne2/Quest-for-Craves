import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { POST, GET, PUT } from '../route';
import { prisma } from '@/lib/prisma';
import { CacheService } from '@/services/cache';
import { SecurityService } from '@/services/security';
import { MonitoringService } from '@/services/monitoring';
import { ExperimentationService } from '@/services/experimentation';
import { DifficultyLevelEnum, CuisineTypeEnum } from '@/types/recipe';

// Mock services
vi.mock('@/lib/prisma', () => ({
  prisma: {
    recipe: {
      create: vi.fn(),
      findUnique: vi.fn(),
      findMany: vi.fn(),
      update: vi.fn(),
      count: vi.fn(),
    },
    recipeInteraction: {
      create: vi.fn(),
    },
    $transaction: vi.fn((callback) => callback(prisma)),
  },
}));

vi.mock('@/services/cache');
vi.mock('@/services/security');
vi.mock('@/services/monitoring');
vi.mock('@/services/experimentation');

describe('Recipe API Routes', () => {
  const mockRecipe = {
    title: 'Test Recipe',
    description: 'A test recipe description',
    difficulty: DifficultyLevelEnum.Easy,
    cuisine: CuisineTypeEnum.Italian,
    prepTime: 30,
    cookTime: 45,
    servings: 4,
    ingredients: [
      { name: 'Test Ingredient', amount: 1, unit: 'cup' }
    ],
    steps: [
      { instruction: 'Test instruction' }
    ],
    userId: 'test-user-id'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Setup default mocks
    vi.mocked(SecurityService.validateRequest).mockResolvedValue({ allowed: true });
    vi.mocked(CacheService.getRecipe).mockResolvedValue(null);
    vi.mocked(CacheService.getRecipeList).mockResolvedValue(null);
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('POST /recipes', () => {
    it('should create a new recipe successfully', async () => {
      const request = new Request('http://localhost:3000/api/recipes', {
        method: 'POST',
        body: JSON.stringify(mockRecipe),
      });

      vi.mocked(prisma.recipe.create).mockResolvedValueOnce({
        ...mockRecipe,
        id: 'test-recipe-id',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(201);
      expect(data.success).toBe(true);
      expect(data.data).toMatchObject({
        id: 'test-recipe-id',
        title: mockRecipe.title,
      });
    });

    it('should return 401 when unauthorized', async () => {
      const request = new Request('http://localhost:3000/api/recipes', {
        method: 'POST',
        body: JSON.stringify(mockRecipe),
      });

      vi.mocked(SecurityService.validateRequest).mockResolvedValueOnce({
        allowed: false,
        reason: 'Unauthorized',
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(401);
      expect(data.success).toBe(false);
      expect(data.error).toBe('Unauthorized');
    });
  });

  describe('GET /recipes', () => {
    it('should get a single recipe by id', async () => {
      const request = new Request(
        'http://localhost:3000/api/recipes?id=test-recipe-id&userId=test-user-id'
      );

      vi.mocked(prisma.recipe.findUnique).mockResolvedValueOnce({
        ...mockRecipe,
        id: 'test-recipe-id',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data).toMatchObject({
        id: 'test-recipe-id',
        title: mockRecipe.title,
      });
    });

    it('should get a list of recipes', async () => {
      const request = new Request(
        'http://localhost:3000/api/recipes?userId=test-user-id'
      );

      vi.mocked(prisma.recipe.findMany).mockResolvedValueOnce([
        {
          ...mockRecipe,
          id: 'test-recipe-id-1',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ]);
      vi.mocked(prisma.recipe.count).mockResolvedValueOnce(1);

      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data.recipes).toHaveLength(1);
      expect(data.data.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: 1,
        totalPages: 1,
      });
    });
  });

  describe('PUT /recipes', () => {
    it('should update a recipe successfully', async () => {
      const request = new Request(
        'http://localhost:3000/api/recipes?id=test-recipe-id',
        {
          method: 'PUT',
          body: JSON.stringify({ title: 'Updated Recipe' }),
        }
      );

      vi.mocked(prisma.recipe.findUnique).mockResolvedValueOnce({
        ...mockRecipe,
        id: 'test-recipe-id',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      vi.mocked(prisma.recipe.update).mockResolvedValueOnce({
        ...mockRecipe,
        id: 'test-recipe-id',
        title: 'Updated Recipe',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      const response = await PUT(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data).toMatchObject({
        id: 'test-recipe-id',
        title: 'Updated Recipe',
      });
    });
  });
});
