import { prisma } from '@/lib/prisma';
import { Monitoring } from './monitoring';
import { Recipe, RecipeVersion, Attribution } from '@prisma/client';

export class RecipeVersioning {
  static async createVersion(
    recipeId: string,
    changes: Partial<Recipe>,
    userId: string
  ): Promise<RecipeVersion> {
    return await prisma.$transaction(async (tx) => {
      // Get current recipe
      const currentRecipe = await tx.recipe.findUnique({
        where: { id: recipeId },
        include: {
          ingredients: true,
          instructions: true,
          attribution: true,
        },
      });

      if (!currentRecipe) {
        throw new Error('Recipe not found');
      }

      // Create version record
      const version = await tx.recipeVersion.create({
        data: {
          recipeId,
          versionNumber: {
            increment: 1,
          },
          previousContent: currentRecipe,
          changes,
          changedBy: userId,
          changeReason: changes.changeReason || 'Recipe update',
        },
      });

      // Update recipe with new content
      await tx.recipe.update({
        where: { id: recipeId },
        data: {
          ...changes,
          currentVersion: version.versionNumber,
          lastModified: new Date(),
        },
      });

      return version;
    });
  }

  static async getVersionHistory(
    recipeId: string
  ): Promise<RecipeVersion[]> {
    return await prisma.recipeVersion.findMany({
      where: { recipeId },
      orderBy: { versionNumber: 'desc' },
      include: {
        changedByUser: {
          select: {
            id: true,
            name: true,
          },
        },
      },
    });
  }

  static async revertToVersion(
    recipeId: string,
    versionNumber: number,
    userId: string
  ): Promise<Recipe> {
    return await prisma.$transaction(async (tx) => {
      const version = await tx.recipeVersion.findUnique({
        where: {
          recipeId_versionNumber: {
            recipeId,
            versionNumber,
          },
        },
      });

      if (!version) {
        throw new Error('Version not found');
      }

      // Create new version record for the revert
      await tx.recipeVersion.create({
        data: {
          recipeId,
          versionNumber: {
            increment: 1,
          },
          previousContent: version.previousContent,
          changes: {},
          changedBy: userId,
          changeReason: `Reverted to version ${versionNumber}`,
        },
      });

      // Update recipe with reverted content
      return await tx.recipe.update({
        where: { id: recipeId },
        data: {
          ...version.previousContent,
          lastModified: new Date(),
        },
      });
    });
  }
}

export class AttributionManager {
  static async addAttribution(
    recipeId: string,
    data: Omit<Attribution, 'id' | 'recipeId'>
  ): Promise<Attribution> {
    return await prisma.attribution.create({
      data: {
        ...data,
        recipeId,
        verificationStatus: 'PENDING',
      },
    });
  }

  static async verifyAttribution(
    attributionId: string,
    status: 'VERIFIED' | 'REJECTED',
    verificationNotes?: string
  ): Promise<Attribution> {
    return await prisma.attribution.update({
      where: { id: attributionId },
      data: {
        verificationStatus: status,
        verificationNotes,
        verifiedAt: new Date(),
      },
    });
  }

  static async getAttributions(recipeId: string): Promise<Attribution[]> {
    return await prisma.attribution.findMany({
      where: { recipeId },
      orderBy: { createdAt: 'desc' },
    });
  }

  static async updateAttributionContent(
    attributionId: string,
    updates: Partial<Attribution>
  ): Promise<Attribution> {
    return await prisma.attribution.update({
      where: { id: attributionId },
      data: {
        ...updates,
        verificationStatus: 'PENDING', // Require re-verification after updates
        verifiedAt: null,
      },
    });
  }

  static async trackContentFormat(
    recipeId: string,
    format: 'TEXT' | 'VIDEO' | 'AUDIO' | 'PRINT',
    metadata: Record<string, any>
  ): Promise<void> {
    await prisma.recipeContent.create({
      data: {
        recipeId,
        format,
        metadata,
        status: 'ACTIVE',
      },
    });
  }

  static async getContentFormats(
    recipeId: string
  ): Promise<Array<{ format: string; metadata: Record<string, any> }>> {
    const contents = await prisma.recipeContent.findMany({
      where: {
        recipeId,
        status: 'ACTIVE'
      },
    });
    return contents.map(({ format, metadata }) => ({ format, metadata }));
  }
}
