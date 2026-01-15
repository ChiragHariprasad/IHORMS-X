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

const createOrgSchema = z.object({
  name: z.string().min(1, 'Organization name is required').max(100),
  admin_email: z.string().email('Valid email is required'),
  admin_password: z.string().min(8, 'Password must be at least 8 characters'),
  subscription_type: z.string().optional(),
});

type CreateOrgFormData = z.infer<typeof createOrgSchema>;

export const SA_CreateOrganizationPage: React.FC = () => {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateOrgFormData>({
    resolver: zodResolver(createOrgSchema),
  });

  const createMutation = useMutation({
    mutationFn: async (data: CreateOrgFormData) => {
      const response = await api.post('/super-admin/organizations', data);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Organization created successfully');
      navigate('/super-admin/orgs');
    },
    onError: (err) => {
      toast.error(getErrorMessage(err));
    },
  });

  const onSubmit = (data: CreateOrgFormData) => {
    createMutation.mutate(data);
  };

  return (
    <div>
      <PageHeader
        title="Create Organization"
        description="Add a new organization to the platform"
      />

      <div className="max-w-xl">
        <form onSubmit={handleSubmit(onSubmit)} className="form-section space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Organization Name</Label>
            <Input
              id="name"
              placeholder="Enter organization name"
              {...register('name')}
              className={errors.name ? 'border-destructive' : ''}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="admin_email">Admin Email</Label>
            <Input
              id="admin_email"
              type="email"
              placeholder="admin@organization.com"
              {...register('admin_email')}
              className={errors.admin_email ? 'border-destructive' : ''}
            />
            {errors.admin_email && (
              <p className="text-sm text-destructive">{errors.admin_email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="admin_password">Admin Password</Label>
            <Input
              id="admin_password"
              type="password"
              placeholder="Minimum 8 characters"
              {...register('admin_password')}
              className={errors.admin_password ? 'border-destructive' : ''}
            />
            {errors.admin_password && (
              <p className="text-sm text-destructive">{errors.admin_password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="subscription_type">Subscription Type (optional)</Label>
            <Input
              id="subscription_type"
              placeholder="e.g., basic, pro, enterprise"
              {...register('subscription_type')}
            />
          </div>

          <div className="flex items-center gap-3 pt-4">
            <Button
              type="submit"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Organization'
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/super-admin/orgs')}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
