'use client';

import { useState } from 'react';
import RecipeCard from '@/components/recipes/RecipeCard';
import RecipeFilters from '@/components/recipes/RecipeFilters';
import { RecipeListItem, RecipeFilters as FilterType } from '@/types/recipe';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

// TODO: Replace with actual API call
const MOCK_RECIPES: RecipeListItem[] = [
  {
    id: '1',
    title: 'The WORST Chocolate Chip Cookies',
    description: "These chocolate chip cookies are the worst because they're impossible to stop eating! Perfectly chewy with crispy edges.",
    imageUrl: '/images/chocolate-chip-cookies.jpg',
    prepTime: '15 min',
    difficulty: 'Easy',
    rating: 4.8,
    valueScore: 9.2,
    servings: 24,
  },
  {
    id: '2',
    title: 'Classic Margherita Pizza',
    description: 'A traditional Neapolitan pizza with fresh basil, mozzarella, and tomatoes. Simple yet incredibly delicious.',
    imageUrl: '/images/margherita-pizza.jpg',
    prepTime: '30 min',
    difficulty: 'Medium',
    rating: 4.5,
    valueScore: 8.7,
    servings: 4,
  },
];

export default function RecipesPage() {
  const [filters, setFilters] = useState<FilterType>({
    sortBy: 'rating',
  });
  const [searchQuery, setSearchQuery] = useState('');

  const filteredRecipes = MOCK_RECIPES.filter((recipe) => {
    if (filters.difficulty && recipe.difficulty !== filters.difficulty) {
      return false;
    }
    if (filters.minRating && recipe.rating < filters.minRating) {
      return false;
    }
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        recipe.title.toLowerCase().includes(query) ||
        recipe.description.toLowerCase().includes(query)
      );
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search recipes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border-gray-200 focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          <div className="md:w-72 flex-shrink-0">
            <div className="sticky top-8">
              <RecipeFilters
                filters={filters}
                onFilterChange={setFilters}
              />
            </div>
          </div>

          <div className="flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredRecipes.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} />
              ))}
            </div>

            {filteredRecipes.length === 0 && (
              <div className="text-center py-16 bg-white rounded-2xl">
                <h3 className="text-lg font-medium text-gray-900 mb-1">
                  No recipes found
                </h3>
                <p className="text-sm text-gray-500">
                  Try adjusting your filters or search query
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
