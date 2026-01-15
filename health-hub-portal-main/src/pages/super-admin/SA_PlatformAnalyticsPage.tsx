import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { Building2, Users, Activity, TrendingUp } from 'lucide-react';

interface PlatformAnalytics {
  total_organizations?: number;
  active_organizations?: number;
  total_users?: number;
  total_appointments?: number;
  revenue?: number;
}

export const SA_PlatformAnalyticsPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['super-admin', 'analytics', 'platform'],
    queryFn: async () => {
      const response = await api.get<PlatformAnalytics>('/super-admin/analytics/platform');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading platform analytics..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const analytics = data || {};

  return (
    <div>
      <PageHeader
        title="Platform Analytics"
        description="Overview of platform-wide metrics"
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Building2 className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Organizations</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.total_organizations ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
              <Building2 className="w-6 h-6 text-success" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Active Organizations</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.active_organizations ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-info/10 flex items-center justify-center">
              <Users className="w-6 h-6 text-info" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Users</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.total_users ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-warning/10 flex items-center justify-center">
              <Activity className="w-6 h-6 text-warning" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Appointments</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.total_appointments ?? '—'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {analytics.revenue !== undefined && (
        <div className="mt-6">
          <div className="card-elevated">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Revenue</p>
                <p className="text-3xl font-bold text-foreground">
                  ${analytics.revenue.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
