import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { HomePage } from './pages/HomePage';

import { OrganizationsListPage } from './pages/super-admin/OrganizationsListPage';
import { CreateOrganizationPage } from './pages/super-admin/CreateOrganizationPage';
import { PlatformAnalyticsPage } from './pages/super-admin/PlatformAnalyticsPage';

import { OrgAdminStaffListPage } from './pages/org-admin/StaffListPage';
import { OrgAdminCreateDoctorPage } from './pages/org-admin/CreateDoctorPage';

import { DoctorAppointmentsListPage } from './pages/doctor/AppointmentsListPage';
import { DoctorAppointmentDetailsPage } from './pages/doctor/AppointmentDetailsPage';

import { PatientAppointmentsPage } from './pages/patient/AppointmentsPage';
import { PatientBookAppointmentPage } from './pages/patient/BookAppointmentPage';

import { PharmacyInventoryPage } from './pages/pharmacy/InventoryPage';

import { ReceptionistCreatePatientPage } from './pages/receptionist/CreatePatientPage';
import { ReceptionistAppointmentsListPage } from './pages/receptionist/AppointmentsListPage';

import { BranchesPage } from './pages/common/BranchesPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/super-admin/*"
              element={
                <ProtectedRoute allowedRoles={['super_admin']}>
                  <Layout>
                    <Routes>
                      <Route path="orgs" element={<OrganizationsListPage />} />
                      <Route path="orgs/new" element={<CreateOrganizationPage />} />
                      <Route path="analytics" element={<PlatformAnalyticsPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/org-admin/*"
              element={
                <ProtectedRoute allowedRoles={['org_admin']}>
                  <Layout>
                    <Routes>
                      <Route path="staff" element={<OrgAdminStaffListPage />} />
                      <Route path="staff/doctors/new" element={<OrgAdminCreateDoctorPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/doctor/*"
              element={
                <ProtectedRoute allowedRoles={['doctor']}>
                  <Layout>
                    <Routes>
                      <Route path="appointments" element={<DoctorAppointmentsListPage />} />
                      <Route path="appointments/:appointmentId" element={<DoctorAppointmentDetailsPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/patient/*"
              element={
                <ProtectedRoute allowedRoles={['patient']}>
                  <Layout>
                    <Routes>
                      <Route path="appointments" element={<PatientAppointmentsPage />} />
                      <Route path="appointments/new" element={<PatientBookAppointmentPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/pharmacy/*"
              element={
                <ProtectedRoute allowedRoles={['pharmacy_staff']}>
                  <Layout>
                    <Routes>
                      <Route path="inventory" element={<PharmacyInventoryPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/receptionist/*"
              element={
                <ProtectedRoute allowedRoles={['receptionist']}>
                  <Layout>
                    <Routes>
                      <Route path="patients/new" element={<ReceptionistCreatePatientPage />} />
                      <Route path="appointments" element={<ReceptionistAppointmentsListPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/common/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="branches" element={<BranchesPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
