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

const createBranchAdminSchema = z.object({
  email: z.string().email('Valid email is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  full_name: z.string().min(1, 'Full name is required').max(100),
  branch_id: z.string().optional(),
});

type CreateBranchAdminFormData = z.infer<typeof createBranchAdminSchema>;

export const OA_CreateBranchAdminPage: React.FC = () => {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateBranchAdminFormData>({
    resolver: zodResolver(createBranchAdminSchema),
  });

  const createMutation = useMutation({
    mutationFn: async (data: CreateBranchAdminFormData) => {
      const response = await api.post('/org-admin/staff/branch-admins', data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Branch Admin created successfully');
      navigate('/org-admin/staff');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  const onSubmit = (data: CreateBranchAdminFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div>
      <PageHeader
        title="Create Branch Admin"
        description="Add a new branch administrator (Dean)"
      />

      <div className="max-w-xl">
        <form onSubmit={handleSubmit(onSubmit)} className="form-section space-y-6">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              placeholder="Enter full name"
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
              placeholder="admin@branch.org"
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

          <div className="flex items-center gap-3 pt-4">
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Branch Admin'
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
