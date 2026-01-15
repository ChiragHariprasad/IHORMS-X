import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { CheckCircle, XCircle, Activity } from 'lucide-react';

interface HealthStatus {
  status: string;
  database?: string;
  cache?: string;
  timestamp?: string;
}

export const SystemStatusPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get<HealthStatus>('/health');
      return response.data;
    },
    refetchInterval: 10000,
  });

  if (isLoading) return <LoadingState message="Checking system status..." />;

  if (isError) {
    return (
      <div>
        <PageHeader title="System Status" description="Backend health check" />
        <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />
      </div>
    );
  }

  const isHealthy = data?.status === 'healthy' || data?.status === 'ok';

  return (
    <div>
      <PageHeader title="System Status" description="Backend health check" />

      <div className="grid gap-6 md:grid-cols-3">
        <div className="card-metric">
          <div className="flex items-center gap-4">
            {isHealthy ? (
              <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-success" />
              </div>
            ) : (
              <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center">
                <XCircle className="w-6 h-6 text-destructive" />
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">API Status</p>
              <p className="text-lg font-semibold text-foreground capitalize">
                {data?.status || 'Unknown'}
              </p>
            </div>
          </div>
        </div>

        {data?.database && (
          <div className="card-metric">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-info/10 flex items-center justify-center">
                <Activity className="w-6 h-6 text-info" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Database</p>
                <p className="text-lg font-semibold text-foreground capitalize">
                  {data.database}
                </p>
              </div>
            </div>
          </div>
        )}

        {data?.timestamp && (
          <div className="card-metric">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                <Activity className="w-6 h-6 text-muted-foreground" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Last Check</p>
                <p className="text-lg font-semibold text-foreground">
                  {new Date(data.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
