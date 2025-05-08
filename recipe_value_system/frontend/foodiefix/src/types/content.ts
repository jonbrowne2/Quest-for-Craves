export enum ContentFormatEnum {
  VIDEO = 'VIDEO',
  AUDIO = 'AUDIO',
  TEXT = 'TEXT',
  IMAGE = 'IMAGE'
}

export enum ContentTypeEnum {
  MAKE_WITH_ME = 'MAKE_WITH_ME',
  COMPANION = 'COMPANION',
  COOKBOOK = 'COOKBOOK'
}

export interface TranscriptSegment {
  startTime: number;  // in seconds
  endTime: number;    // in seconds
  text: string;
  speaker?: string;
  isJoke?: boolean;
}

export interface Transcript {
  language: string;
  segments: TranscriptSegment[];
  format: 'srt' | 'vtt' | 'plain';
}

export interface ContentMetadata {
  format: ContentFormatEnum;
  type: ContentTypeEnum;
  duration?: number;
  resolution?: {
    width: number;
    height: number;
  };
  quality?: string;
  language?: string;
  transcripts?: Record<string, Transcript>;  // key is language code
  accessibility?: {
    captions?: boolean;
    audioDescription?: boolean;
  };
}

export interface GenerationConfig {
  preferredDuration?: number;
  quality?: string;
  style?: string;
  voiceType?: string;
  pacing?: 'slow' | 'medium' | 'fast';
  includeAccessibility?: boolean;
  targetLanguages?: string[];
}

export interface ContentJob {
  id: string;
  recipeId: string;
  userId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  format: ContentFormatEnum;
  type: ContentTypeEnum;
  config: GenerationConfig;
  metadata?: ContentMetadata;
  outputUrl?: string;
  error?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ContentGenerationResult {
  jobId: string;
  status: ContentJob['status'];
  outputUrl?: string;
  error?: string;
}
