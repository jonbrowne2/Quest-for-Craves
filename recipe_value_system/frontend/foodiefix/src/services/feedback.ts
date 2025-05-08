import { trackRecipeValueMetric } from './analytics-service';

// Feedback types
export enum FeedbackType {
  RECIPE_RATING = 'recipe_rating',
  FEATURE_SATISFACTION = 'feature_satisfaction',
  NPS = 'nps',
  GENERAL_FEEDBACK = 'general_feedback',
  BUG_REPORT = 'bug_report',
  FEATURE_REQUEST = 'feature_request'
}

// Feedback data interface
export interface FeedbackData {
  userId: string;
  recipeId?: string;
  featureId?: string;
  rating?: number;
  comment?: string;
  context?: any;
  [key: string]: any;
}

export class FeedbackService {
  // Collect user feedback
  static async collectFeedback(
    userId: string, 
    feedbackType: FeedbackType,
    feedbackData: Omit<FeedbackData, 'userId'>
  ) {
    const feedback: FeedbackData = {
      userId,
      ...feedbackData,
      timestamp: new Date().toISOString()
    };
    
    console.log(`Collecting ${feedbackType} feedback from user: ${userId}`, feedback);
    
    // Send to backend API
    try {
      // In a real implementation, this would send to your API
      // await fetch('/api/feedback', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ type: feedbackType, data: feedback })
      // });
      
      // Track as value metric
      if (feedbackType === FeedbackType.RECIPE_RATING && feedbackData.recipeId) {
        trackRecipeValueMetric('recipe_satisfaction', {
          recipeId: feedbackData.recipeId,
          score: feedbackData.rating,
          feedback: feedbackData.comment,
          userId
        });
      } else if (feedbackType === FeedbackType.FEATURE_SATISFACTION && feedbackData.featureId) {
        trackRecipeValueMetric('feature_satisfaction', {
          featureId: feedbackData.featureId,
          score: feedbackData.rating,
          feedback: feedbackData.comment,
          userId
        });
      } else if (feedbackType === FeedbackType.NPS) {
        trackRecipeValueMetric('nps', {
          score: feedbackData.rating,
          feedback: feedbackData.comment,
          userId
        });
      }
      
      return { success: true, feedbackId: `fb_${Date.now()}` };
    } catch (error) {
      console.error('Error submitting feedback:', error);
      return { success: false, error };
    }
  }

  // Analyze sentiment of text feedback
  static async analyzeSentiment(feedback: string): Promise<number> {
    // In a real implementation, this would use a sentiment analysis service
    // For now, we'll return a simple mock implementation
    if (!feedback) return 0;
    
    const positiveWords = ['good', 'great', 'excellent', 'love', 'amazing', 'delicious', 'tasty', 'wonderful'];
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'disappointing', 'bland', 'poor'];
    
    const feedbackLower = feedback.toLowerCase();
    let score = 0;
    
    positiveWords.forEach(word => {
      if (feedbackLower.includes(word)) score += 1;
    });
    
    negativeWords.forEach(word => {
      if (feedbackLower.includes(word)) score -= 1;
    });
    
    // Normalize to range -1 to 1
    return Math.max(-1, Math.min(1, score / 3));
  }
  
  // Submit recipe rating
  static async rateRecipe(
    userId: string,
    recipeId: string,
    rating: number,
    comment?: string
  ) {
    return this.collectFeedback(userId, FeedbackType.RECIPE_RATING, {
      recipeId,
      rating,
      comment
    });
  }
  
  // Submit feature satisfaction rating
  static async rateFeature(
    userId: string,
    featureId: string,
    rating: number,
    comment?: string
  ) {
    return this.collectFeedback(userId, FeedbackType.FEATURE_SATISFACTION, {
      featureId,
      rating,
      comment
    });
  }
  
  // Submit NPS rating
  static async submitNPS(
    userId: string,
    rating: number,
    comment?: string
  ) {
    return this.collectFeedback(userId, FeedbackType.NPS, {
      rating,
      comment
    });
  }
}
