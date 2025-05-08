import { Recipe } from '@/types/recipe';

export class CacheService {
  private static cache = new Map<string, any>();
  private static listKeys = new Set<string>();

  static async getRecipe(id: string): Promise<Recipe | null> {
    return this.cache.get(`recipe:${id}`) || null;
  }

  static async setRecipe(id: string, recipe: Recipe): Promise<void> {
    this.cache.set(`recipe:${id}`, recipe);
  }

  static async getRecipeList(page: number, limit: number): Promise<any | null> {
    return this.cache.get(`recipe-list:${page}:${limit}`) || null;
  }

  static async setRecipeList(page: number, limit: number, list: any): Promise<void> {
    const key = `recipe-list:${page}:${limit}`;
    this.cache.set(key, list);
    this.listKeys.add(key);
  }

  static async invalidateRecipeLists(): Promise<void> {
    for (const key of this.listKeys) {
      this.cache.delete(key);
    }
    this.listKeys.clear();
  }

  static async invalidateRecipe(id: string): Promise<void> {
    this.cache.delete(`recipe:${id}`);
    await this.invalidateRecipeLists();
  }
}
