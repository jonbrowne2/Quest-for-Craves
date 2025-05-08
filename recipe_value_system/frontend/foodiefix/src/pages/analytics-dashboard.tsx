import React, { useState } from 'react';
import FeatureValueDashboard from '../components/analytics/FeatureValueDashboard';
import { useAnalytics } from '../hooks/useAnalytics';
import { FeatureCategory } from '../services/feature-tracking';

/**
 * Analytics Dashboard Page
 * Demonstrates the "Simplicity Through Usage" philosophy in action
 */
export default function AnalyticsDashboardPage() {
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month' | 'quarter' | 'year'>('month');
  const analytics = useAnalytics();
  
  // Track page view when component mounts
  React.useEffect(() => {
    const trackingInfo = analytics.trackFeature('analytics_dashboard', FeatureCategory.CORE);
    
    return () => {
      // Track feature completion when component unmounts
      analytics.completeFeature(trackingInfo.trackingId, true);
    };
  }, [analytics]);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Recipe Value Analytics</h1>
        <p className="text-gray-600 mt-2">
          Insights based on our "Simplicity Through Usage" philosophy
        </p>
      </header>
      
      <div className="mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Time Range</h2>
          <div className="flex flex-wrap gap-2">
            <button
              className={`px-4 py-2 rounded-md ${timeRange === 'day' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setTimeRange('day')}
            >
              Last 24 Hours
            </button>
            <button
              className={`px-4 py-2 rounded-md ${timeRange === 'week' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setTimeRange('week')}
            >
              Last 7 Days
            </button>
            <button
              className={`px-4 py-2 rounded-md ${timeRange === 'month' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setTimeRange('month')}
            >
              Last 30 Days
            </button>
            <button
              className={`px-4 py-2 rounded-md ${timeRange === 'quarter' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setTimeRange('quarter')}
            >
              Last 90 Days
            </button>
            <button
              className={`px-4 py-2 rounded-md ${timeRange === 'year' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setTimeRange('year')}
            >
              Last Year
            </button>
          </div>
        </div>
      </div>
      
      {/* Feature Value Dashboard */}
      <FeatureValueDashboard timeRange={timeRange} />
      
      {/* Philosophy Explanation */}
      <div className="mt-12 bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Our "Simplicity Through Usage" Philosophy</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-3">Usage Frequency Metrics</h3>
            <ul className="list-disc pl-5 space-y-2">
              <li>Times accessed per user</li>
              <li>Time spent per feature</li>
              <li>Completion rates</li>
              <li>Abandonment points</li>
              <li>User segments utilizing</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-3">Value Metrics</h3>
            <ul className="list-disc pl-5 space-y-2">
              <li>User satisfaction scores</li>
              <li>Feature-specific NPS</li>
              <li>Direct user feedback</li>
              <li>Revenue impact</li>
              <li>Retention correlation</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-3">Optimization Rules</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-red-50 p-4 rounded-lg">
              <h4 className="font-medium text-red-700 mb-2">Remove if:</h4>
              <ul className="list-disc pl-5 space-y-1 text-red-800">
                <li>&lt; 5% user engagement</li>
                <li>High abandonment rate</li>
                <li>Low satisfaction scores</li>
                <li>No clear value proposition</li>
                <li>Maintenance cost &gt; Value</li>
              </ul>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-medium text-green-700 mb-2">Enhance if:</h4>
              <ul className="list-disc pl-5 space-y-1 text-green-800">
                <li>&gt; 30% user engagement</li>
                <li>High completion rates</li>
                <li>Strong user feedback</li>
                <li>Clear ROI</li>
                <li>Strategic importance</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-3">Feature Categories</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-700 mb-2">Core</h4>
              <p className="text-blue-800 text-sm">Essential features that define our product</p>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-medium text-purple-700 mb-2">Growth</h4>
              <p className="text-purple-800 text-sm">New experiments we're testing</p>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="font-medium text-yellow-700 mb-2">Legacy</h4>
              <p className="text-yellow-800 text-sm">Candidates for removal or refactoring</p>
            </div>
            
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h4 className="font-medium text-indigo-700 mb-2">Premium</h4>
              <p className="text-indigo-800 text-sm">Paid features with revenue impact</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Feedback Form */}
      <div className="mt-12 bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Help Us Improve</h2>
        <p className="text-gray-600 mb-6">
          Your feedback helps us determine which features to enhance and which to simplify.
        </p>
        
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          const rating = parseInt(formData.get('rating') as string);
          const feedback = formData.get('feedback') as string;
          
          // Submit NPS rating
          analytics.submitNPS(rating, feedback);
          
          // Reset form
          (e.target as HTMLFormElement).reset();
          
          // Show success message
          alert('Thank you for your feedback!');
        }}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="rating">
              How likely are you to recommend FoodieFix to a friend? (0-10)
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="rating"
              name="rating"
              type="number"
              min="0"
              max="10"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="feedback">
              What features do you find most valuable? What could we improve?
            </label>
            <textarea
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
              id="feedback"
              name="feedback"
              rows={4}
            />
          </div>
          
          <div className="flex items-center justify-end">
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              type="submit"
            >
              Submit Feedback
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
