import { Prisma } from '@prisma/client';
import { Counter, Histogram } from 'prom-client';
import { logger } from './logger';

// Prometheus metrics
const requestCounter = new Counter({
  name: 'recipe_api_requests_total',
  help: 'Total number of API requests',
  labelNames: ['method', 'path', 'status'],
});

const requestDuration = new Histogram({
  name: 'recipe_api_request_duration_seconds',
  help: 'API request duration in seconds',
  labelNames: ['method', 'path'],
});

const cacheHits = new Counter({
  name: 'recipe_cache_hits_total',
  help: 'Total number of cache hits',
  labelNames: ['type'],
});

const cacheMisses = new Counter({
  name: 'recipe_cache_misses_total',
  help: 'Total number of cache misses',
  labelNames: ['type'],
});

export class Monitoring {
  static trackRequest(method: string, path: string, status: number, duration: number) {
    requestCounter.inc({ method, path, status });
    requestDuration.observe({ method, path }, duration);

    // Log slow requests
    if (duration > 1000) {
      logger.warn('Slow request detected', {
        method,
        path,
        duration,
        status,
      });
    }
  }

  static trackCacheHit(type: string) {
    cacheHits.inc({ type });
  }

  static trackCacheMiss(type: string) {
    cacheMisses.inc({ type });
  }

  static trackError(error: Error, context?: any) {
    if (error instanceof Prisma.PrismaClientKnownRequestError) {
      logger.error('Database error', {
        code: error.code,
        meta: error.meta,
        message: error.message,
        context,
      });
    } else {
      logger.error('Application error', {
        name: error.name,
        message: error.message,
        stack: error.stack,
        context,
      });
    }
  }

  static trackAnalytics(recipeId: string, metrics: Record<string, number>) {
    logger.info('Recipe analytics updated', {
      recipeId,
      metrics,
      timestamp: new Date().toISOString(),
    });
  }
}
