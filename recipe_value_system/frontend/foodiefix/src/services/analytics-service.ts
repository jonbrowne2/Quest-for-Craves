/**
 * Analytics service for tracking user interactions with recipes
 */

// Event types for recipe interactions
export enum RecipeEventType {
  VIEW = 'recipe_view',
  SEARCH = 'recipe_search',
  FILTER = 'recipe_filter',
  RATE = 'recipe_rate',
  FAVORITE = 'recipe_favorite',
  COOK = 'recipe_cook',
  SHARE = 'recipe_share',
  PRINT = 'recipe_print',
  CATEGORY_VIEW = 'category_view',
  VARIANT_VIEW = 'variant_view',
  SIMILAR_RECIPE_CLICK = 'similar_recipe_click'
}

// Interface for recipe event data
interface RecipeEventData {
  recipeId?: string;
  recipeSlug?: string;
  recipeTitle?: string;
  categoryId?: string;
  categoryName?: string;
  rating?: number;
  searchQuery?: string;
  filters?: Record<string, any>;
  timeSpent?: number;
  completionStatus?: 'completed' | 'abandoned';
  abandonmentPoint?: string;
  userSegment?: string;
  deviceType?: string;
  [key: string]: any;
}

/**
 * Track recipe-related events for analytics
 * @param eventType Type of event
 * @param eventData Event data
 */
export function trackRecipeEvent(eventType: RecipeEventType, eventData: RecipeEventData): void {
  try {
    // Add common metadata
    const enrichedData = {
      ...eventData,
      timestamp: new Date().toISOString(),
      deviceType: getDeviceType(),
      sessionId: getSessionId()
    };

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Analytics] ${eventType}:`, enrichedData);
    }

    // Send to analytics endpoint
    sendAnalyticsEvent(eventType, enrichedData);
    
  } catch (error) {
    console.error('Error tracking recipe event:', error);
  }
}

/**
 * Track recipe feature usage metrics
 * @param featureName Name of the feature
 * @param usageData Usage data
 */
export function trackRecipeFeatureUsage(
  featureName: string, 
  usageData: { 
    timeSpent?: number, 
    completed?: boolean,
    userAction?: string,
    [key: string]: any 
  }
): void {
  try {
    const eventData = {
      feature: featureName,
      ...usageData,
      timestamp: new Date().toISOString()
    };

    // Send to feature tracking endpoint
    sendFeatureUsageData(featureName, eventData);
    
  } catch (error) {
    console.error('Error tracking feature usage:', error);
  }
}

/**
 * Track recipe value metrics
 * @param metricName Name of the metric
 * @param metricData Metric data
 */
export function trackRecipeValueMetric(
  metricName: string,
  metricData: {
    recipeId?: string,
    score?: number,
    feedback?: string,
    [key: string]: any
  }
): void {
  try {
    const eventData = {
      metric: metricName,
      ...metricData,
      timestamp: new Date().toISOString()
    };

    // Send to value metrics endpoint
    sendValueMetricData(metricName, eventData);
    
  } catch (error) {
    console.error('Error tracking value metric:', error);
  }
}

// Helper functions
function getDeviceType(): string {
  // Simple device detection
  const userAgent = typeof window !== 'undefined' ? window.navigator.userAgent : '';
  if (/mobile/i.test(userAgent)) return 'mobile';
  if (/tablet/i.test(userAgent)) return 'tablet';
  return 'desktop';
}

function getSessionId(): string {
  // Get or create session ID
  if (typeof window === 'undefined') return 'server';
  
  let sessionId = sessionStorage.getItem('foodiefix_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    sessionStorage.setItem('foodiefix_session_id', sessionId);
  }
  return sessionId;
}

// API communication functions
async function sendAnalyticsEvent(eventType: string, eventData: any): Promise<void> {
  // In a real implementation, this would send data to your analytics service
  const endpoint = '/api/analytics/events';
  
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        eventType,
        eventData
      }),
    });
  } catch (error) {
    console.error('Failed to send analytics event:', error);
  }
}

async function sendFeatureUsageData(featureName: string, usageData: any): Promise<void> {
  const endpoint = '/api/analytics/feature-usage';
  
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        feature: featureName,
        data: usageData
      }),
    });
  } catch (error) {
    console.error('Failed to send feature usage data:', error);
  }
}

async function sendValueMetricData(metricName: string, metricData: any): Promise<void> {
  const endpoint = '/api/analytics/value-metrics';
  
  try {
    await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        metric: metricName,
        data: metricData
      }),
    });
  } catch (error) {
    console.error('Failed to send value metric data:', error);
  }
}
