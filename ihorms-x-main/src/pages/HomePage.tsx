import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const roleDefaultRoutes: Record<string, string> = {
  super_admin: '/super-admin/orgs',
  org_admin: '/org-admin/staff',
  branch_admin: '/branch-admin/staff',
  doctor: '/doctor/appointments',
  nurse: '/nurse/appointments',
  receptionist: '/receptionist/appointments',
  pharmacy_staff: '/pharmacy/inventory',
  patient: '/patient/appointments',
};

export const HomePage = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const defaultRoute = roleDefaultRoutes[user.role] || '/common/branches';
  return <Navigate to={defaultRoute} replace />;
};
