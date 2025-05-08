import { prisma } from '@/lib/prisma';
import { Monitoring } from './monitoring';
import { FeatureTracking } from './feature-tracking';

export type FeedbackType = 'NPS' | 'SATISFACTION' | 'FEATURE' | 'CONTENT' | 'RECIPE';

export class FeedbackService {
  static async collectFeedback(data: {
    userId: string;
    type: FeedbackType;
    score: number;
    comment?: string;
    metadata: {
      featureId?: string;
      recipeId?: string;
      contentFormat?: string;
      source?: string;
    };
  }) {
    const feedback = await prisma.feedback.create({
      data: {
        ...data,
        createdAt: new Date(),
      },
    });

    // Track feature usage if applicable
    if (data.metadata.featureId) {
      await FeatureTracking.trackFeatureUsage(data.metadata.featureId, data.userId, {
        feedbackType: data.type,
        score: data.score,
      });
    }

    // Calculate impact on feature metrics
    if (data.type === 'FEATURE' && data.metadata.featureId) {
      await this.updateFeatureMetrics(data.metadata.featureId);
    }

    return feedback;
  }

  static async collectNPS(userId: string, score: number, comment?: string) {
    return this.collectFeedback({
      userId,
      type: 'NPS',
      score,
      comment,
      metadata: { source: 'periodic_survey' },
    });
  }

  static async getFeedbackSummary(params: {
    type?: FeedbackType;
    featureId?: string;
    recipeId?: string;
    timeWindow?: number; // days
  }) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - (params.timeWindow || 30));

    const feedback = await prisma.feedback.findMany({
      where: {
        type: params.type,
        'metadata.featureId': params.featureId,
        'metadata.recipeId': params.recipeId,
        createdAt: { gte: startDate },
      },
    });

    return {
      totalResponses: feedback.length,
      averageScore: feedback.reduce((sum, f) => sum + f.score, 0) / feedback.length,
      distribution: this.calculateScoreDistribution(feedback),
      sentimentAnalysis: await this.analyzeSentiment(feedback),
    };
  }

  static async updateFeatureMetrics(featureId: string) {
    const [feedback, usage] = await prisma.$transaction([
      prisma.feedback.findMany({
        where: {
          type: 'FEATURE',
          'metadata.featureId': featureId,
        },
        orderBy: { createdAt: 'desc' },
        take: 100, // Consider recent feedback
      }),
      prisma.featureUsage.findMany({
        where: {
          featureId,
          endTime: { not: null },
        },
        orderBy: { startTime: 'desc' },
        take: 1000,
      }),
    ]);

    const metrics = {
      satisfactionScore: feedback.reduce((sum, f) => sum + f.score, 0) / feedback.length,
      completionRate: usage.filter(u => u.completed).length / usage.length,
      engagementScore: this.calculateEngagementScore(feedback, usage),
    };

    await prisma.featureMetric.upsert({
      where: { featureId },
      update: { metrics },
      create: {
        featureId,
        metrics,
        calculatedAt: new Date(),
      },
    });

    return metrics;
  }

  private static calculateScoreDistribution(feedback: any[]) {
    const distribution = new Map<number, number>();
    feedback.forEach(f => {
      distribution.set(f.score, (distribution.get(f.score) || 0) + 1);
    });
    return Object.fromEntries(distribution);
  }

  private static async analyzeSentiment(feedback: any[]) {
    const comments = feedback.filter(f => f.comment).map(f => f.comment);
    if (comments.length === 0) return null;

    try {
      // Implement sentiment analysis
      // This could use a service like AWS Comprehend or a local NLP library
      return {
        positive: 0.6,
        negative: 0.2,
        neutral: 0.2,
        commonThemes: ['ease of use', 'recipe quality'],
      };
    } catch (error) {
      Monitoring.trackError(error, { context: 'sentiment_analysis' });
      return null;
    }
  }

  private static calculateEngagementScore(feedback: any[], usage: any[]) {
    const satisfactionWeight = 0.4;
    const usageWeight = 0.3;
    const completionWeight = 0.3;

    const satisfactionScore = feedback.reduce((sum, f) => sum + f.score, 0) / feedback.length;
    const usageScore = Math.min(usage.length / 1000, 1); // Normalize to 0-1
    const completionScore = usage.filter(u => u.completed).length / usage.length;

    return (
      satisfactionScore * satisfactionWeight +
      usageScore * usageWeight +
      completionScore * completionWeight
    );
  }
}
