export interface MonitoringMetadata {
  path: string;
  method: string;
  timestamp?: string;
  context?: Record<string, unknown>;
}

export class MonitoringService {
  static async trackError(error: Error, metadata: MonitoringMetadata): Promise<void> {
    console.error('Error:', {
      error: error.message,
      stack: error.stack,
      ...metadata,
      timestamp: new Date().toISOString()
    });
  }

  static async logRequest(metadata: MonitoringMetadata): Promise<void> {
    console.log('Request:', {
      ...metadata,
      timestamp: new Date().toISOString()
    });
  }

  static async logResponse(metadata: MonitoringMetadata, statusCode: number): Promise<void> {
    console.log('Response:', {
      ...metadata,
      statusCode,
      timestamp: new Date().toISOString()
    });
  }

  static async trackEvent(
    eventName: string,
    data: Record<string, unknown>,
    metadata: MonitoringMetadata
  ): Promise<void> {
    console.log('Event:', {
      event: eventName,
      data,
      ...metadata,
      timestamp: new Date().toISOString()
    });
  }
}
