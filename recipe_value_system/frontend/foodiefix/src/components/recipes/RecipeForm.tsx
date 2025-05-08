'use client';

import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { DifficultyLevel, CuisineType } from '@/types/recipe';
import { PlusIcon, MinusIcon, PhotoIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { uploadImage } from '@/lib/imageUpload';

// Simplified schema focusing on essential fields
const recipeSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(100),
  description: z.string().min(10, 'Description must be at least 10 characters').max(280), // Twitter-style limit
  prepTime: z.string().min(1, 'Prep time is required'),
  difficulty: z.enum(['Easy', 'Medium', 'Advanced'] as const),
  cuisine: z.enum(['Italian', 'Japanese', 'Mexican', 'Indian', 'Chinese', 'French', 'Mediterranean', 'American', 'Thai', 'Other'] as const),
  servings: z.number().min(1).max(50),
  ingredients: z.array(z.object({
    name: z.string().min(1, 'Required'),
    amount: z.number().min(0),
    unit: z.string().min(1, 'Required'),
  })).min(1, 'Add at least one ingredient'),
  steps: z.array(z.object({
    instruction: z.string().min(10, 'Make this step clearer'),
  })).min(1, 'Add at least one step'),
});

type RecipeFormData = z.infer<typeof recipeSchema>;

export default function RecipeForm() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isPreview, setIsPreview] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  const { 
    register, 
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch
  } = useForm<RecipeFormData>({
    resolver: zodResolver(recipeSchema),
    defaultValues: {
      ingredients: [{ name: '', amount: 0, unit: '' }],
      steps: [{ instruction: '' }],
    },
  });

  const { fields: ingredientFields, append: appendIngredient, remove: removeIngredient } = useFieldArray({
    control,
    name: 'ingredients',
  });

  const { fields: stepFields, append: appendStep, remove: removeStep } = useFieldArray({
    control,
    name: 'steps',
  });

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const onSubmit = async (data: RecipeFormData) => {
    try {
      setIsUploading(true);
      let imageUrl = '';
      
      if (imageFile) {
        imageUrl = await uploadImage(imageFile);
      }

      const recipeData = {
        ...data,
        imageUrl,
        createdAt: new Date().toISOString(),
      };

      // TODO: Replace with your API endpoint
      const response = await fetch('/api/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recipeData),
      });

      if (!response.ok) throw new Error('Failed to save recipe');

      // Redirect to the new recipe page
      window.location.href = '/recipes';
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to save recipe. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const formData = watch();

  const PreviewCard = () => (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {imagePreview && (
        <div className="aspect-w-16 aspect-h-9">
          <img src={imagePreview} alt="Preview" className="object-cover" />
        </div>
      )}
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-2">{formData.title || 'Recipe Title'}</h2>
        <p className="text-gray-600 mb-4">{formData.description || 'Recipe description'}</p>
        
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
          <span>{formData.prepTime || '0 min'}</span>
          <span>{formData.difficulty}</span>
          <span>{formData.servings} servings</span>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="font-medium mb-2">Ingredients</h3>
            <ul className="list-disc list-inside space-y-1">
              {formData.ingredients.map((ing, i) => (
                <li key={i}>{ing.amount} {ing.unit} {ing.name}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-medium mb-2">Instructions</h3>
            <ol className="list-decimal list-inside space-y-2">
              {formData.steps.map((step, i) => (
                <li key={i}>{step.instruction}</li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="flex justify-end space-x-4 mb-6">
        <button
          type="button"
          onClick={() => setIsPreview(!isPreview)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-xl shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          {isPreview ? 'Edit Recipe' : 'Preview'}
        </button>
      </div>

      {isPreview ? (
        <PreviewCard />
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Image Upload */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-xl">
              <div className="space-y-1 text-center">
                {imagePreview ? (
                  <img src={imagePreview} alt="Recipe preview" className="mx-auto h-32 w-32 object-cover rounded-lg" />
                ) : (
                  <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
                )}
                <div className="flex text-sm text-gray-600">
                  <label className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500">
                    <span>Upload a photo</span>
                    <input type="file" className="sr-only" accept="image/*" onChange={handleImageChange} />
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Basic Info */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
            <input
              {...register('title')}
              placeholder="Recipe Title"
              className="w-full text-2xl font-medium border-0 focus:ring-0 p-0"
            />
            {errors.title && <p className="text-sm text-red-600">{errors.title.message}</p>}

            <textarea
              {...register('description')}
              placeholder="Brief description (280 characters max)"
              rows={2}
              className="w-full border-0 focus:ring-0 p-0 resize-none"
            />
            {errors.description && <p className="text-sm text-red-600">{errors.description.message}</p>}

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <input
                {...register('prepTime')}
                placeholder="Prep time"
                className="rounded-xl"
              />
              <input
                type="number"
                {...register('servings', { valueAsNumber: true })}
                placeholder="Servings"
                className="rounded-xl"
              />
              <select {...register('difficulty')} className="rounded-xl">
                <option value="">Difficulty</option>
                {['Easy', 'Medium', 'Advanced'].map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
              <select {...register('cuisine')} className="rounded-xl">
                <option value="">Cuisine</option>
                {['Italian', 'Japanese', 'Mexican', 'Indian', 'Chinese', 'French', 'Mediterranean', 'American', 'Thai', 'Other'].map(cuisine => (
                  <option key={cuisine} value={cuisine}>{cuisine}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Ingredients */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Ingredients</h2>
              <button
                type="button"
                onClick={() => appendIngredient({ name: '', amount: 0, unit: '' })}
                className="text-primary-600 hover:text-primary-700"
              >
                <PlusIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-3">
              {ingredientFields.map((field, index) => (
                <div key={field.id} className="flex items-center space-x-2">
                  <input
                    type="number"
                    {...register(`ingredients.${index}.amount` as const, { valueAsNumber: true })}
                    placeholder="Amount"
                    className="w-20 rounded-xl"
                  />
                  <input
                    {...register(`ingredients.${index}.unit` as const)}
                    placeholder="Unit"
                    className="w-24 rounded-xl"
                  />
                  <input
                    {...register(`ingredients.${index}.name` as const)}
                    placeholder="Ingredient"
                    className="flex-1 rounded-xl"
                  />
                  <button
                    type="button"
                    onClick={() => removeIngredient(index)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <MinusIcon className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Steps */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Steps</h2>
              <button
                type="button"
                onClick={() => appendStep({ instruction: '' })}
                className="text-primary-600 hover:text-primary-700"
              >
                <PlusIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-4">
              {stepFields.map((field, index) => (
                <div key={field.id} className="flex items-start space-x-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm">
                    {index + 1}
                  </span>
                  <div className="flex-1">
                    <textarea
                      {...register(`steps.${index}.instruction` as const)}
                      placeholder="Describe this step"
                      rows={2}
                      className="w-full rounded-xl resize-none"
                    />
                    {errors.steps?.[index]?.instruction && (
                      <p className="text-sm text-red-600 mt-1">{errors.steps[index]?.instruction?.message}</p>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => removeStep(index)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <MinusIcon className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting || isUploading}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {(isSubmitting || isUploading) ? (
                <>
                  <ArrowPathIcon className="animate-spin h-5 w-5 mr-2" />
                  Saving...
                </>
              ) : (
                'Save Recipe'
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
