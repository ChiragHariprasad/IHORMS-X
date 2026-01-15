import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, CheckCircle, FileText, Pill } from 'lucide-react';
import { toast } from 'sonner';

interface AppointmentDetails {
  id: string;
  patient_id: string;
  doctor_id: string;
  status: string;
  appointment_date: string;
  appointment_time: string;
  patient_name?: string;
  reason?: string;
  notes?: string;
  diagnosis?: string;
}

export const DR_AppointmentDetailsPage: React.FC = () => {
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['doctor', 'appointments', appointmentId],
    queryFn: async () => {
      const response = await api.get<AppointmentDetails>(`/doctor/appointments/${appointmentId}`);
      return response.data;
    },
    enabled: !!appointmentId,
  });

  const completeMutation = useMutation({
    mutationFn: async () => {
      await api.put(`/doctor/appointments/${appointmentId}/complete`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctor', 'appointments'] });
      toast.success('Appointment marked as complete');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  if (isLoading) return <LoadingState message="Loading appointment details..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  if (!data) {
    return <ErrorState message="Appointment not found" />;
  }

  return (
    <div>
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/doctor/appointments">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Appointments
          </Link>
        </Button>
      </div>

      <PageHeader
        title={`Appointment ${data.id}`}
        description={`${data.appointment_date} at ${data.appointment_time}`}
        actions={<StatusBadge status={data.status} />}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card-elevated">
          <h3 className="text-lg font-semibold text-foreground mb-4">Appointment Information</h3>
          <dl className="grid gap-4">
            <div>
              <dt className="text-sm text-muted-foreground">Patient ID</dt>
              <dd className="text-foreground font-medium">{data.patient_id}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Date & Time</dt>
              <dd className="text-foreground">
                {data.appointment_date} at {data.appointment_time}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Reason</dt>
              <dd className="text-foreground">{data.reason || '—'}</dd>
            </div>
            {data.notes && (
              <div>
                <dt className="text-sm text-muted-foreground">Notes</dt>
                <dd className="text-foreground">{data.notes}</dd>
              </div>
            )}
            {data.diagnosis && (
              <div>
                <dt className="text-sm text-muted-foreground">Diagnosis</dt>
                <dd className="text-foreground">{data.diagnosis}</dd>
              </div>
            )}
          </dl>
        </div>

        <div className="space-y-4">
          <div className="card-elevated">
            <h3 className="text-lg font-semibold text-foreground mb-4">Clinical Actions</h3>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link to={`/doctor/appointments/${appointmentId}/notes`}>
                  <FileText className="w-4 h-4 mr-2" />
                  Add Clinical Notes
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link to={`/doctor/appointments/${appointmentId}/diagnosis`}>
                  <FileText className="w-4 h-4 mr-2" />
                  Add Diagnosis
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link to={`/doctor/appointments/${appointmentId}/prescription`}>
                  <Pill className="w-4 h-4 mr-2" />
                  Issue Prescription
                </Link>
              </Button>
            </div>
          </div>

          {data.status === 'confirmed' && (
            <Button
              className="w-full"
              onClick={() => completeMutation.mutate()}
              disabled={completeMutation.isPending}
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Mark as Complete
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
