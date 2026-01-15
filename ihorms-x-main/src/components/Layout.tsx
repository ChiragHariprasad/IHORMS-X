import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Building2,
  Users,
  Calendar,
  FileText,
  Activity,
  Package,
  UserPlus,
  ClipboardList,
  LogOut,
  BarChart3,
  Stethoscope,
  Pill,
  Shield,
  DoorOpen,
  Wrench,
} from 'lucide-react';
import { Role } from '../types';

interface LayoutProps {
  children: ReactNode;
}

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
  roles: Role[];
}

const navigationItems: NavItem[] = [
  { label: 'Organizations', path: '/super-admin/orgs', icon: Building2, roles: ['super_admin'] },
  { label: 'Platform Analytics', path: '/super-admin/analytics', icon: BarChart3, roles: ['super_admin'] },
  { label: 'System Events', path: '/super-admin/audit/system-events', icon: Shield, roles: ['super_admin'] },

  { label: 'Staff Directory', path: '/org-admin/staff', icon: Users, roles: ['org_admin'] },
  { label: 'Create Doctor', path: '/org-admin/staff/doctors/new', icon: Stethoscope, roles: ['org_admin'] },
  { label: 'Create Nurse', path: '/org-admin/staff/nurses/new', icon: Activity, roles: ['org_admin'] },
  { label: 'Create Branch Admin', path: '/org-admin/staff/branch-admins/new', icon: UserPlus, roles: ['org_admin'] },
  { label: 'Billing Analytics', path: '/org-admin/analytics/billing', icon: BarChart3, roles: ['org_admin'] },
  { label: 'Appointment Analytics', path: '/org-admin/analytics/appointments', icon: Calendar, roles: ['org_admin'] },
  { label: 'Audit Logs', path: '/org-admin/audit/logs', icon: Shield, roles: ['org_admin'] },

  { label: 'Branch Staff', path: '/branch-admin/staff', icon: Users, roles: ['branch_admin'] },
  { label: 'Create Doctor', path: '/branch-admin/staff/doctors/new', icon: Stethoscope, roles: ['branch_admin'] },
  { label: 'Create Nurse', path: '/branch-admin/staff/nurses/new', icon: Activity, roles: ['branch_admin'] },
  { label: 'Create Receptionist', path: '/branch-admin/staff/receptionists/new', icon: UserPlus, roles: ['branch_admin'] },
  { label: 'Create Pharmacy Staff', path: '/branch-admin/staff/pharmacy-staff/new', icon: Pill, roles: ['branch_admin'] },
  { label: 'Appointment Analytics', path: '/branch-admin/analytics/appointments', icon: Calendar, roles: ['branch_admin'] },
  { label: 'Operations Metrics', path: '/branch-admin/analytics/operations', icon: BarChart3, roles: ['branch_admin'] },
  { label: 'Audit Logs', path: '/branch-admin/audit/logs', icon: Shield, roles: ['branch_admin'] },

  { label: 'My Appointments', path: '/doctor/appointments', icon: Calendar, roles: ['doctor'] },
  { label: 'Schedule', path: '/doctor/schedule', icon: ClipboardList, roles: ['doctor'] },
  { label: 'Patient Search', path: '/doctor/patients/search', icon: Users, roles: ['doctor'] },

  { label: 'Appointments', path: '/nurse/appointments', icon: Calendar, roles: ['nurse'] },
  { label: 'Add Telemetry', path: '/nurse/telemetry/new', icon: Activity, roles: ['nurse'] },
  { label: 'ICU Telemetry', path: '/nurse/telemetry/icu', icon: Activity, roles: ['nurse'] },
  { label: 'Telemetry Alerts', path: '/nurse/telemetry/alerts', icon: Activity, roles: ['nurse'] },
  { label: 'Rooms', path: '/nurse/rooms', icon: DoorOpen, roles: ['nurse'] },
  { label: 'Equipment', path: '/nurse/equipment', icon: Wrench, roles: ['nurse'] },

  { label: 'Inventory', path: '/pharmacy/inventory', icon: Package, roles: ['pharmacy_staff'] },
  { label: 'Restock', path: '/pharmacy/inventory/restock', icon: Package, roles: ['pharmacy_staff'] },
  { label: 'Orders', path: '/pharmacy/orders', icon: ClipboardList, roles: ['pharmacy_staff'] },
  { label: 'Low Stock', path: '/pharmacy/inventory/low-stock', icon: Package, roles: ['pharmacy_staff'] },
  { label: 'Analytics', path: '/pharmacy/inventory/analytics', icon: BarChart3, roles: ['pharmacy_staff'] },

  { label: 'My Medical History', path: '/patient/medical-history', icon: FileText, roles: ['patient'] },
  { label: 'My Appointments', path: '/patient/appointments', icon: Calendar, roles: ['patient'] },
  { label: 'Book Appointment', path: '/patient/appointments/new', icon: Calendar, roles: ['patient'] },
  { label: 'My Prescriptions', path: '/patient/prescriptions', icon: Pill, roles: ['patient'] },
  { label: 'Browse Doctors', path: '/patient/doctors', icon: Stethoscope, roles: ['patient'] },

  { label: 'Create Patient', path: '/receptionist/patients/new', icon: UserPlus, roles: ['receptionist'] },
  { label: 'Search Patients', path: '/receptionist/patients/search', icon: Users, roles: ['receptionist'] },
  { label: 'Create Appointment', path: '/receptionist/appointments/new', icon: Calendar, roles: ['receptionist'] },
  { label: 'Appointments', path: '/receptionist/appointments', icon: Calendar, roles: ['receptionist'] },
  { label: 'Doctor Availability', path: '/receptionist/doctors/availability', icon: Stethoscope, roles: ['receptionist'] },

  { label: 'Branches', path: '/common/branches', icon: Building2, roles: ['super_admin', 'org_admin', 'branch_admin', 'doctor', 'nurse', 'receptionist', 'pharmacy_staff', 'patient'] },
  { label: 'Rooms', path: '/common/rooms', icon: DoorOpen, roles: ['super_admin', 'org_admin', 'branch_admin', 'doctor', 'nurse', 'receptionist', 'pharmacy_staff', 'patient'] },
  { label: 'Equipment', path: '/common/equipment', icon: Wrench, roles: ['super_admin', 'org_admin', 'branch_admin', 'doctor', 'nurse', 'receptionist', 'pharmacy_staff', 'patient'] },
];

export const Layout = ({ children }: LayoutProps) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const userNavItems = navigationItems.filter((item) =>
    item.roles.includes(user?.role as Role)
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">IHORMS-X</h1>
          <p className="text-sm text-gray-500 mt-1">{user?.role?.replace('_', ' ').toUpperCase()}</p>
        </div>
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {userNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={logout}
            className="flex items-center w-full px-3 py-2 text-sm font-medium text-red-700 rounded-md hover:bg-red-50 transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              {user?.email}
            </h2>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user?.organization_id && `Org: ${user.organization_id}`}
                {user?.branch_id && ` | Branch: ${user.branch_id}`}
              </span>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
