import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { Shield } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface SystemEvent {
  id: string;
  event_type?: string;
  description?: string;
  created_at?: string;
  user_id?: string;
  metadata?: Record<string, unknown>;
}

export const SA_SystemEventsPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['audit', 'system-events'],
    queryFn: async () => {
      const response = await api.get<SystemEvent[]>('/audit/system-events');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading system events..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const events = data || [];

  return (
    <div>
      <PageHeader
        title="System Events"
        description="Platform-wide system events and activity"
      />

      {events.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Shield}
            title="No system events"
            description="There are no system events recorded yet."
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Event Type</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>User ID</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {events.map((event) => (
                <TableRow key={event.id}>
                  <TableCell className="font-medium">
                    {event.event_type || '—'}
                  </TableCell>
                  <TableCell>{event.description || '—'}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {event.user_id || '—'}
                  </TableCell>
                  <TableCell>
                    {event.created_at
                      ? new Date(event.created_at).toLocaleString()
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
