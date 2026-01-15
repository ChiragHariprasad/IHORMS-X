import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const createDoctorSchema = z.object({
  email: z.string().email('Valid email is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  full_name: z.string().min(1, 'Full name is required').max(100),
  specialization: z.string().min(1, 'Specialization is required'),
  license_number: z.string().optional(),
  branch_id: z.string().optional(),
});

type CreateDoctorFormData = z.infer<typeof createDoctorSchema>;

export const OA_CreateDoctorPage: React.FC = () => {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateDoctorFormData>({
    resolver: zodResolver(createDoctorSchema),
  });

  const createMutation = useMutation({
    mutationFn: async (data: CreateDoctorFormData) => {
      const response = await api.post('/org-admin/staff/doctors', data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Doctor created successfully');
      navigate('/org-admin/staff');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  const onSubmit = (data: CreateDoctorFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div>
      <PageHeader
        title="Create Doctor"
        description="Add a new doctor to your organization"
      />

      <div className="max-w-xl">
        <form onSubmit={handleSubmit(onSubmit)} className="form-section space-y-6">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              placeholder="Dr. John Smith"
              {...register('full_name')}
              className={errors.full_name ? 'border-destructive' : ''}
            />
            {errors.full_name && (
              <p className="text-sm text-destructive">{errors.full_name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="doctor@organization.com"
              {...register('email')}
              className={errors.email ? 'border-destructive' : ''}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Minimum 8 characters"
              {...register('password')}
              className={errors.password ? 'border-destructive' : ''}
            />
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="specialization">Specialization</Label>
            <Input
              id="specialization"
              placeholder="e.g., Cardiology, Pediatrics"
              {...register('specialization')}
              className={errors.specialization ? 'border-destructive' : ''}
            />
            {errors.specialization && (
              <p className="text-sm text-destructive">{errors.specialization.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="license_number">License Number (optional)</Label>
            <Input
              id="license_number"
              placeholder="Medical license number"
              {...register('license_number')}
            />
          </div>

          <div className="flex items-center gap-3 pt-4">
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Doctor'
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/org-admin/staff')}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
