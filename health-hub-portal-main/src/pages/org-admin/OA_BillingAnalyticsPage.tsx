import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { DollarSign, TrendingUp, CreditCard, Receipt } from 'lucide-react';

interface BillingAnalytics {
  total_revenue?: number;
  pending_payments?: number;
  completed_payments?: number;
  average_bill_amount?: number;
  total_bills?: number;
}

export const OA_BillingAnalyticsPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['org-admin', 'analytics', 'billing'],
    queryFn: async () => {
      const response = await api.get<BillingAnalytics>('/org-admin/analytics/billing');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading billing analytics..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const analytics = data || {};

  return (
    <div>
      <PageHeader
        title="Billing Analytics"
        description="Organization-wide billing metrics and insights"
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-success" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Revenue</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.total_revenue !== undefined
                  ? `$${analytics.total_revenue.toLocaleString()}`
                  : '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-warning/10 flex items-center justify-center">
              <CreditCard className="w-6 h-6 text-warning" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pending Payments</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.pending_payments !== undefined
                  ? `$${analytics.pending_payments.toLocaleString()}`
                  : '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-info/10 flex items-center justify-center">
              <Receipt className="w-6 h-6 text-info" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Bills</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.total_bills ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Avg. Bill Amount</p>
              <p className="text-2xl font-bold text-foreground">
                {analytics.average_bill_amount !== undefined
                  ? `$${analytics.average_bill_amount.toLocaleString()}`
                  : '—'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
