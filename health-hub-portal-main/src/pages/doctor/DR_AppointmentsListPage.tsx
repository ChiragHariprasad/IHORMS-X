import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, Eye, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  status: string;
  appointment_date: string;
  appointment_time: string;
  patient_name?: string;
  reason?: string;
}

export const DR_AppointmentsListPage: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['doctor', 'appointments', statusFilter],
    queryFn: async () => {
      const params = statusFilter ? `?status=${statusFilter}` : '';
      const response = await api.get<Appointment[]>(`/doctor/appointments${params}`);
      return response.data;
    },
  });

  const acceptMutation = useMutation({
    mutationFn: async (appointmentId: string) => {
      await api.put(`/doctor/appointments/${appointmentId}/accept`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor', 'appointments'] });
      toast.success('Appointment accepted');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  const rejectMutation = useMutation({
    mutationFn: async (appointmentId: string) => {
      await api.put(`/doctor/appointments/${appointmentId}/reject`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor', 'appointments'] });
      toast.success('Appointment rejected');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  if (isLoading) return <LoadingState message="Loading appointments..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const appointments = data || [];

  return (
    <div>
      <PageHeader
        title="My Appointments"
        description="View and manage your appointments"
      />

      <div className="mb-6">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="confirmed">Confirmed</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {appointments.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Calendar}
            title="No appointments found"
            description="You have no appointments matching your criteria."
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Patient ID</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {appointments.map((appointment) => (
                <TableRow key={appointment.id}>
                  <TableCell className="font-medium">
                    {appointment.appointment_date}
                  </TableCell>
                  <TableCell>{appointment.appointment_time}</TableCell>
                  <TableCell>{appointment.patient_id}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {appointment.reason || '—'}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={appointment.status} />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/doctor/appointments/${appointment.id}`}>
                          <Eye className="w-4 h-4" />
                        </Link>
                      </Button>
                      {appointment.status === 'pending' && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => acceptMutation.mutate(appointment.id)}
                            disabled={acceptMutation.isPending}
                            className="text-success hover:text-success"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => rejectMutation.mutate(appointment.id)}
                            disabled={rejectMutation.isPending}
                            className="text-destructive hover:text-destructive"
                          >
                            <XCircle className="w-4 h-4" />
                          </Button>
                        </>
                      )}
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
