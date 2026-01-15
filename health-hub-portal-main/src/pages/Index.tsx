import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

const roleDefaultRoutes: Record<string, string> = {
  super_admin: '/super-admin/orgs',
  org_admin: '/org-admin/staff',
  branch_admin: '/branch-admin/staff',
  doctor: '/doctor/appointments',
  nurse: '/nurse/appointments',
  pharmacy_staff: '/pharmacy/inventory',
  patient: '/patient/appointments',
  receptionist: '/receptionist/appointments',
};

const Index: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="loading-spinner" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const defaultRoute = user?.role ? roleDefaultRoutes[user.role] : '/common/branches';
  return <Navigate to={defaultRoute} replace />;
};

export default Index;
