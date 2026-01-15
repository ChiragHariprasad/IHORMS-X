import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { Input } from '@/components/ui/input';
import { FileText, Search } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface AuditLog {
  id: string;
  entity_type?: string;
  action?: string;
  user_id?: string;
  description?: string;
  created_at?: string;
}

export const OA_AuditLogsPage: React.FC = () => {
  const [entityFilter, setEntityFilter] = useState('');

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['audit', 'logs', entityFilter],
    queryFn: async () => {
      const params = entityFilter ? `?entity_type=${entityFilter}` : '';
      const response = await api.get<AuditLog[]>(`/audit/logs${params}`);
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading audit logs..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const logs = data || [];

  return (
    <div>
      <PageHeader
        title="Audit Logs"
        description="View system activity and access logs"
      />

      <div className="mb-6">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Filter by entity type..."
            value={entityFilter}
            onChange={(e) => setEntityFilter(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {logs.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={FileText}
            title="No audit logs found"
            description="There are no audit logs matching your criteria."
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Entity Type</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>User ID</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-medium">
                    {log.entity_type || '—'}
                  </TableCell>
                  <TableCell>{log.action || '—'}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {log.description || '—'}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {log.user_id || '—'}
                  </TableCell>
                  <TableCell>
                    {log.created_at
                      ? new Date(log.created_at).toLocaleString()
                      : '—'}
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
