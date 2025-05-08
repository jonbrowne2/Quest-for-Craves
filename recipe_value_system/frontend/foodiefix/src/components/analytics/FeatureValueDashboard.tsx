import React, { useState, useEffect } from 'react';
import { FeatureCategory } from '../../services/feature-tracking';

// Feature ROI data interface
interface FeatureROI {
  feature_name: string;
  engagement_rate: number;
  completion_rate: number;
  satisfaction_score: number;
  roi_score: number;
  recommendation: string;
}

// Feature category data interface
interface FeatureCategoryData {
  id: number;
  name: string;
  description: string;
  created_at: string;
  last_updated: string;
}

// Dashboard props
interface FeatureValueDashboardProps {
  timeRange?: 'day' | 'week' | 'month' | 'quarter' | 'year';
}

/**
 * Feature Value Dashboard Component
 * Displays feature usage and value metrics based on the "Simplicity Through Usage" philosophy
 */
const FeatureValueDashboard: React.FC<FeatureValueDashboardProps> = ({ 
  timeRange = 'month' 
}) => {
  const [features, setFeatures] = useState<Record<string, FeatureCategoryData[]>>({});
  const [featureROI, setFeatureROI] = useState<FeatureROI[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>(FeatureCategory.CORE);

  // Fetch feature data
  useEffect(() => {
    const fetchFeatures = async () => {
      try {
        setLoading(true);
        // In a real implementation, this would fetch from your API
        const response = await fetch('/api/analytics/features');
        const data = await response.json();
        setFeatures(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load feature data');
        setLoading(false);
        console.error('Error fetching features:', err);
      }
    };

    fetchFeatures();
  }, []);

  // Fetch ROI data for selected category
  useEffect(() => {
    const fetchROIData = async () => {
      if (!features[selectedCategory]?.length) return;

      try {
        setLoading(true);
        
        // Calculate date range based on timeRange
        const endDate = new Date();
        const startDate = new Date();
        
        switch (timeRange) {
          case 'day':
            startDate.setDate(startDate.getDate() - 1);
            break;
          case 'week':
            startDate.setDate(startDate.getDate() - 7);
            break;
          case 'month':
            startDate.setMonth(startDate.getMonth() - 1);
            break;
          case 'quarter':
            startDate.setMonth(startDate.getMonth() - 3);
            break;
          case 'year':
            startDate.setFullYear(startDate.getFullYear() - 1);
            break;
        }
        
        // Fetch ROI data for each feature in the selected category
        const roiPromises = features[selectedCategory].map(async (feature) => {
          const response = await fetch(
            `/api/analytics/features/${feature.name}/roi?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`
          );
          return response.json();
        });
        
        const roiData = await Promise.all(roiPromises);
        setFeatureROI(roiData);
        setLoading(false);
      } catch (err) {
        setError('Failed to load ROI data');
        setLoading(false);
        console.error('Error fetching ROI data:', err);
      }
    };

    fetchROIData();
  }, [features, selectedCategory, timeRange]);

  // Get recommendation class based on ROI score
  const getRecommendationClass = (recommendation: string): string => {
    if (recommendation.startsWith('ENHANCE')) return 'text-green-600';
    if (recommendation.startsWith('MAINTAIN')) return 'text-blue-600';
    if (recommendation.startsWith('REVIEW')) return 'text-yellow-600';
    if (recommendation.startsWith('CONSIDER REMOVAL')) return 'text-red-600';
    return '';
  };

  // Mock data for development
  const mockFeatures = {
    [FeatureCategory.CORE]: [
      { id: 1, name: 'recipe_view', description: 'Recipe viewing', created_at: '2023-01-01', last_updated: '2023-02-01' },
      { id: 2, name: 'recipe_search', description: 'Recipe search', created_at: '2023-01-01', last_updated: '2023-02-01' }
    ],
    [FeatureCategory.GROWTH]: [
      { id: 3, name: 'recipe_variant', description: 'Recipe variants', created_at: '2023-03-01', last_updated: '2023-04-01' }
    ],
    [FeatureCategory.LEGACY]: [
      { id: 4, name: 'old_print', description: 'Legacy print function', created_at: '2022-01-01', last_updated: '2022-02-01' }
    ],
    [FeatureCategory.PREMIUM]: [
      { id: 5, name: 'ai_video', description: 'AI video generation', created_at: '2023-05-01', last_updated: '2023-06-01' }
    ]
  };

  const mockROI = [
    {
      feature_name: 'recipe_view',
      engagement_rate: 0.85,
      completion_rate: 0.95,
      satisfaction_score: 4.7,
      roi_score: 92,
      recommendation: 'ENHANCE: High ROI feature that should be enhanced and promoted'
    },
    {
      feature_name: 'recipe_search',
      engagement_rate: 0.65,
      completion_rate: 0.82,
      satisfaction_score: 4.2,
      roi_score: 78,
      recommendation: 'ENHANCE: High ROI feature that should be enhanced and promoted'
    }
  ];

  // Use mock data in development
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      setFeatures(mockFeatures);
      setFeatureROI(mockROI);
      setLoading(false);
    }
  }, []);

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Feature Value Dashboard</h2>
      
      {/* Time range selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
        <select 
          className="border border-gray-300 rounded-md p-2 w-full md:w-64"
          value={timeRange}
          onChange={(e) => setSelectedCategory(e.target.value as any)}
        >
          <option value="day">Last 24 Hours</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
          <option value="quarter">Last 90 Days</option>
          <option value="year">Last Year</option>
        </select>
      </div>
      
      {/* Category tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex -mb-px">
          {Object.keys(features).length > 0 ? (
            Object.keys(features).map((category) => (
              <button
                key={category}
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedCategory === category
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCategory(category)}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)} ({features[category]?.length || 0})
              </button>
            ))
          ) : (
            <>
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedCategory === FeatureCategory.CORE
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCategory(FeatureCategory.CORE)}
              >
                Core
              </button>
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedCategory === FeatureCategory.GROWTH
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCategory(FeatureCategory.GROWTH)}
              >
                Growth
              </button>
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedCategory === FeatureCategory.LEGACY
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCategory(FeatureCategory.LEGACY)}
              >
                Legacy
              </button>
              <button
                className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedCategory === FeatureCategory.PREMIUM
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                onClick={() => setSelectedCategory(FeatureCategory.PREMIUM)}
              >
                Premium
              </button>
            </>
          )}
        </nav>
      </div>
      
      {/* Feature ROI table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="spinner-border text-blue-500" role="status">
            <span className="sr-only">Loading...</span>
          </div>
          <p className="mt-2 text-gray-600">Loading feature data...</p>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feature
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Engagement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completion Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Satisfaction
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ROI Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {featureROI.length > 0 ? (
                featureROI.map((feature) => (
                  <tr key={feature.feature_name}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{feature.feature_name}</div>
                      <div className="text-sm text-gray-500">
                        {features[selectedCategory]?.find(f => f.name === feature.feature_name)?.description || ''}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{(feature.engagement_rate * 100).toFixed(1)}%</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{(feature.completion_rate * 100).toFixed(1)}%</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{feature.satisfaction_score.toFixed(1)}/5</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{feature.roi_score}/100</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm ${getRecommendationClass(feature.recommendation)}`}>
                        {feature.recommendation}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No ROI data available for selected features
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Feature list */}
      <div className="mt-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Features
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features[selectedCategory]?.map((feature) => (
            <div key={feature.id} className="border rounded-lg p-4 bg-gray-50">
              <h4 className="font-medium text-gray-900">{feature.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{feature.description}</p>
              <div className="mt-2 text-xs text-gray-500">
                <p>Created: {new Date(feature.created_at).toLocaleDateString()}</p>
                <p>Updated: {new Date(feature.last_updated).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeatureValueDashboard;
