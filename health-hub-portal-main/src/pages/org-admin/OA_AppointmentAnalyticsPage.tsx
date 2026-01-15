import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { Calendar, CheckCircle, Clock, XCircle } from 'lucide-react';

interface AppointmentAnalytics {
  total_appointments?: number;
  completed_appointments?: number;
  pending_appointments?: number;
  cancelled_appointments?: number;
  completion_rate?: number;
}

export const OA_AppointmentAnalyticsPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['org-admin', 'analytics', 'appointments'],
    queryFn: async () => {
      const response = await api.get<AppointmentAnalytics>('/org-admin/analytics/appointments');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading appointment analytics..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const analytics = data || {};

  return (
    <div>
      <PageHeader
        title="Appointment Analytics"
        description="Organization-wide appointment metrics"
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Calendar className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Appointments</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.total_appointments ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-success" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.completed_appointments ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-warning/10 flex items-center justify-center">
              <Clock className="w-6 h-6 text-warning" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.pending_appointments ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center">
              <XCircle className="w-6 h-6 text-destructive" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Cancelled</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.cancelled_appointments ?? '—'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {analytics.completion_rate !== undefined && (
        <div className="mt-6">
          <div className="card-elevated">
            <h3 className="text-lg font-semibold text-foreground mb-2">Completion Rate</h3>
            <div className="flex items-center gap-4">
              <div className="flex-1 h-4 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-success rounded-full transition-all"
                  style={{ width: `${analytics.completion_rate}%` }}
                />
              </div>
              <span className="text-lg font-bold text-foreground">
                {analytics.completion_rate}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
