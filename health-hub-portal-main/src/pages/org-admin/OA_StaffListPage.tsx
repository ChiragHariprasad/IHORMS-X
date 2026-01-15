import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { Users, Plus, UserX } from 'lucide-react';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Staff {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active?: boolean;
  branch_id?: string;
  specialization?: string;
}

export const OA_StaffListPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['org-admin', 'staff'],
    queryFn: async () => {
      const response = await api.get<Staff[]>('/org-admin/staff');
      return response.data;
    },
  });

  const disableMutation = useMutation({
    mutationFn: async (staffId: string) => {
      await api.put(`/org-admin/staff/${staffId}/disable`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org-admin', 'staff'] });
      toast.success('Staff member disabled');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  if (isLoading) return <LoadingState message="Loading staff directory..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const staff = data || [];

  return (
    <div>
      <PageHeader
        title="Staff Directory"
        description="Manage all staff members across branches"
        actions={
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Staff
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => navigate('/org-admin/staff/doctors/new')}>
                Create Doctor
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/org-admin/staff/nurses/new')}>
                Create Nurse
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/org-admin/staff/branch-admins/new')}>
                Create Branch Admin
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        }
      />

      {staff.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Users}
            title="No staff members found"
            description="Add staff members to get started."
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Specialization</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {staff.map((member) => (
                <TableRow key={member.id}>
                  <TableCell className="font-medium">
                    {member.full_name || '—'}
                  </TableCell>
                  <TableCell>{member.email}</TableCell>
                  <TableCell className="capitalize">
                    {member.role.replace('_', ' ')}
                  </TableCell>
                  <TableCell>
                    {member.specialization || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={member.is_active ? 'active' : 'inactive'} />
                  </TableCell>
                  <TableCell className="text-right">
                    {member.is_active && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => disableMutation.mutate(member.id)}
                        disabled={disableMutation.isPending}
                        className="text-destructive hover:text-destructive"
                      >
                        <UserX className="w-4 h-4" />
                      </Button>
                    )}
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
