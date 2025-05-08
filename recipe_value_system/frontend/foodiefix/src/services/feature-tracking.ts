import { trackRecipeFeatureUsage } from './analytics-service';

// Feature categories based on our "Simplicity Through Usage" philosophy
export enum FeatureCategory {
  CORE = 'core',       // Essential features
  GROWTH = 'growth',   // New experiments
  LEGACY = 'legacy',   // Candidates for removal
  PREMIUM = 'premium'  // Paid features
}

// Track feature usage metrics
interface FeatureUsageMetrics {
  timeSpent?: number;
  completionStatus?: 'completed' | 'abandoned';
  abandonmentPoint?: string;
  userSegment?: string;
  userAction?: string;
  [key: string]: any;
}

export class FeatureTrackingService {
  // Track the start of feature usage
  static async trackFeatureUsage(
    feature: string, 
    userId: string, 
    context: any = {},
    category: FeatureCategory = FeatureCategory.CORE
  ) {
    const trackingId = `${feature}_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    const startTime = Date.now();
    
    // Store tracking info in session storage for later completion
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(trackingId, JSON.stringify({
        feature,
        userId,
        startTime,
        category,
        context
      }));
    }
    
    // Log to console in development
    console.log(`Tracking feature: ${feature} (${category}) for user: ${userId}`, context);
    
    // Track via analytics service
    trackRecipeFeatureUsage(feature, {
      userId,
      category,
      action: 'start',
      ...context
    });
    
    return { trackingId, startTime };
  }

  // Complete feature usage tracking
  static async completeFeatureUsage(
    trackingId: string, 
    success: boolean, 
    additionalData: any = {}
  ) {
    let trackingInfo: any = {};
    let timeSpent = 0;
    
    // Retrieve tracking info from session storage
    if (typeof window !== 'undefined') {
      const storedInfo = sessionStorage.getItem(trackingId);
      if (storedInfo) {
        trackingInfo = JSON.parse(storedInfo);
        timeSpent = Date.now() - trackingInfo.startTime;
        sessionStorage.removeItem(trackingId); // Clean up
      }
    }
    
    const { feature, userId, category, context } = trackingInfo;
    
    console.log(`Completing feature tracking ${trackingId} success: ${success}, time spent: ${timeSpent}ms`);
    
    // Track completion via analytics service
    trackRecipeFeatureUsage(feature || 'unknown_feature', {
      userId,
      category,
      action: 'complete',
      timeSpent,
      completed: success,
      completionStatus: success ? 'completed' : 'abandoned',
      ...context,
      ...additionalData
    });
    
    return { timeSpent };
  }
  
  // Track feature abandonment
  static async abandonFeatureUsage(
    trackingId: string, 
    abandonmentPoint: string, 
    additionalData: any = {}
  ) {
    return this.completeFeatureUsage(trackingId, false, {
      abandonmentPoint,
      ...additionalData
    });
  }
  
  // Helper function to simplify tracking in React components
  static useFeatureTracking(feature: string, category: FeatureCategory = FeatureCategory.CORE) {
    // This would be implemented as a React hook in a real application
    // For now, we'll provide a simplified version
    return {
      startTracking: (userId: string, context: any = {}) => 
        this.trackFeatureUsage(feature, userId, context, category),
      
      completeTracking: (trackingId: string, success: boolean, additionalData: any = {}) => 
        this.completeFeatureUsage(trackingId, success, additionalData),
      
      abandonTracking: (trackingId: string, abandonmentPoint: string, additionalData: any = {}) => 
        this.abandonFeatureUsage(trackingId, abandonmentPoint, additionalData)
    };
  }
}

// Simple wrapper function for easier usage
export async function trackFeatureUsage(
  feature: string, 
  context: any = {}, 
  userId: string = 'anonymous'
) {
  return FeatureTrackingService.trackFeatureUsage(feature, userId, context);
}
