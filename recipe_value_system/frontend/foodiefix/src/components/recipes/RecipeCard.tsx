import Image from 'next/image';
import Link from 'next/link';
import { RecipeListItem } from '@/types/recipe';
import { StarIcon, ClockIcon } from '@heroicons/react/24/solid';

interface RecipeCardProps {
  recipe: RecipeListItem;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const {
    id,
    title,
    description,
    imageUrl,
    prepTime,
    difficulty,
    rating,
    valueScore,
  } = recipe;

  return (
    <Link 
      href={`/recipes/${id}`} 
      className="group relative block overflow-hidden rounded-2xl bg-white shadow-sm transition-all duration-300 hover:shadow-xl animate-fade-in"
    >
      <div className="aspect-w-16 aspect-h-9 relative overflow-hidden">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={title}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
            <span className="text-primary-600 font-medium">Coming soon</span>
          </div>
        )}
        
        {/* Floating difficulty badge */}
        <div className="absolute top-4 left-4">
          <span className={`
            px-3 py-1 rounded-full text-xs font-medium backdrop-blur-md
            ${difficulty === 'Easy' 
              ? 'bg-green-100/90 text-green-800' 
              : difficulty === 'Medium'
              ? 'bg-yellow-100/90 text-yellow-800'
              : 'bg-red-100/90 text-red-800'
            }`}
          >
            {difficulty}
          </span>
        </div>

        {/* Rating badge */}
        <div className="absolute top-4 right-4">
          <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-white/90 backdrop-blur-md">
            <StarIcon className="h-3.5 w-3.5 text-yellow-400" />
            <span className="text-xs font-medium text-gray-700">
              {rating.toFixed(1)}
            </span>
          </div>
        </div>
      </div>

      <div className="p-4">
        <h3 className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors">
          {title}
        </h3>
        
        <p className="mt-1 text-sm text-gray-500 line-clamp-2">
          {description}
        </p>

        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <ClockIcon className="h-4 w-4 text-primary-500" />
            <span className="text-sm text-gray-600">{prepTime}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <div className="h-1.5 w-16 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-primary-500 transition-all duration-300"
                style={{ width: `${(valueScore / 10) * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-500">Value</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
