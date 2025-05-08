import { prisma } from '@/lib/prisma';
import { MonitoringService } from '@/services/monitoring';
import { FeatureTrackingService } from '@/services/feature-tracking';
import { ContentAnalytics, AnalyticsDashboard } from '@/types/analytics';
import { PlatformType } from '@/types/distribution';

export class ContentAnalyticsService {
  /**
   * Updates analytics for a piece of content across all platforms
   */
  static async updateContentAnalytics(contentId: string): Promise<void> {
    const platforms = await prisma.distributionJob.findMany({
      where: { contentJobId: contentId }
    });

    await Promise.all(
      platforms.map(platform => this.updatePlatformAnalytics(contentId, platform.platform as PlatformType))
    );
  }

  /**
   * Gets analytics dashboard data
   */
  static async getDashboard(
    timeRange: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<AnalyticsDashboard> {
    const startDate = this.getStartDate(timeRange);
    
    const analytics = await prisma.contentAnalytics.findMany({
      where: {
        createdAt: {
          gte: startDate
        }
      },
      include: {
        content: true
      }
    });

    return {
      overview: this.calculateOverview(analytics),
      contentPerformance: this.analyzeContentPerformance(analytics),
      audienceInsights: await this.getAudienceInsights(analytics),
      contentInsights: await this.getContentInsights(analytics),
      trends: await this.analyzeTrends(analytics)
    };
  }

  /**
   * Gets detailed analytics for a specific piece of content
   */
  static async getContentDetails(contentId: string): Promise<ContentAnalytics[]> {
    return prisma.contentAnalytics.findMany({
      where: { contentId }
    });
  }

  private static async updatePlatformAnalytics(
    contentId: string,
    platform: PlatformType
  ): Promise<void> {
    try {
      const metrics = await this.fetchPlatformMetrics(contentId, platform);
      
      await prisma.contentAnalytics.upsert({
        where: {
          contentId_platform: {
            contentId,
            platform
          }
        },
        update: {
          metrics,
          updatedAt: new Date()
        },
        create: {
          contentId,
          platform,
          metrics,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      });
    } catch (err) {
      if (err instanceof Error) {
        MonitoringService.trackError(err, {
          path: 'content-analytics',
          method: 'updatePlatformAnalytics'
        });
      } else {
        MonitoringService.trackError(new Error('Unknown error occurred'), {
          path: 'content-analytics',
          method: 'updatePlatformAnalytics'
        });
      }
      throw err;
    }
  }

  private static async fetchPlatformMetrics(
    contentId: string,
    platform: PlatformType
  ): Promise<ContentAnalytics['metrics']> {
    // TODO: Implement platform-specific API calls to fetch metrics
    // This would integrate with YouTube Analytics API, TikTok Analytics API, etc.
    return {
      views: 0,
      likes: 0,
      comments: 0,
      shares: 0,
      watchTime: 0,
      averageWatchDuration: 0,
      completionRate: 0,
      engagement: 0
    };
  }

  private static calculateOverview(
    analytics: ContentAnalytics[]
  ): AnalyticsDashboard['overview'] {
    const platformBreakdown: Record<PlatformType, { views: number; engagement: number }> = 
      Object.values(PlatformType).reduce((acc, platform) => ({
        ...acc,
        [platform]: { views: 0, engagement: 0 }
      }), {} as Record<PlatformType, { views: number; engagement: number }>);

    let totalViews = 0;
    let totalEngagement = 0;
    let totalWatchTime = 0;
    let completionRates = 0;

    analytics.forEach(analytic => {
      totalViews += analytic.metrics.views;
      totalEngagement += analytic.metrics.engagement;
      totalWatchTime += analytic.metrics.watchTime;
      completionRates += analytic.metrics.completionRate;

      platformBreakdown[analytic.platform].views += analytic.metrics.views;
      platformBreakdown[analytic.platform].engagement += analytic.metrics.engagement;
    });

    return {
      totalViews,
      totalEngagement,
      averageCompletionRate: completionRates / analytics.length,
      totalWatchTime,
      platformBreakdown
    };
  }

  private static analyzeContentPerformance(
    analytics: ContentAnalytics[]
  ): AnalyticsDashboard['contentPerformance'] {
    const sorted = [...analytics].sort(
      (a, b) => b.metrics.engagement - a.metrics.engagement
    );

    return {
      topPerforming: sorted.slice(0, 5).map(a => ({
        contentId: a.contentId,
        title: 'TODO: Get title', // TODO: Include content title in query
        platform: a.platform,
        metrics: a.metrics
      })),
      underPerforming: sorted.slice(-5).map(a => ({
        contentId: a.contentId,
        title: 'TODO: Get title', // TODO: Include content title in query
        platform: a.platform,
        metrics: a.metrics
      }))
    };
  }

  private static async getAudienceInsights(
    analytics: ContentAnalytics[]
  ): Promise<AnalyticsDashboard['audienceInsights']> {
    // Aggregate demographics across all content
    const demographics = analytics.reduce(
      (acc, curr) => {
        if (!curr.demographics) return acc;
        
        Object.entries(curr.demographics.ageRanges || {}).forEach(([range, count]) => {
          if (!acc.aggregate.ageRanges[range]) {
            acc.aggregate.ageRanges[range] = 0;
          }
          acc.aggregate.ageRanges[range] += count;
        });

        Object.entries(curr.demographics.genders || {}).forEach(([gender, count]) => {
          if (!acc.aggregate.genders[gender]) {
            acc.aggregate.genders[gender] = 0;
          }
          acc.aggregate.genders[gender] += count;
        });

        Object.entries(curr.demographics.locations || {}).forEach(([location, count]) => {
          if (!acc.aggregate.locations[location]) {
            acc.aggregate.locations[location] = 0;
          }
          acc.aggregate.locations[location] += count;
        });

        return acc;
      },
      {
        aggregate: {
          ageRanges: {} as Record<string, number>,
          genders: {} as Record<string, number>,
          locations: {} as Record<string, number>
        },
        trends: []
      }
    );

    // Calculate peak engagement times
    const engagementByTime = analytics.reduce((acc, curr) => {
      curr.timeBasedMetrics.forEach(metric => {
        const hour = metric.timestamp.getHours();
        const day = metric.timestamp.getDay();
        const key = `${day}-${hour}`;
        
        if (!acc[key]) {
          acc[key] = {
            dayOfWeek: day,
            hour,
            engagementScore: 0
          };
        }
        
        acc[key].engagementScore += metric.metrics.engagement;
      });
      return acc;
    }, {} as Record<string, { dayOfWeek: number; hour: number; engagementScore: number }>);

    return {
      peakEngagementTimes: Object.values(engagementByTime)
        .sort((a, b) => b.engagementScore - a.engagementScore)
        .slice(0, 10),
      demographics
    };
  }

  private static async getContentInsights(
    analytics: ContentAnalytics[]
  ): Promise<AnalyticsDashboard['contentInsights']> {
    const jokes = analytics
      .flatMap(a => a.transcriptEngagement?.jokeReactions || [])
      .sort((a, b) => b.positiveReactions - a.positiveReactions);

    const segments = analytics
      .flatMap(a => a.transcriptEngagement?.mostRewatchedSegments || [])
      .sort((a, b) => b.replayCount - a.replayCount);

    const dropoffs = analytics
      .flatMap(a => a.retention?.dropOffPoints || [])
      .sort((a, b) => b.dropPercentage - a.dropPercentage);

    return {
      bestPerformingJokes: jokes.slice(0, 10).map(joke => ({
        text: joke.text,
        positiveReactionRate: joke.positiveReactions / (joke.positiveReactions + joke.negativeReactions),
        timestamp: joke.timestamp,
        context: 'TODO: Get context' // TODO: Get surrounding transcript
      })),
      engagingSegments: segments.slice(0, 10).map(segment => ({
        startTime: segment.startTime,
        endTime: segment.endTime,
        replayCount: segment.replayCount,
        transcript: 'TODO: Get transcript' // TODO: Get segment transcript
      })),
      dropOffPatterns: dropoffs.slice(0, 10).map(dropoff => ({
        timestamp: dropoff.timestamp,
        dropPercentage: dropoff.dropPercentage,
        context: 'TODO: Get context' // TODO: Get context from transcript
      }))
    };
  }

  private static async analyzeTrends(
    analytics: ContentAnalytics[]
  ): Promise<AnalyticsDashboard['trends']> {
    const daily: Record<string, ContentAnalytics['metrics']> = {};
    const weekly: Record<string, ContentAnalytics['metrics']> = {};
    const monthly: Record<string, ContentAnalytics['metrics']> = {};

    analytics.forEach(analytic => {
      analytic.timeBasedMetrics.forEach(metric => {
        const date = metric.timestamp.toISOString().split('T')[0];
        const week = this.getWeekStart(metric.timestamp).toISOString().split('T')[0];
        const month = this.getMonthStart(metric.timestamp).toISOString().split('T')[0];

        [daily[date], weekly[week], monthly[month]].forEach(period => {
          if (!period) {
            period = {
              views: 0,
              likes: 0,
              comments: 0,
              shares: 0,
              watchTime: 0,
              averageWatchDuration: 0,
              completionRate: 0,
              engagement: 0
            };
          }

          period.views += metric.metrics.views;
          period.likes += metric.metrics.likes;
          period.comments += metric.metrics.comments;
          period.shares += metric.metrics.shares;
        });
      });
    });

    return {
      daily: Object.entries(daily).map(([date, metrics]) => ({
        date: new Date(date),
        metrics
      })),
      weekly: Object.entries(weekly).map(([date, metrics]) => ({
        weekStart: new Date(date),
        metrics
      })),
      monthly: Object.entries(monthly).map(([date, metrics]) => ({
        monthStart: new Date(date),
        metrics
      }))
    };
  }

  private static getStartDate(timeRange: 'day' | 'week' | 'month' | 'year'): Date {
    const now = new Date();
    switch (timeRange) {
      case 'day':
        return new Date(now.setDate(now.getDate() - 1));
      case 'week':
        return new Date(now.setDate(now.getDate() - 7));
      case 'month':
        return new Date(now.setMonth(now.getMonth() - 1));
      case 'year':
        return new Date(now.setFullYear(now.getFullYear() - 1));
    }
  }

  private static getWeekStart(date: Date): Date {
    const d = new Date(date);
    d.setDate(d.getDate() - d.getDay());
    return d;
  }

  private static getMonthStart(date: Date): Date {
    const d = new Date(date);
    d.setDate(1);
    return d;
  }
}
