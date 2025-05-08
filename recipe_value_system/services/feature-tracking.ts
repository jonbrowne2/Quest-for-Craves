import { prisma } from '@/lib/prisma';
import { Monitoring } from './monitoring';
import { FeatureCategory, FeatureMetric } from '@prisma/client';

export class FeatureTracking {
  private static readonly ENGAGEMENT_THRESHOLD_LOW = 0.05; // 5%
  private static readonly ENGAGEMENT_THRESHOLD_HIGH = 0.30; // 30%

  static async trackFeatureUsage(
    featureId: string,
    userId: string,
    metadata: Record<string, any> = {}
  ) {
    const startTime = Date.now();
    try {
      await prisma.featureUsage.create({
        data: {
          featureId,
          userId,
          metadata,
          startTime: new Date(),
        },
      });
    } catch (error) {
      Monitoring.trackError(error, { context: 'feature_tracking', featureId });
    }
    return { trackingId: `${featureId}-${startTime}` };
  }

  static async completeFeatureUsage(trackingId: string, success: boolean) {
    const [featureId, startTime] = trackingId.split('-');
    try {
      await prisma.featureUsage.update({
        where: {
          featureId_startTime: {
            featureId,
            startTime: new Date(parseInt(startTime)),
          },
        },
        data: {
          endTime: new Date(),
          completed: success,
        },
      });
    } catch (error) {
      Monitoring.trackError(error, { context: 'feature_tracking', trackingId });
    }
  }

  static async calculateFeatureMetrics(
    featureId: string,
    timeWindow: { days: number } = { days: 30 }
  ) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - timeWindow.days);

    const [usageStats, totalUsers] = await prisma.$transaction([
      prisma.featureUsage.groupBy({
        by: ['userId', 'completed'],
        where: {
          featureId,
          startTime: { gte: startDate },
        },
        _count: true,
      }),
      prisma.user.count(),
    ]);

    const uniqueUsers = new Set(usageStats.map(stat => stat.userId)).size;
    const completedUsage = usageStats.find(stat => stat.completed)?._count ?? 0;
    const abandonedUsage = usageStats.find(stat => !stat.completed)?._count ?? 0;

    const metrics = {
      engagementRate: uniqueUsers / totalUsers,
      completionRate: completedUsage / (completedUsage + abandonedUsage),
      abandonmentRate: abandonedUsage / (completedUsage + abandonedUsage),
    };

    await prisma.featureMetric.create({
      data: {
        featureId,
        metrics,
        calculatedAt: new Date(),
      },
    });

    return metrics;
  }

  static async getFeatureRecommendation(featureId: string): Promise<{
    category: FeatureCategory;
    action: 'REMOVE' | 'ENHANCE' | 'MAINTAIN';
    reason: string;
  }> {
    const metrics = await prisma.featureMetric.findFirst({
      where: { featureId },
      orderBy: { calculatedAt: 'desc' },
    });

    if (!metrics) {
      return {
        category: FeatureCategory.GROWTH,
        action: 'MAINTAIN',
        reason: 'Insufficient data for recommendation',
      };
    }

    const { engagementRate, completionRate, abandonmentRate } = metrics.metrics;

    if (engagementRate < this.ENGAGEMENT_THRESHOLD_LOW) {
      return {
        category: FeatureCategory.LEGACY,
        action: 'REMOVE',
        reason: 'Low engagement rate',
      };
    }

    if (
      engagementRate > this.ENGAGEMENT_THRESHOLD_HIGH &&
      completionRate > 0.7
    ) {
      return {
        category: FeatureCategory.CORE,
        action: 'ENHANCE',
        reason: 'High engagement and completion rates',
      };
    }

    return {
      category: FeatureCategory.GROWTH,
      action: 'MAINTAIN',
      reason: 'Moderate engagement, monitoring required',
    };
  }
}
