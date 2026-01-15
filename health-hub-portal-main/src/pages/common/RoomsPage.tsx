import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { DoorOpen } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Room {
  id: string;
  name: string;
  room_number?: string;
  floor?: string;
  type?: string;
  capacity?: number;
  is_available?: boolean;
  branch_id?: string;
}

export const RoomsPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['rooms'],
    queryFn: async () => {
      const response = await api.get<Room[]>('/rooms');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState message="Loading rooms..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const rooms = data || [];

  return (
    <div>
      <PageHeader
        title="Rooms"
        description="View all rooms in the system"
      />

      {rooms.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={DoorOpen}
            title="No rooms found"
            description="There are no rooms available in the system."
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Room</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Floor</TableHead>
                <TableHead>Capacity</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rooms.map((room) => (
                <TableRow key={room.id}>
                  <TableCell className="font-medium">
                    {room.name || room.room_number || `Room ${room.id}`}
                  </TableCell>
                  <TableCell>
                    {room.type || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    {room.floor || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    {room.capacity || <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={room.is_available ? 'active' : 'inactive'} />
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
