import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Users, Building2 } from 'lucide-react';

interface OrganizationDetails {
  id: string;
  name: string;
  is_active?: boolean;
  created_at?: string;
  subscription_type?: string;
  admin_email?: string;
  branches_count?: number;
  staff_count?: number;
}

export const SA_OrganizationDetailsPage: React.FC = () => {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['super-admin', 'organizations', orgId],
    queryFn: async () => {
      const response = await api.get<OrganizationDetails>(`/super-admin/organizations/${orgId}`);
      return response.data;
    },
    enabled: !!orgId,
  });

  if (isLoading) return <LoadingState message="Loading organization details..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  if (!data) {
    return <ErrorState message="Organization not found" />;
  }

  return (
    <div>
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/super-admin/orgs">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Organizations
          </Link>
        </Button>
      </div>

      <PageHeader
        title={data.name}
        description="Organization details and management"
        actions={
          <StatusBadge status={data.is_active ? 'active' : 'inactive'} />
        }
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Building2 className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Subscription</p>
              <p className="text-lg font-semibold text-foreground">
                {data.subscription_type || 'Not set'}
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
              <p className="text-sm text-muted-foreground">Branches</p>
              <p className="text-lg font-semibold text-foreground">
                {data.branches_count ?? '—'}
              </p>
            </div>
          </div>
        </div>

        <div className="card-metric">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center">
              <Users className="w-6 h-6 text-success" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Staff Count</p>
              <p className="text-lg font-semibold text-foreground">
                {data.staff_count ?? '—'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 card-elevated">
        <h3 className="text-lg font-semibold text-foreground mb-4">Organization Information</h3>
        <dl className="grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-sm text-muted-foreground">Admin Email</dt>
            <dd className="text-foreground">{data.admin_email || '—'}</dd>
          </div>
          <div>
            <dt className="text-sm text-muted-foreground">Created</dt>
            <dd className="text-foreground">
              {data.created_at ? new Date(data.created_at).toLocaleDateString() : '—'}
            </dd>
          </div>
        </dl>
      </div>

      <div className="mt-6">
        <Button variant="outline" asChild>
          <Link to={`/super-admin/org-admin/${orgId}`}>
            View Org Admin Profile
          </Link>
        </Button>
      </div>
    </div>
  );
};
