import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, FileText, Calendar } from 'lucide-react';

interface MedicalRecord {
  id: string;
  date: string;
  type?: string;
  diagnosis?: string;
  treatment?: string;
  notes?: string;
  doctor_id?: string;
  doctor_name?: string;
}

export const DR_PatientHistoryPage: React.FC = () => {
  const { patientId } = useParams<{ patientId: string }>();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['doctor', 'patients', patientId, 'history'],
    queryFn: async () => {
      const response = await api.get<MedicalRecord[]>(`/doctor/patients/${patientId}/history`);
      return response.data;
    },
    enabled: !!patientId,
  });

  if (isLoading) return <LoadingState message="Loading patient history..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const records = data || [];

  return (
    <div>
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/doctor/patients/search">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Search
          </Link>
        </Button>
      </div>

      <PageHeader
        title="Patient Medical History"
        description={`Patient ID: ${patientId}`}
      />

      {records.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={FileText}
            title="No medical history"
            description="This patient has no medical records yet."
          />
        </div>
      ) : (
        <div className="space-y-4">
          {records.map((record) => (
            <div key={record.id} className="card-elevated">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <Calendar className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{record.date}</p>
                    <p className="text-sm text-muted-foreground">{record.type || 'Medical Record'}</p>
                  </div>
                </div>
                {record.doctor_name && (
                  <span className="text-sm text-muted-foreground">
                    Dr. {record.doctor_name}
                  </span>
                )}
              </div>

              <dl className="grid gap-3 sm:grid-cols-2">
                {record.diagnosis && (
                  <div>
                    <dt className="text-sm text-muted-foreground">Diagnosis</dt>
                    <dd className="text-foreground">{record.diagnosis}</dd>
                  </div>
                )}
                {record.treatment && (
                  <div>
                    <dt className="text-sm text-muted-foreground">Treatment</dt>
                    <dd className="text-foreground">{record.treatment}</dd>
                  </div>
                )}
                {record.notes && (
                  <div className="sm:col-span-2">
                    <dt className="text-sm text-muted-foreground">Notes</dt>
                    <dd className="text-foreground">{record.notes}</dd>
                  </div>
                )}
              </dl>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
