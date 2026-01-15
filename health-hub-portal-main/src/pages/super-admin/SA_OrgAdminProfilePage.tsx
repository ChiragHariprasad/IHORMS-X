import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { Button } from '@/components/ui/button';
import { ArrowLeft, KeyRound, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface OrgAdmin {
  id: string;
  email: string;
  full_name?: string;
  is_active?: boolean;
  organization_id?: string;
}

export const SA_OrgAdminProfilePage: React.FC = () => {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['super-admin', 'org-admins', orgId],
    queryFn: async () => {
      const response = await api.get<OrgAdmin>(`/super-admin/org-admins/${orgId}`);
      return response.data;
    },
    enabled: !!orgId,
  });

  const resetPasswordMutation = useMutation({
    mutationFn: async (adminId: string) => {
      await api.post(`/super-admin/org-admins/${adminId}/reset-password`);
    },
    onSuccess: () => {
      toast.success('Password reset email sent');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  if (isLoading) return <LoadingState message="Loading admin profile..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  if (!data) {
    return <ErrorState message="Admin not found" />;
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
        title="Org Admin Profile"
        description="View and manage organization administrator"
      />

      <div className="max-w-xl">
        <div className="card-elevated">
          <dl className="grid gap-4">
            <div>
              <dt className="text-sm text-muted-foreground">Full Name</dt>
              <dd className="text-lg font-medium text-foreground">{data.full_name || '—'}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Email</dt>
              <dd className="text-foreground">{data.email}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Status</dt>
              <dd className="text-foreground">
                {data.is_active ? 'Active' : 'Inactive'}
              </dd>
            </div>
          </dl>

          <div className="mt-6 pt-6 border-t border-border">
            <Button
              variant="outline"
              onClick={() => resetPasswordMutation.mutate(data.id)}
              disabled={resetPasswordMutation.isPending}
            >
              {resetPasswordMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Resetting...
                </>
              ) : (
                <>
                  <KeyRound className="w-4 h-4 mr-2" />
                  Reset Password
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
