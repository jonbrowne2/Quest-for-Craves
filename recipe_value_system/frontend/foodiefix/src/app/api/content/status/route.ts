import { ContentGenerationService } from '@/services/content-generation';
import { SecurityService } from '@/services/security';
import { MonitoringService } from '@/services/monitoring';

const wrapResponse = (data: unknown, status = 200) => {
  return new Response(JSON.stringify({
    success: true,
    data
  }), { status });
};

const wrapError = (message: string, status = 400) => {
  return new Response(JSON.stringify({
    success: false,
    error: message
  }), { status });
};

/**
 * Get content generation job status
 * 
 * @param request - The incoming HTTP request
 * @returns Response with the job status or error details
 * 
 * @example
 * GET /api/content/status?jobId=job123
 */
export async function GET(request: Request) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();

  MonitoringService.logRequest({
    id: requestId,
    method: 'GET',
    path: '/content/status',
    timestamp: new Date().toISOString()
  });

  try {
    const validation = await SecurityService.validateRequest(request, {
      requireAuth: true,
      rateLimit: { window: 60000, max: 100 }
    });

    if (!validation.allowed) {
      return wrapError(validation.reason || 'Unauthorized', 401);
    }

    const { searchParams } = new URL(request.url);
    const jobId = searchParams.get('jobId');

    if (!jobId) {
      return wrapError('Job ID is required', 400);
    }

    const job = await ContentGenerationService.checkJobStatus(jobId);
    
    if (!job) {
      return wrapError('Job not found', 404);
    }

    MonitoringService.logResponse({
      id: requestId,
      status: 200,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });

    return wrapResponse(job);
  } catch (error) {
    const errorToTrack = error instanceof Error ? error : new Error(String(error));
    
    MonitoringService.trackError(errorToTrack, {
      path: '/content/status',
      method: 'GET'
    });

    MonitoringService.logResponse({
      id: requestId,
      status: 500,
      error: errorToTrack.message,
      duration: Date.now() - startTime,
      timestamp: new Date().toISOString()
    });

    return wrapError('Failed to check job status', 500);
  }
}
