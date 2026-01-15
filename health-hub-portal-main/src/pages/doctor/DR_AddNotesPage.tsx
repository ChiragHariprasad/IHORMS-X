import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const notesSchema = z.object({
  notes: z.string().min(1, 'Notes are required').max(2000),
});

type NotesFormData = z.infer<typeof notesSchema>;

export const DR_AddNotesPage: React.FC = () => {
  const { appointmentId } = useParams<{ appointmentId: string }>();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<NotesFormData>({
    resolver: zodResolver(notesSchema),
  });

  const addNotesMutation = useMutation({
    mutationFn: async (data: NotesFormData) => {
      await api.post(`/doctor/appointments/${appointmentId}/notes`, data);
    },
    onSuccess: () => {
      toast.success('Notes added successfully');
      navigate(`/doctor/appointments/${appointmentId}`);
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  const onSubmit = (data: NotesFormData) => {
    addNotesMutation.mutate(data);
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
        title="Add Clinical Notes"
        description="Record clinical observations and notes"
      />

      <div className="max-w-xl">
        <form onSubmit={handleSubmit(onSubmit)} className="form-section space-y-6">
          <div className="space-y-2">
            <Label htmlFor="notes">Clinical Notes</Label>
            <Textarea
              id="notes"
              placeholder="Enter detailed clinical notes..."
              rows={8}
              {...register('notes')}
              className={errors.notes ? 'border-destructive' : ''}
            />
            {errors.notes && (
              <p className="text-sm text-destructive">{errors.notes.message}</p>
            )}
          </div>

          <div className="flex items-center gap-3 pt-4">
            <Button type="submit" disabled={addNotesMutation.isPending}>
              {addNotesMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Notes'
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
