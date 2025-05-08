import { Recipe } from '@/types/recipe';
import { MonitoringService } from '@/services/monitoring';
import { prisma } from '@/lib/prisma';

interface RecipeSource {
  url: string;
  siteName: string;
  author?: string;
  license?: string;
}

export class RecipeImportService {
  /**
   * Import a recipe from a URL while maintaining proper attribution
   */
  static async importFromUrl(url: string, userId: string): Promise<Recipe> {
    try {
      // 1. Extract recipe data
      const recipeData = await this.extractRecipeData(url);
      
      // 2. Create recipe with attribution
      const recipe = await prisma.recipe.create({
        data: {
          ...recipeData.recipe,
          userId,
          source: {
            create: {
              url: recipeData.source.url,
              siteName: recipeData.source.siteName,
              author: recipeData.source.author,
              license: recipeData.source.license,
              importedAt: new Date()
            }
          }
        }
      });

      await MonitoringService.trackEvent('recipe_imported', {
        recipeId: recipe.id,
        sourceUrl: url
      }, {
        path: 'recipe-import',
        method: 'importFromUrl'
      });

      return recipe;
    } catch (err) {
      if (err instanceof Error) {
        MonitoringService.trackError(err, {
          path: 'recipe-import',
          method: 'importFromUrl'
        });
      }
      throw err;
    }
  }

  /**
   * Import multiple recipes from URLs
   */
  static async importBatch(
    urls: string[],
    userId: string,
    options: {
      continueOnError?: boolean;
      progressCallback?: (current: number, total: number) => void;
    } = {}
  ): Promise<{
    successful: Recipe[];
    failed: { url: string; error: string }[];
  }> {
    const results = {
      successful: [] as Recipe[],
      failed: [] as { url: string; error: string }[]
    };

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      try {
        const recipe = await this.importFromUrl(url, userId);
        results.successful.push(recipe);
      } catch (err) {
        results.failed.push({
          url,
          error: err instanceof Error ? err.message : 'Unknown error'
        });
        if (!options.continueOnError) {
          break;
        }
      }

      options.progressCallback?.(i + 1, urls.length);
    }

    return results;
  }

  private static async extractRecipeData(url: string): Promise<{
    recipe: Omit<Recipe, 'id' | 'userId' | 'createdAt' | 'updatedAt'>;
    source: RecipeSource;
  }> {
    // TODO: Implement recipe extraction based on site
    // This would use site-specific extractors or a general recipe schema extractor
    throw new Error('Recipe extraction not yet implemented');
  }
}
