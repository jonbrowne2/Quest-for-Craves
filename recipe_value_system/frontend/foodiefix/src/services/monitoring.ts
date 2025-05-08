export class MonitoringService {
  static trackError(error: Error, context: { path: string; method: string }) {
    console.error(`[${context.method}] ${context.path} Error:`, error);
  }

  static trackRequest(method: string, path: string, status: number, duration: number) {
    console.log(`[${method}] ${path} Status: ${status} Duration: ${duration}ms`);
  }

  static trackCacheHit(type: string) {
    console.log(`Cache hit for ${type}`);
  }

  static trackCacheMiss(type: string) {
    console.log(`Cache miss for ${type}`);
  }
}
