import { NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import sharp from 'sharp';
import { nanoid } from 'nanoid';
import { trackEvent } from '@/lib/analytics';

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      );
    }

    // Track upload attempt
    trackEvent('recipe_image_upload_started', {
      fileSize: file.size,
      fileType: file.type,
    });

    // Convert file to buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Generate unique filename
    const uniqueId = nanoid();
    const ext = file.type.split('/')[1];
    const filename = `${uniqueId}.${ext}`;
    const publicPath = join(process.cwd(), 'public', 'uploads');
    const filePath = join(publicPath, filename);

    // Optimize image
    const optimizedImage = await sharp(buffer)
      .resize(1200, 800, {
        fit: 'inside',
        withoutEnlargement: true,
      })
      .jpeg({
        quality: 80,
        progressive: true,
      })
      .toBuffer();

    // Save optimized image
    await writeFile(filePath, optimizedImage);

    // Track successful upload
    trackEvent('recipe_image_upload_completed', {
      fileSize: file.size,
      optimizedSize: optimizedImage.length,
      compressionRatio: (optimizedImage.length / file.size * 100).toFixed(2),
    });

    return NextResponse.json({
      url: `/uploads/${filename}`,
    });
  } catch (error) {
    console.error('Image upload error:', error);

    // Track upload error
    trackEvent('recipe_image_upload_error', {
      error: error instanceof Error ? error.message : 'Unknown error',
    });

    return NextResponse.json(
      { error: 'Failed to upload image' },
      { status: 500 }
    );
  }
}
