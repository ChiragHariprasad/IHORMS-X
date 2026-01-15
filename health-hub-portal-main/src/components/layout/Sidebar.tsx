import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/types/auth';
import {
  Building2,
  Users,
  BarChart3,
  Calendar,
  Stethoscope,
  Activity,
  Pill,
  ClipboardList,
  UserPlus,
  Package,
  FileText,
  Shield,
  Heart,
  Home,
  Settings,
  GitBranch,
  DoorOpen,
  Wrench,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
}

const roleNavigation: Record<UserRole, NavItem[]> = {
  super_admin: [
    { label: 'Organizations', path: '/super-admin/orgs', icon: Building2 },
    { label: 'Create Organization', path: '/super-admin/orgs/new', icon: UserPlus },
    { label: 'Platform Analytics', path: '/super-admin/analytics', icon: BarChart3 },
    { label: 'System Events', path: '/super-admin/audit/system-events', icon: Shield },
  ],
  org_admin: [
    { label: 'Staff Directory', path: '/org-admin/staff', icon: Users },
    { label: 'Create Doctor', path: '/org-admin/staff/doctors/new', icon: Stethoscope },
    { label: 'Create Nurse', path: '/org-admin/staff/nurses/new', icon: Heart },
    { label: 'Create Branch Admin', path: '/org-admin/staff/branch-admins/new', icon: UserPlus },
    { label: 'Billing Analytics', path: '/org-admin/analytics/billing', icon: BarChart3 },
    { label: 'Appointment Analytics', path: '/org-admin/analytics/appointments', icon: Calendar },
    { label: 'Audit Logs', path: '/org-admin/audit/logs', icon: FileText },
  ],
  branch_admin: [
    { label: 'Branch Staff', path: '/branch-admin/staff', icon: Users },
    { label: 'Create Doctor', path: '/branch-admin/staff/doctors/new', icon: Stethoscope },
    { label: 'Create Nurse', path: '/branch-admin/staff/nurses/new', icon: Heart },
    { label: 'Create Receptionist', path: '/branch-admin/staff/receptionists/new', icon: UserPlus },
    { label: 'Create Pharmacy Staff', path: '/branch-admin/staff/pharmacy-staff/new', icon: Pill },
    { label: 'Appointment Analytics', path: '/branch-admin/analytics/appointments', icon: Calendar },
    { label: 'Operations Metrics', path: '/branch-admin/analytics/operations', icon: Activity },
    { label: 'Audit Logs', path: '/branch-admin/audit/logs', icon: FileText },
  ],
  doctor: [
    { label: 'My Appointments', path: '/doctor/appointments', icon: Calendar },
    { label: 'Schedule', path: '/doctor/schedule', icon: ClipboardList },
    { label: 'Patient Search', path: '/doctor/patients/search', icon: Users },
  ],
  nurse: [
    { label: 'Appointments', path: '/nurse/appointments', icon: Calendar },
    { label: 'Add Telemetry', path: '/nurse/telemetry/new', icon: Activity },
    { label: 'ICU Monitor', path: '/nurse/telemetry/icu', icon: Heart },
    { label: 'Alerts', path: '/nurse/telemetry/alerts', icon: Shield },
    { label: 'Rooms', path: '/nurse/rooms', icon: DoorOpen },
    { label: 'Equipment', path: '/nurse/equipment', icon: Wrench },
  ],
  pharmacy_staff: [
    { label: 'Inventory', path: '/pharmacy/inventory', icon: Package },
    { label: 'Restock', path: '/pharmacy/inventory/restock', icon: UserPlus },
    { label: 'Low Stock', path: '/pharmacy/inventory/low-stock', icon: Shield },
    { label: 'Analytics', path: '/pharmacy/inventory/analytics', icon: BarChart3 },
    { label: 'Orders', path: '/pharmacy/orders', icon: ClipboardList },
  ],
  patient: [
    { label: 'Medical History', path: '/patient/medical-history', icon: FileText },
    { label: 'My Appointments', path: '/patient/appointments', icon: Calendar },
    { label: 'Book Appointment', path: '/patient/appointments/new', icon: UserPlus },
    { label: 'Prescriptions', path: '/patient/prescriptions', icon: Pill },
    { label: 'Find Doctors', path: '/patient/doctors', icon: Stethoscope },
  ],
  receptionist: [
    { label: 'Appointments', path: '/receptionist/appointments', icon: Calendar },
    { label: 'Create Appointment', path: '/receptionist/appointments/new', icon: UserPlus },
    { label: 'Create Patient', path: '/receptionist/patients/new', icon: Users },
    { label: 'Patient Search', path: '/receptionist/patients/search', icon: Users },
    { label: 'Doctor Availability', path: '/receptionist/doctors/availability', icon: Stethoscope },
  ],
};

const commonNavigation: NavItem[] = [
  { label: 'Branches', path: '/common/branches', icon: GitBranch },
  { label: 'Rooms', path: '/common/rooms', icon: DoorOpen },
  { label: 'Equipment', path: '/common/equipment', icon: Wrench },
];

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const roleItems = roleNavigation[user.role] || [];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-sidebar flex flex-col border-r border-sidebar-border z-40">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sidebar-primary flex items-center justify-center">
            <Heart className="w-5 h-5 text-sidebar-primary-foreground" />
          </div>
          <span className="text-lg font-bold text-sidebar-foreground">IHORMS-X</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        {/* Role-specific navigation */}
        <div className="space-y-1">
          {roleItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                )
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </div>

        {/* Divider */}
        <div className="my-4 border-t border-sidebar-border" />

        {/* Common navigation */}
        <div className="space-y-1">
          <p className="px-3 py-2 text-xs font-semibold text-sidebar-muted uppercase tracking-wider">
            Common
          </p>
          {commonNavigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                )
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center">
            <span className="text-sm font-medium text-sidebar-accent-foreground">
              {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground truncate">
              {user.full_name || user.email}
            </p>
            <p className="text-xs text-sidebar-muted capitalize">
              {user.role.replace('_', ' ')}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};
