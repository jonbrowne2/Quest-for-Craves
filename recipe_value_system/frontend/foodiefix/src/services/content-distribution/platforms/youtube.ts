import { google } from 'googleapis';
import { DistributionJob } from '@/types/distribution';
import { MonitoringService } from '@/services/monitoring';

interface TranscriptSegment {
  startTime: number;
  endTime: number;
  text: string;
}

export class YouTubeUploader {
  private youtube;

  constructor(apiKey: string) {
    this.youtube = google.youtube('v3');
  }

  async uploadVideo(
    videoPath: string,
    title: string,
    description: string,
    transcript: TranscriptSegment[],
    tags: string[]
  ): Promise<string> {
    try {
      // Upload video
      const uploadResponse = await this.youtube.videos.insert({
        part: ['snippet', 'status'],
        requestBody: {
          snippet: {
            title,
            description,
            tags,
            categoryId: '22' // People & Blogs
          },
          status: {
            privacyStatus: 'private' // Start as private, can be made public later
          }
        },
        media: {
          body: videoPath
        }
      });

      const videoId = uploadResponse.data.id;
      if (!videoId) {
        throw new Error('Failed to get video ID from upload response');
      }

      // Upload captions
      await this.uploadCaptions(videoId, transcript);

      return videoId;
    } catch (err) {
      if (err instanceof Error) {
        MonitoringService.trackError(err, {
          path: 'youtube-uploader',
          method: 'uploadVideo'
        });
      } else {
        MonitoringService.trackError(new Error('Unknown error occurred'), {
          path: 'youtube-uploader',
          method: 'uploadVideo'
        });
      }
      throw err;
    }
  }

  private async uploadCaptions(
    videoId: string,
    transcript: TranscriptSegment[]
  ): Promise<void> {
    try {
      const captionContent = this.formatTranscriptForCaptions(transcript);

      await this.youtube.captions.insert({
        part: ['snippet'],
        requestBody: {
          snippet: {
            videoId,
            language: 'en',
            name: 'English',
            isDraft: false
          }
        },
        media: {
          body: captionContent
        }
      });
    } catch (err) {
      if (err instanceof Error) {
        MonitoringService.trackError(err, {
          path: 'youtube-uploader',
          method: 'uploadCaptions'
        });
      } else {
        MonitoringService.trackError(new Error('Unknown error occurred'), {
          path: 'youtube-uploader',
          method: 'uploadCaptions'
        });
      }
      throw err;
    }
  }

  private formatTranscriptForCaptions(transcript: TranscriptSegment[]): string {
    return transcript.map((segment, index) => {
      const startTime = this.formatTimestamp(segment.startTime);
      const endTime = this.formatTimestamp(segment.endTime);
      return `${index + 1}\n${startTime} --> ${endTime}\n${segment.text}\n\n`;
    }).join('');
  }

  private formatTimestamp(seconds: number): string {
    const date = new Date(seconds * 1000);
    const hours = date.getUTCHours().toString().padStart(2, '0');
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    const secs = date.getUTCSeconds().toString().padStart(2, '0');
    const ms = date.getUTCMilliseconds().toString().padStart(3, '0');
    return `${hours}:${minutes}:${secs},${ms}`;
  }
}
