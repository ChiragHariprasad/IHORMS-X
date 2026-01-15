import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Wrench } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Equipment {
  id: string;
  name: string;
  type?: string;
  model?: string;
  serial_number?: string;
  status?: string;
  is_available?: boolean;
  branch_id?: string;
}

export const EquipmentPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['equipment'],
    queryFn: async () => {
      const response = await api.get<Equipment[]>('/equipment');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading equipment..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const equipment = data || [];

  return (
    <div>
      <PageHeader
        title="Equipment"
        description="View all equipment in the system"
      />

      {equipment.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Wrench}
            title="No equipment found"
            description="There is no equipment available in the system."
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Serial Number</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {equipment.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>
                    {item.type || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    {item.model || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    {item.serial_number || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={item.status || (item.is_available ? 'active' : 'inactive')} />
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
