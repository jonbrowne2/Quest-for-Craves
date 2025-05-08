import Redis from 'ioredis';
import { Recipe } from '@prisma/client';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export class CacheService {
  private static readonly DEFAULT_TTL = 3600; // 1 hour
  private static readonly PREFIX = 'foodiefix:';

  static async get<T>(key: string): Promise<T | null> {
    const data = await redis.get(this.PREFIX + key);
    return data ? JSON.parse(data) : null;
  }

  static async set(key: string, value: any, ttl = this.DEFAULT_TTL): Promise<void> {
    await redis.setex(this.PREFIX + key, ttl, JSON.stringify(value));
  }

  static async del(key: string): Promise<void> {
    await redis.del(this.PREFIX + key);
  }

  static async getRecipe(id: string): Promise<Recipe | null> {
    return this.get<Recipe>(`recipe:${id}`);
  }

  static async setRecipe(recipe: Recipe): Promise<void> {
    await this.set(`recipe:${id}`, recipe);
  }

  static async invalidateRecipe(id: string): Promise<void> {
    await this.del(`recipe:${id}`);
  }

  static async getRecipeList(page: number, limit: number): Promise<{ recipes: Recipe[]; total: number } | null> {
    return this.get<{ recipes: Recipe[]; total: number }>(`recipes:${page}:${limit}`);
  }

  static async setRecipeList(page: number, limit: number, data: { recipes: Recipe[]; total: number }): Promise<void> {
    await this.set(`recipes:${page}:${limit}`, data, 300); // 5 minutes TTL for lists
  }

  static async invalidateRecipeLists(): Promise<void> {
    const keys = await redis.keys(`${this.PREFIX}recipes:*`);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
  }
}
