import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/common/ProtectedRoute";
import { MainLayout } from "@/components/layout/MainLayout";

// Auth Pages
import { LoginPage } from "@/pages/auth/LoginPage";
import { UnauthorizedPage } from "@/pages/auth/UnauthorizedPage";
import Index from "@/pages/Index";
import NotFound from "@/pages/NotFound";

// Common Pages
import { BranchesPage } from "@/pages/common/BranchesPage";
import { RoomsPage } from "@/pages/common/RoomsPage";
import { EquipmentPage } from "@/pages/common/EquipmentPage";

// Super Admin Pages
import { SA_OrganizationsListPage } from "@/pages/super-admin/SA_OrganizationsListPage";
import { SA_CreateOrganizationPage } from "@/pages/super-admin/SA_CreateOrganizationPage";
import { SA_OrganizationDetailsPage } from "@/pages/super-admin/SA_OrganizationDetailsPage";
import { SA_PlatformAnalyticsPage } from "@/pages/super-admin/SA_PlatformAnalyticsPage";
import { SA_OrgAdminProfilePage } from "@/pages/super-admin/SA_OrgAdminProfilePage";
import { SA_SystemEventsPage } from "@/pages/super-admin/SA_SystemEventsPage";

// Org Admin Pages
import { OA_StaffListPage } from "@/pages/org-admin/OA_StaffListPage";
import { OA_CreateDoctorPage } from "@/pages/org-admin/OA_CreateDoctorPage";
import { OA_CreateNursePage } from "@/pages/org-admin/OA_CreateNursePage";
import { OA_CreateBranchAdminPage } from "@/pages/org-admin/OA_CreateBranchAdminPage";
import { OA_BillingAnalyticsPage } from "@/pages/org-admin/OA_BillingAnalyticsPage";
import { OA_AppointmentAnalyticsPage } from "@/pages/org-admin/OA_AppointmentAnalyticsPage";
import { OA_AuditLogsPage } from "@/pages/org-admin/OA_AuditLogsPage";

// Doctor Pages
import { DR_AppointmentsListPage } from "@/pages/doctor/DR_AppointmentsListPage";
import { DR_AppointmentDetailsPage } from "@/pages/doctor/DR_AppointmentDetailsPage";
import { DR_SchedulePage } from "@/pages/doctor/DR_SchedulePage";
import { DR_PatientSearchPage } from "@/pages/doctor/DR_PatientSearchPage";
import { DR_PatientHistoryPage } from "@/pages/doctor/DR_PatientHistoryPage";
import { DR_AddNotesPage } from "@/pages/doctor/DR_AddNotesPage";
import { DR_AddDiagnosisPage } from "@/pages/doctor/DR_AddDiagnosisPage";
import { DR_IssuePrescriptionPage } from "@/pages/doctor/DR_IssuePrescriptionPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            {/* Protected Routes with Layout */}
            <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
              <Route path="/" element={<Index />} />

              {/* Common Routes */}
              <Route path="/common/branches" element={<BranchesPage />} />
              <Route path="/common/rooms" element={<RoomsPage />} />
              <Route path="/common/equipment" element={<EquipmentPage />} />

              {/* Super Admin Routes */}
              <Route path="/super-admin/orgs" element={<ProtectedRoute allowedRoles={['super_admin']}><SA_OrganizationsListPage /></ProtectedRoute>} />
              <Route path="/super-admin/orgs/new" element={<ProtectedRoute allowedRoles={['super_admin']}><SA_CreateOrganizationPage /></ProtectedRoute>} />
              <Route path="/super-admin/orgs/:orgId" element={<ProtectedRoute allowedRoles={['super_admin']}><SA_OrganizationDetailsPage /></ProtectedRoute>} />
              <Route path="/super-admin/analytics" element={<ProtectedRoute allowedRoles={['super_admin']}><SA_PlatformAnalyticsPage /></ProtectedRoute>} />
              <Route path="/super-admin/org-admin/:orgId" element={<ProtectedRoute allowedRoles={['super_admin']}><SA_OrgAdminProfilePage /></ProtectedRoute>} />
              <Route path="/super-admin/audit/system-events" element={<ProtectedRoute allowedRoles={['super_admin']}><SA_SystemEventsPage /></ProtectedRoute>} />

              {/* Org Admin Routes */}
              <Route path="/org-admin/staff" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_StaffListPage /></ProtectedRoute>} />
              <Route path="/org-admin/staff/doctors/new" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_CreateDoctorPage /></ProtectedRoute>} />
              <Route path="/org-admin/staff/nurses/new" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_CreateNursePage /></ProtectedRoute>} />
              <Route path="/org-admin/staff/branch-admins/new" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_CreateBranchAdminPage /></ProtectedRoute>} />
              <Route path="/org-admin/analytics/billing" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_BillingAnalyticsPage /></ProtectedRoute>} />
              <Route path="/org-admin/analytics/appointments" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_AppointmentAnalyticsPage /></ProtectedRoute>} />
              <Route path="/org-admin/audit/logs" element={<ProtectedRoute allowedRoles={['org_admin']}><OA_AuditLogsPage /></ProtectedRoute>} />

              {/* Doctor Routes */}
              <Route path="/doctor/appointments" element={<ProtectedRoute allowedRoles={['doctor']}><DR_AppointmentsListPage /></ProtectedRoute>} />
              <Route path="/doctor/appointments/:appointmentId" element={<ProtectedRoute allowedRoles={['doctor']}><DR_AppointmentDetailsPage /></ProtectedRoute>} />
              <Route path="/doctor/appointments/:appointmentId/notes" element={<ProtectedRoute allowedRoles={['doctor']}><DR_AddNotesPage /></ProtectedRoute>} />
              <Route path="/doctor/appointments/:appointmentId/diagnosis" element={<ProtectedRoute allowedRoles={['doctor']}><DR_AddDiagnosisPage /></ProtectedRoute>} />
              <Route path="/doctor/appointments/:appointmentId/prescription" element={<ProtectedRoute allowedRoles={['doctor']}><DR_IssuePrescriptionPage /></ProtectedRoute>} />
              <Route path="/doctor/schedule" element={<ProtectedRoute allowedRoles={['doctor']}><DR_SchedulePage /></ProtectedRoute>} />
              <Route path="/doctor/patients/search" element={<ProtectedRoute allowedRoles={['doctor']}><DR_PatientSearchPage /></ProtectedRoute>} />
              <Route path="/doctor/patients/:patientId/history" element={<ProtectedRoute allowedRoles={['doctor']}><DR_PatientHistoryPage /></ProtectedRoute>} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
