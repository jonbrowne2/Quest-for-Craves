import { prisma } from '@/lib/prisma';
import { Monitoring } from './monitoring';
import { FeatureTracking } from './feature-tracking';

export type ExperimentVariant = {
  id: string;
  name: string;
  weight: number;
  config: Record<string, any>;
};

export class ExperimentationService {
  static async createExperiment(
    name: string,
    variants: ExperimentVariant[],
    metadata: {
      hypothesis: string;
      metrics: string[];
      targetSegment?: string;
      duration: number; // days
    }
  ) {
    return await prisma.experiment.create({
      data: {
        name,
        variants,
        status: 'ACTIVE',
        startDate: new Date(),
        endDate: new Date(Date.now() + metadata.duration * 86400000),
        metadata,
      },
    });
  }

  static async assignVariant(
    experimentId: string,
    userId: string
  ): Promise<ExperimentVariant> {
    const experiment = await prisma.experiment.findUnique({
      where: { id: experimentId },
    });

    if (!experiment || experiment.status !== 'ACTIVE') {
      throw new Error('Experiment not active');
    }

    // Check if user already assigned
    const existing = await prisma.experimentAssignment.findUnique({
      where: {
        experimentId_userId: {
          experimentId,
          userId,
        },
      },
    });

    if (existing) {
      return experiment.variants.find(v => v.id === existing.variantId)!;
    }

    // Assign variant based on weights
    const variant = this.selectVariant(experiment.variants);

    await prisma.experimentAssignment.create({
      data: {
        experimentId,
        userId,
        variantId: variant.id,
        assignedAt: new Date(),
      },
    });

    return variant;
  }

  static async trackConversion(
    experimentId: string,
    userId: string,
    metric: string,
    value: number
  ) {
    const assignment = await prisma.experimentAssignment.findUnique({
      where: {
        experimentId_userId: {
          experimentId,
          userId,
        },
      },
    });

    if (!assignment) return;

    await prisma.experimentConversion.create({
      data: {
        experimentId,
        userId,
        variantId: assignment.variantId,
        metric,
        value,
      },
    });
  }

  static async analyzeResults(experimentId: string) {
    const [experiment, conversions, assignments] = await prisma.$transaction([
      prisma.experiment.findUnique({
        where: { id: experimentId },
      }),
      prisma.experimentConversion.findMany({
        where: { experimentId },
      }),
      prisma.experimentAssignment.findMany({
        where: { experimentId },
      }),
    ]);

    if (!experiment) throw new Error('Experiment not found');

    const results = experiment.variants.map(variant => {
      const variantAssignments = assignments.filter(
        a => a.variantId === variant.id
      );
      const variantConversions = conversions.filter(
        c => c.variantId === variant.id
      );

      const metrics = experiment.metadata.metrics.map(metric => {
        const metricConversions = variantConversions.filter(
          c => c.metric === metric
        );
        return {
          name: metric,
          conversionRate:
            metricConversions.length / variantAssignments.length,
          averageValue:
            metricConversions.reduce((sum, c) => sum + c.value, 0) /
            metricConversions.length,
        };
      });

      return {
        variantId: variant.id,
        variantName: variant.name,
        sampleSize: variantAssignments.length,
        metrics,
      };
    });

    // Calculate statistical significance
    const significanceResults = this.calculateSignificance(results);

    // Store results
    await prisma.experimentResult.create({
      data: {
        experimentId,
        results,
        significanceResults,
        calculatedAt: new Date(),
      },
    });

    return {
      results,
      significanceResults,
    };
  }

  private static selectVariant(variants: ExperimentVariant[]): ExperimentVariant {
    const totalWeight = variants.reduce((sum, v) => sum + v.weight, 0);
    let random = Math.random() * totalWeight;

    for (const variant of variants) {
      random -= variant.weight;
      if (random <= 0) return variant;
    }

    return variants[0];
  }

  private static calculateSignificance(results: any[]) {
    // Implement statistical significance calculations
    // (e.g., chi-square test for conversion rates)
    return {
      hasSignificantDifference: true, // Placeholder
      confidenceLevel: 0.95,
      winningVariant: results[0].variantId,
    };
  }
}

export class UserJourneyTracker {
  static async startJourney(
    userId: string,
    journeyType: string,
    metadata: Record<string, any> = {}
  ) {
    return await prisma.userJourney.create({
      data: {
        userId,
        journeyType,
        metadata,
        startTime: new Date(),
        status: 'IN_PROGRESS',
      },
    });
  }

  static async recordStep(
    journeyId: string,
    step: string,
    success: boolean,
    metadata: Record<string, any> = {}
  ) {
    await prisma.journeyStep.create({
      data: {
        journeyId,
        step,
        success,
        metadata,
        timestamp: new Date(),
      },
    });

    // Track feature usage
    const journey = await prisma.userJourney.findUnique({
      where: { id: journeyId },
    });

    if (journey) {
      await FeatureTracking.trackFeatureUsage(step, journey.userId, {
        journeyType: journey.journeyType,
        ...metadata,
      });
    }
  }

  static async completeJourney(
    journeyId: string,
    success: boolean,
    metadata: Record<string, any> = {}
  ) {
    const journey = await prisma.userJourney.update({
      where: { id: journeyId },
      data: {
        status: success ? 'COMPLETED' : 'ABANDONED',
        endTime: new Date(),
        completionMetadata: metadata,
      },
    });

    // Calculate journey metrics
    const steps = await prisma.journeyStep.findMany({
      where: { journeyId },
    });

    const metrics = {
      duration: journey.endTime!.getTime() - journey.startTime.getTime(),
      stepCount: steps.length,
      successRate: steps.filter(s => s.success).length / steps.length,
    };

    // Update journey analytics
    await prisma.journeyAnalytics.create({
      data: {
        journeyType: journey.journeyType,
        metrics,
        timestamp: new Date(),
      },
    });

    return { journey, metrics };
  }

  static async analyzeJourneys(
    journeyType: string,
    timeWindow: { days: number } = { days: 30 }
  ) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - timeWindow.days);

    const journeys = await prisma.userJourney.findMany({
      where: {
        journeyType,
        startTime: { gte: startDate },
      },
      include: {
        steps: true,
      },
    });

    const analysis = {
      totalJourneys: journeys.length,
      completionRate:
        journeys.filter(j => j.status === 'COMPLETED').length / journeys.length,
      averageDuration:
        journeys.reduce(
          (sum, j) =>
            sum + (j.endTime?.getTime() ?? 0) - j.startTime.getTime(),
          0
        ) / journeys.length,
      commonDropoffPoints: this.findDropoffPoints(journeys),
    };

    return analysis;
  }

  private static findDropoffPoints(journeys: any[]) {
    const dropoffs = new Map<string, number>();

    for (const journey of journeys) {
      if (journey.status === 'ABANDONED') {
        const lastStep = journey.steps[journey.steps.length - 1];
        dropoffs.set(
          lastStep.step,
          (dropoffs.get(lastStep.step) || 0) + 1
        );
      }
    }

    return Array.from(dropoffs.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
  }
}
