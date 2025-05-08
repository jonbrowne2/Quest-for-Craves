export enum PlatformType {
  YOUTUBE = 'YOUTUBE',
  TIKTOK = 'TIKTOK',
  INSTAGRAM = 'INSTAGRAM',
  FACEBOOK = 'FACEBOOK',
  PINTEREST = 'PINTEREST',
  SPOTIFY = 'SPOTIFY',
  APPLE_PODCASTS = 'APPLE_PODCASTS',
  GOOGLE_PODCASTS = 'GOOGLE_PODCASTS'
}

export enum ContentTone {
  FRIENDLY = 'FRIENDLY',
  HUMOROUS = 'HUMOROUS',
  PROFESSIONAL = 'PROFESSIONAL',
  EDUCATIONAL = 'EDUCATIONAL'
}

export enum JokeCategory {
  COOKING_PUNS = 'COOKING_PUNS',
  FOOD_WORDPLAY = 'FOOD_WORDPLAY',
  KITCHEN_MISHAPS = 'KITCHEN_MISHAPS',
  INGREDIENT_JOKES = 'INGREDIENT_JOKES'
}

export interface VoiceoverStyle {
  tone: ContentTone;
  pace: 'slow' | 'medium' | 'fast';
  personality: {
    friendly: number; // 0-1
    enthusiastic: number; // 0-1
    humorous: number; // 0-1
  };
  humorSettings: {
    frequency: 'low' | 'medium' | 'high';
    categories: JokeCategory[];
    familyFriendly: boolean;
  };
}

export interface PlatformConfig {
  platform: PlatformType;
  enabled: boolean;
  credentials?: {
    apiKey?: string;
    apiSecret?: string;
    accessToken?: string;
    refreshToken?: string;
  };
  formatting: {
    aspectRatio?: string;
    maxDuration?: number;
    maxFileSize?: number;
    preferredFormat?: string;
  };
  posting: {
    schedule?: {
      frequency: 'daily' | 'weekly' | 'monthly';
      preferredTime?: string;
      timezone?: string;
    };
    hashtags?: string[];
    description?: {
      template: string;
      maxLength: number;
    };
  };
}

export interface DistributionJob {
  id: string;
  contentJobId: string;
  platform: PlatformType;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  postUrl?: string;
  error?: string;
  analytics?: {
    views: number;
    likes: number;
    comments: number;
    shares: number;
    engagement: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface ContentDistributionResult {
  jobId: string;
  platform: PlatformType;
  status: DistributionJob['status'];
  postUrl?: string;
  error?: string;
}
