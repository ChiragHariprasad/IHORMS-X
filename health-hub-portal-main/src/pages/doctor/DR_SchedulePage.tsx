import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Calendar, Clock } from 'lucide-react';

interface ScheduleSlot {
  id: string;
  date: string;
  time: string;
  is_available?: boolean;
  patient_id?: string;
  appointment_id?: string;
}

export const DR_SchedulePage: React.FC = () => {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['doctor', 'schedule', date],
    queryFn: async () => {
      const response = await api.get<ScheduleSlot[]>(`/doctor/schedule?date=${date}`);
      return response.data;
    },
    enabled: !!date,
  });

  if (isLoading) return <LoadingState message="Loading schedule..." />;

  if (isError) {
    return <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />;
  }

  const schedule = data || [];

  return (
    <div>
      <PageHeader
        title="My Schedule"
        description="View your daily schedule and appointments"
      />

      <div className="mb-6">
        <Input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-48"
        />
      </div>

      {schedule.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Calendar}
            title="No schedule entries"
            description={`No appointments scheduled for ${date}`}
          />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {schedule.map((slot) => (
            <div
              key={slot.id}
              className={`card-metric ${slot.is_available ? 'border-success/30' : 'border-warning/30'}`}
            >
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  slot.is_available ? 'bg-success/10' : 'bg-warning/10'
                }`}>
                  <Clock className={`w-6 h-6 ${
                    slot.is_available ? 'text-success' : 'text-warning'
                  }`} />
                </div>
                <div>
                  <p className="text-lg font-semibold text-foreground">{slot.time}</p>
                  <p className="text-sm text-muted-foreground">
                    {slot.is_available ? 'Available' : 'Booked'}
                  </p>
                  {slot.patient_id && (
                    <p className="text-xs text-muted-foreground">
                      Patient: {slot.patient_id}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
