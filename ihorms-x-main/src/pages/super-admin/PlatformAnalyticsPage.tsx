import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { BarChart3 } from 'lucide-react';

export const PlatformAnalyticsPage = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['platform-analytics'],
    queryFn: async () => {
      const response = await apiClient.get('/super-admin/analytics/platform');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} retry={refetch} />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Platform Analytics</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(data || {}).map(([key, value]) => (
          <div key={key} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 uppercase">
                  {key.replace(/_/g, ' ')}
                </p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {typeof value === 'number' ? value : JSON.stringify(value)}
                </p>
              </div>
              <BarChart3 className="w-12 h-12 text-blue-500" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
