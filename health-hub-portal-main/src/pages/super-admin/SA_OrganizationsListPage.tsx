import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, Link } from 'react-router-dom';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { Building2, Plus, Eye, ToggleLeft, ToggleRight } from 'lucide-react';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Organization {
  id: string;
  name: string;
  is_active?: boolean;
  created_at?: string;
  subscription_type?: string;
}

export const SA_OrganizationsListPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['super-admin', 'organizations'],
    queryFn: async () => {
      const response = await api.get<Organization[]>('/super-admin/organizations');
      return response.data;
    },
  });

  const toggleStatusMutation = useMutation({
    mutationFn: async ({ orgId, status }: { orgId: string; status: boolean }) => {
      await api.put(`/super-admin/organizations/${orgId}/status`, { is_active: status });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['super-admin', 'organizations'] });
      toast.success('Organization status updated');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  if (isLoading) return <LoadingState message="Loading organizations..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const organizations = data || [];

  return (
    <div>
      <PageHeader
        title="Organizations"
        description="Manage all organizations on the platform"
        actions={
          <Button onClick={() => navigate('/super-admin/orgs/new')}>
            <Plus className="w-4 h-4 mr-2" />
            Create Organization
          </Button>
        }
      />

      {organizations.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Building2}
            title="No organizations found"
            description="Create your first organization to get started."
            action={
              <Button onClick={() => navigate('/super-admin/orgs/new')}>
                <Plus className="w-4 h-4 mr-2" />
                Create Organization
              </Button>
            }
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Organization</TableHead>
                <TableHead>Subscription</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {organizations.map((org) => (
                <TableRow key={org.id}>
                  <TableCell className="font-medium">{org.name}</TableCell>
                  <TableCell>
                    {org.subscription_type || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    {org.created_at 
                      ? new Date(org.created_at).toLocaleDateString() 
                      : <span className="text-muted-foreground">—</span>
                    }
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={org.is_active ? 'active' : 'inactive'} />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        asChild
                      >
                        <Link to={`/super-admin/orgs/${org.id}`}>
                          <Eye className="w-4 h-4" />
                        </Link>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleStatusMutation.mutate({
                          orgId: org.id,
                          status: !org.is_active,
                        })}
                        disabled={toggleStatusMutation.isPending}
                      >
                        {org.is_active ? (
                          <ToggleRight className="w-4 h-4 text-success" />
                        ) : (
                          <ToggleLeft className="w-4 h-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
};
