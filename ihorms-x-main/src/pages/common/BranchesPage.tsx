import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { EmptyState } from '../../components/EmptyState';
import { Building2 } from 'lucide-react';

export const BranchesPage = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['branches'],
    queryFn: async () => {
      const response = await apiClient.get('/branches');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} retry={refetch} />;

  const branches = Array.isArray(data) ? data : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Branches</h1>

      {branches.length === 0 ? (
        <EmptyState message="No branches found" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {branches.map((branch: {id: string; name?: string; address?: string; phone?: string}) => (
            <div key={branch.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center mb-4">
                <Building2 className="w-8 h-8 text-blue-500 mr-3" />
                <h3 className="text-lg font-semibold text-gray-900">
                  {branch.name || branch.id}
                </h3>
              </div>
              {branch.address && (
                <p className="text-sm text-gray-600 mb-2">{branch.address}</p>
              )}
              {branch.phone && (
                <p className="text-sm text-gray-600">{branch.phone}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
