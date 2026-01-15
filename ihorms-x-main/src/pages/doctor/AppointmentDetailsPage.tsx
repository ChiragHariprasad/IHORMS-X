import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../../lib/api';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';

export const DoctorAppointmentDetailsPage = () => {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['appointment-details', appointmentId],
    queryFn: async () => {
      const response = await apiClient.get(`/doctor/appointments/${appointmentId}`);
      return response.data;
    },
  });

  const acceptMutation = useMutation({
    mutationFn: async () => {
      await apiClient.put(`/doctor/appointments/${appointmentId}/accept`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointment-details', appointmentId] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: async () => {
      await apiClient.put(`/doctor/appointments/${appointmentId}/reject`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointment-details', appointmentId] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: async () => {
      await apiClient.put(`/doctor/appointments/${appointmentId}/complete`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointment-details', appointmentId] });
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} retry={refetch} />;

  return (
    <div>
      <button
        onClick={() => navigate('/doctor/appointments')}
        className="mb-4 text-blue-600 hover:text-blue-800"
      >
        ← Back to Appointments
      </button>

      <h1 className="text-2xl font-bold text-gray-900 mb-6">Appointment Details</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        {Object.entries(data || {}).map(([key, value]) => (
          <div key={key} className="flex justify-between py-2 border-b border-gray-200">
            <span className="font-medium text-gray-700">{key.replace(/_/g, ' ').toUpperCase()}</span>
            <span className="text-gray-900">{String(value)}</span>
          </div>
        ))}
      </div>

      <div className="mt-6 flex space-x-3">
        <button
          onClick={() => acceptMutation.mutate()}
          disabled={acceptMutation.isPending}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          Accept
        </button>
        <button
          onClick={() => rejectMutation.mutate()}
          disabled={rejectMutation.isPending}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
        >
          Reject
        </button>
        <button
          onClick={() => completeMutation.mutate()}
          disabled={completeMutation.isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Complete
        </button>
        <button
          onClick={() => navigate(`/doctor/appointments/${appointmentId}/notes`)}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Add Notes
        </button>
        <button
          onClick={() => navigate(`/doctor/appointments/${appointmentId}/diagnosis`)}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Add Diagnosis
        </button>
        <button
          onClick={() => navigate(`/doctor/appointments/${appointmentId}/prescription`)}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Issue Prescription
        </button>
      </div>
    </div>
  );
};
