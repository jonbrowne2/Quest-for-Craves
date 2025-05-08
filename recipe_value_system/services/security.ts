import { NextRequest } from 'next/server';
import { createHash, randomBytes } from 'crypto';
import Redis from 'ioredis';
import { Monitoring } from './monitoring';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export class SecurityService {
  private static readonly API_KEY_PREFIX = 'apikey:';
  private static readonly CSRF_PREFIX = 'csrf:';
  private static readonly RATE_LIMIT_PREFIX = 'ratelimit:';
  private static readonly DEFAULT_RATE_LIMIT = 100;
  private static readonly DEFAULT_WINDOW = 60; // seconds

  static async validateApiKey(apiKey: string): Promise<boolean> {
    try {
      const keyData = await redis.get(`${this.API_KEY_PREFIX}${apiKey}`);
      return !!keyData;
    } catch (error) {
      Monitoring.trackError(error, { context: 'api_key_validation' });
      return false;
    }
  }

  static generateCsrfToken(sessionId: string): string {
    const token = randomBytes(32).toString('hex');
    const hash = this.hashToken(token);

    // Store in Redis with 24h expiry
    redis.setex(`${this.CSRF_PREFIX}${sessionId}`, 86400, hash);

    return token;
  }

  static async validateCsrfToken(sessionId: string, token: string): Promise<boolean> {
    try {
      const storedHash = await redis.get(`${this.CSRF_PREFIX}${sessionId}`);
      if (!storedHash) return false;

      const providedHash = this.hashToken(token);
      return storedHash === providedHash;
    } catch (error) {
      Monitoring.trackError(error, { context: 'csrf_validation' });
      return false;
    }
  }

  static async checkRateLimit(
    identifier: string,
    limit = this.DEFAULT_RATE_LIMIT,
    window = this.DEFAULT_WINDOW
  ): Promise<{
    allowed: boolean;
    remaining: number;
    resetTime: number;
  }> {
    const key = `${this.RATE_LIMIT_PREFIX}${identifier}`;
    const now = Math.floor(Date.now() / 1000);

    try {
      const current = await redis.get(key);
      if (!current) {
        await redis.setex(key, window, '1');
        return {
          allowed: true,
          remaining: limit - 1,
          resetTime: now + window,
        };
      }

      const count = parseInt(current, 10);
      if (count >= limit) {
        const ttl = await redis.ttl(key);
        return {
          allowed: false,
          remaining: 0,
          resetTime: now + ttl,
        };
      }

      await redis.incr(key);
      const ttl = await redis.ttl(key);

      return {
        allowed: true,
        remaining: limit - count - 1,
        resetTime: now + ttl,
      };
    } catch (error) {
      Monitoring.trackError(error, { context: 'rate_limit' });
      // Fail open with warning
      Monitoring.trackEvent('rate_limit_fail_open', { identifier });
      return {
        allowed: true,
        remaining: 1,
        resetTime: now + window,
      };
    }
  }

  static sanitizeInput(input: unknown): unknown {
    if (typeof input === 'string') {
      return this.sanitizeString(input);
    }
    if (Array.isArray(input)) {
      return input.map(item => this.sanitizeInput(item));
    }
    if (input && typeof input === 'object') {
      return Object.fromEntries(
        Object.entries(input).map(([key, value]) => [
          key,
          this.sanitizeInput(value),
        ])
      );
    }
    return input;
  }

  static validateRequest(req: NextRequest): {
    valid: boolean;
    error?: string;
  } {
    // Validate required headers
    const apiKey = req.headers.get('x-api-key');
    if (!apiKey) {
      return { valid: false, error: 'Missing API key' };
    }

    // Validate content type for non-GET requests
    if (req.method !== 'GET' && !req.headers.get('content-type')?.includes('application/json')) {
      return { valid: false, error: 'Invalid content type' };
    }

    // Validate origin for CORS
    const origin = req.headers.get('origin');
    if (origin && !this.isAllowedOrigin(origin)) {
      return { valid: false, error: 'Invalid origin' };
    }

    return { valid: true };
  }

  private static hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private static sanitizeString(input: string): string {
    return input
      .replace(/[<>]/g, '') // Remove potential HTML tags
      .trim();
  }

  private static isAllowedOrigin(origin: string): boolean {
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];
    return allowedOrigins.includes(origin);
  }
}
