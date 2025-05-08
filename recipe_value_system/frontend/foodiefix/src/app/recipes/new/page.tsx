'use client';

import RecipeForm from '@/components/recipes/RecipeForm';

export default function NewRecipePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create New Recipe</h1>
          <p className="mt-2 text-sm text-gray-600">
            Share your culinary masterpiece with the FoodieFix community
          </p>
        </div>
        
        <RecipeForm />
      </div>
    </div>
  );
}
