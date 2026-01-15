import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const diagnosisSchema = z.object({
  diagnosis: z.string().min(1, 'Diagnosis is required').max(500),
  icd_code: z.string().optional(),
  notes: z.string().optional(),
});

type DiagnosisFormData = z.infer<typeof diagnosisSchema>;

export const DR_AddDiagnosisPage: React.FC = () => {
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DiagnosisFormData>({
    resolver: zodResolver(diagnosisSchema),
  });

  const addDiagnosisMutation = useMutation({
    mutationFn: async (data: DiagnosisFormData) => {
      await api.put(`/doctor/appointments/${appointmentId}/diagnosis`, data);
    },
    onSuccess: () => {
      toast.success('Diagnosis added successfully');
      navigate(`/doctor/appointments/${appointmentId}`);
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  const onSubmit = (data: DiagnosisFormData) => {
    addDiagnosisMutation.mutate(data);
  };

  return (
    <div>
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild>
          <Link to={`/doctor/appointments/${appointmentId}`}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Appointment
          </Link>
        </Button>
      </div>

      <PageHeader
        title="Add Diagnosis"
        description="Record the patient diagnosis"
      />

      <div className="max-w-xl">
        <form onSubmit={handleSubmit(onSubmit)} className="form-section space-y-6">
          <div className="space-y-2">
            <Label htmlFor="diagnosis">Diagnosis</Label>
            <Input
              id="diagnosis"
              placeholder="Primary diagnosis"
              {...register('diagnosis')}
              className={errors.diagnosis ? 'border-destructive' : ''}
            />
            {errors.diagnosis && (
              <p className="text-sm text-destructive">{errors.diagnosis.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="icd_code">ICD Code (optional)</Label>
            <Input
              id="icd_code"
              placeholder="e.g., J06.9"
              {...register('icd_code')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes (optional)</Label>
            <Textarea
              id="notes"
              placeholder="Additional observations..."
              rows={4}
              {...register('notes')}
            />
          </div>

          <div className="flex items-center gap-3 pt-4">
            <Button type="submit" disabled={addDiagnosisMutation.isPending}>
              {addDiagnosisMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Diagnosis'
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate(`/doctor/appointments/${appointmentId}`)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
