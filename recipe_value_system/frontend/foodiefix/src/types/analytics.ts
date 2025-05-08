import { Recipe, RecipeInteraction } from '@prisma/client';
import { PlatformType } from './distribution';

export interface IRecipeAnalytics {
    id: string;
    recipeId: string;
    views: number;
    likes: number;
    shares: number;
    comments: number;
    saves: number;
    averageRating: number;
    totalInteractions: number;
    createdAt: Date;
    updatedAt: Date;
}

export interface IAnalyticsJob {
    update_recipe_analytics: (recipe: any) => Promise<void>;
}

export class AnalyticsError extends Error {
    constructor(message: string, public cause?: unknown) {
        super(message);
        this.name = 'AnalyticsError';
    }
}

export interface ContentAnalytics {
  id: string;
  contentId: string;
  platform: PlatformType;
  metrics: {
    views: number;
    likes: number;
    comments: number;
    shares: number;
    watchTime: number;
    averageWatchDuration: number;
    completionRate: number;
    engagement: number;
  };
  demographics?: {
    ageRanges: Record<string, number>;
    genders: Record<string, number>;
    locations: Record<string, number>;
  };
  retention?: {
    graph: Array<{ timestamp: number; viewers: number }>;
    dropOffPoints: Array<{ timestamp: number; dropPercentage: number }>;
  };
  transcriptEngagement?: {
    jokeReactions: Array<{
      timestamp: number;
      text: string;
      positiveReactions: number;
      negativeReactions: number;
    }>;
    mostRewatchedSegments: Array<{
      startTime: number;
      endTime: number;
      replayCount: number;
    }>;
  };
  timeBasedMetrics: Array<{
    timestamp: Date;
    metrics: {
      views: number;
      likes: number;
      comments: number;
      shares: number;
    };
  }>;
  createdAt: Date;
  updatedAt: Date;
}

export interface AnalyticsDashboard {
  overview: {
    totalViews: number;
    totalEngagement: number;
    averageCompletionRate: number;
    totalWatchTime: number;
    platformBreakdown: Record<PlatformType, {
      views: number;
      engagement: number;
    }>;
  };
  contentPerformance: {
    topPerforming: Array<{
      contentId: string;
      title: string;
      platform: PlatformType;
      metrics: ContentAnalytics['metrics'];
    }>;
    underPerforming: Array<{
      contentId: string;
      title: string;
      platform: PlatformType;
      metrics: ContentAnalytics['metrics'];
    }>;
  };
  audienceInsights: {
    peakEngagementTimes: Array<{
      dayOfWeek: number;
      hour: number;
      engagementScore: number;
    }>;
    demographics: {
      aggregate: ContentAnalytics['demographics'];
      trends: Array<{
        date: Date;
        demographics: ContentAnalytics['demographics'];
      }>;
    };
  };
  contentInsights: {
    bestPerformingJokes: Array<{
      text: string;
      positiveReactionRate: number;
      timestamp: number;
      context: string;
    }>;
    engagingSegments: Array<{
      startTime: number;
      endTime: number;
      replayCount: number;
      transcript: string;
    }>;
    dropOffPatterns: Array<{
      timestamp: number;
      dropPercentage: number;
      context: string;
    }>;
  };
  trends: {
    daily: Array<{
      date: Date;
      metrics: ContentAnalytics['metrics'];
    }>;
    weekly: Array<{
      weekStart: Date;
      metrics: ContentAnalytics['metrics'];
    }>;
    monthly: Array<{
      monthStart: Date;
      metrics: ContentAnalytics['metrics'];
    }>;
  };
}
