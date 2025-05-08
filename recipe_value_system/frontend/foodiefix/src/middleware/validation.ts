import { NextResponse } from 'next/server';
import { rateLimit } from '@/lib/rate-limit';
import { sanitizeInput } from '@/lib/security';
import { prisma } from '@/lib/prisma';
import { ZodSchema } from 'zod';

export interface ValidationOptions {
  schema?: ZodSchema;
  requireAuth?: boolean;
  rateLimit?: {
    window: number; // in seconds
    max: number;
  };
}

export async function validateRequest(
  request: Request,
  options: ValidationOptions = {}
) {
  try {
    // 1. Rate limiting
    if (options.rateLimit) {
      const ip = request.headers.get('x-forwarded-for') || 'unknown';
      const { success, limit, remaining, reset } = await rateLimit(
        ip,
        options.rateLimit.window,
        options.rateLimit.max
      );

      if (!success) {
        return NextResponse.json(
          {
            success: false,
            error: 'Too many requests',
            reset,
          },
          {
            status: 429,
            headers: {
              'X-RateLimit-Limit': limit.toString(),
              'X-RateLimit-Remaining': remaining.toString(),
              'X-RateLimit-Reset': reset.toString(),
            },
          }
        );
      }
    }

    // 2. Get and validate request data
    let data = {};
    if (request.method !== 'GET') {
      const rawData = await request.json();
      data = sanitizeInput(rawData);
    }

    // 3. Schema validation
    if (options.schema) {
      data = options.schema.parse(data);
    }

    // 4. Auth check
    if (options.requireAuth) {
      const userId = request.headers.get('x-user-id');
      if (!userId) {
        return NextResponse.json(
          { success: false, error: 'Authentication required' },
          { status: 401 }
        );
      }

      // Verify user exists
      const user = await prisma.user.findUnique({
        where: { id: userId },
        select: { id: true },
      });

      if (!user) {
        return NextResponse.json(
          { success: false, error: 'Invalid user' },
          { status: 401 }
        );
      }

      data = { ...data, userId };
    }

    return { success: true, data };
  } catch (error) {
    console.error('Validation error:', error);
    return NextResponse.json(
      { success: false, error: 'Invalid request' },
      { status: 400 }
    );
  }
}
