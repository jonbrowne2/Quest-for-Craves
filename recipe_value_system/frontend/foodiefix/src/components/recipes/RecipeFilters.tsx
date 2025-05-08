import { RecipeFilters as FilterType } from '@/types/recipe';
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface RecipeFiltersProps {
  filters: FilterType;
  onFilterChange: (filters: FilterType) => void;
}

export default function RecipeFilters({ filters, onFilterChange }: RecipeFiltersProps) {
  const cuisines = [
    'All',
    'Italian',
    'Mexican',
    'Asian',
    'American',
    'Mediterranean',
    'Indian',
  ];

  const difficulties = ['Easy', 'Medium', 'Hard'];
  const sortOptions = [
    { value: 'rating', label: 'Highest Rated' },
    { value: 'valueScore', label: 'Best Value' },
    { value: 'newest', label: 'Newest' },
  ];

  const clearFilters = () => {
    onFilterChange({});
  };

  const hasActiveFilters = filters.cuisine || filters.difficulty || filters.minRating || filters.sortBy !== 'rating';

  return (
    <div className="bg-white rounded-2xl shadow-sm p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5 text-primary-500" />
          <h2 className="text-lg font-medium text-gray-900">Filters</h2>
        </div>
        
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1 transition-colors"
          >
            <XMarkIcon className="h-4 w-4" />
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Cuisine Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Cuisine
          </label>
          <div className="flex flex-wrap gap-2">
            {cuisines.map((cuisine) => (
              <button
                key={cuisine}
                onClick={() =>
                  onFilterChange({
                    ...filters,
                    cuisine: cuisine === 'All' ? undefined : cuisine,
                  })
                }
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                  ${
                    (cuisine === 'All' && !filters.cuisine) ||
                    filters.cuisine === cuisine
                      ? 'bg-primary-100 text-primary-800 ring-2 ring-primary-200'
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                  }`}
              >
                {cuisine}
              </button>
            ))}
          </div>
        </div>

        {/* Difficulty Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Difficulty
          </label>
          <div className="flex gap-2">
            {difficulties.map((level) => (
              <button
                key={level}
                onClick={() =>
                  onFilterChange({
                    ...filters,
                    difficulty: filters.difficulty === level ? undefined : level as any,
                  })
                }
                className={`flex-1 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200
                  ${
                    filters.difficulty === level
                      ? 'bg-primary-100 text-primary-800 ring-2 ring-primary-200'
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                  }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Sort Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Sort By
          </label>
          <select
            value={filters.sortBy || 'rating'}
            onChange={(e) =>
              onFilterChange({ ...filters, sortBy: e.target.value as any })
            }
            className="w-full rounded-xl border-gray-200 py-2.5 text-sm text-gray-600 focus:border-primary-500 focus:ring-primary-500 bg-gray-50"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Rating Filter */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Minimum Rating
            </label>
            <span className="text-sm text-primary-600 font-medium">
              {filters.minRating || 0} ★
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="5"
            step="0.5"
            value={filters.minRating || 0}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                minRating: parseFloat(e.target.value),
              })
            }
            className="w-full accent-primary-500"
          />
        </div>
      </div>
    </div>
  );
}
