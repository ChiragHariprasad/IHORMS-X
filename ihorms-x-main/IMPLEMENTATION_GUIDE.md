# IHORMS-X Frontend Implementation Guide

This guide explains the architecture and patterns for implementing the remaining pages.

## Architecture Overview

### Core Components

1. **API Client** (`src/lib/api.ts`)
   - Axios instance with base URL `http://localhost:8000/api`
   - Automatic JWT token injection via interceptor
   - Auto-logout on 401 responses

2. **Auth Context** (`src/context/AuthContext.tsx`)
   - Manages authentication state
   - Provides `user`, `login`, `logout`, and `refetchUser`
   - Fetches current user from `/api/auth/me` on app init

3. **Protected Routes** (`src/components/ProtectedRoute.tsx`)
   - Wraps routes requiring authentication
   - Supports role-based access via `allowedRoles` prop
   - Redirects to `/login` or `/unauthorized` as needed

4. **Layout** (`src/components/Layout.tsx`)
   - Sidebar with dynamic navigation based on user role
   - Topbar with user info and logout button
   - Navigation items filtered by role

## Page Implementation Pattern

Every page follows this standard pattern:

### 1. List/Table Pages

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { EmptyState } from '../../components/EmptyState';

export const ExampleListPage = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['example-items'],
    queryFn: async () => {
      const response = await apiClient.get('/endpoint');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} retry={refetch} />;

  const items = Array.isArray(data) ? data : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Page Title</h1>

      {items.length === 0 ? (
        <EmptyState message="No items found" />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            {/* Table content */}
          </table>
        </div>
      )}
    </div>
  );
};
```

### 2. Create/Form Pages

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';

export const ExampleCreatePage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    field1: '',
    field2: '',
  });

  const mutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await apiClient.post('/endpoint', data);
      return response.data;
    },
    onSuccess: () => {
      navigate('/success-route');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Create Item</h1>

      {mutation.error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-700">{(mutation.error as Error).message}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-4">
        {/* Form fields */}

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {mutation.isPending ? 'Creating...' : 'Create'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/back-route')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
```

### 3. Detail Pages with Actions

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../../lib/api';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';

export const ExampleDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['item-details', id],
    queryFn: async () => {
      const response = await apiClient.get(`/endpoint/${id}`);
      return response.data;
    },
  });

  const actionMutation = useMutation({
    mutationFn: async () => {
      await apiClient.put(`/endpoint/${id}/action`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['item-details', id] });
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} retry={refetch} />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Details</h1>

      <div className="bg-white rounded-lg shadow p-6">
        {/* Display data */}
      </div>

      <div className="mt-6 flex space-x-3">
        <button
          onClick={() => actionMutation.mutate()}
          disabled={actionMutation.isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Action
        </button>
      </div>
    </div>
  );
};
```

## Adding New Pages - Step-by-Step

### Example: Adding Nurse Appointments Page

#### 1. Create the page component

Create `src/pages/nurse/AppointmentsListPage.tsx`:

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';
import { LoadingState } from '../../components/LoadingState';
import { ErrorState } from '../../components/ErrorState';
import { EmptyState } from '../../components/EmptyState';
import { useNavigate } from 'react-router-dom';

export const NurseAppointmentsListPage = () => {
  const navigate = useNavigate();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['nurse-appointments'],
    queryFn: async () => {
      const response = await apiClient.get('/nurse/appointments');
      return response.data;
    },
  });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={(error as Error).message} retry={refetch} />;

  const appointments = Array.isArray(data) ? data : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Appointments</h1>

      {appointments.length === 0 ? (
        <EmptyState message="No appointments found" />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {appointments.map((apt: any) => (
                <tr key={apt.id}>
                  <td className="px-6 py-4 text-sm text-gray-900">{apt.id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{apt.patient_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{apt.appointment_date}</td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <button
                      onClick={() => navigate(`/nurse/appointments/${apt.id}`)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
```

#### 2. Add route to App.tsx

```typescript
// Import the component
import { NurseAppointmentsListPage } from './pages/nurse/AppointmentsListPage';

// Add route in the appropriate section
<Route
  path="/nurse/*"
  element={
    <ProtectedRoute allowedRoles={['nurse']}>
      <Layout>
        <Routes>
          <Route path="appointments" element={<NurseAppointmentsListPage />} />
          {/* Other nurse routes */}
        </Routes>
      </Layout>
    </ProtectedRoute>
  }
/>
```

#### 3. Navigation is already handled

The Layout component dynamically generates navigation from the `navigationItems` array based on the user's role. The menu items are already defined.

## Remaining Pages to Implement

### Super Admin
- [x] Organizations List
- [x] Create Organization
- [ ] Organization Details (`GET /super-admin/organizations/{org_id}`)
- [x] Platform Analytics
- [ ] Org Admin Profile (`GET /super-admin/org-admins/{org_id}`)
- [ ] Reset Org Admin Password (`POST /super-admin/org-admins/{admin_id}/reset-password`)
- [ ] System Events (`GET /audit/system-events`)

### Org Admin
- [x] Staff List
- [x] Create Doctor
- [ ] Create Nurse (`POST /org-admin/staff/nurses`)
- [ ] Create Branch Admin (`POST /org-admin/staff/branch-admins`)
- [ ] Reset Dean Password (`POST /org-admin/branch-admins/{dean_id}/reset-password`)
- [x] Billing Analytics
- [x] Appointment Analytics
- [ ] Audit Logs (`GET /audit/logs`)
- [ ] Patient Access Logs (`GET /audit/patient-access/{patient_id}`)

### Branch Admin
- [ ] All staff management pages (similar to Org Admin)
- [ ] Appointment Analytics
- [ ] Operations Metrics
- [ ] Audit Logs

### Doctor
- [x] Appointments List
- [x] Appointment Details
- [ ] Schedule (`GET /doctor/schedule?date=...`)
- [ ] Patient Search (`GET /doctor/patients/search?patient_uid=...`)
- [ ] Patient History (`GET /doctor/patients/{patient_id}/history`)
- [ ] Add Notes (`POST /doctor/appointments/{appointment_id}/notes`)
- [ ] Add Diagnosis (`PUT /doctor/appointments/{appointment_id}/diagnosis`)
- [ ] Issue Prescription (`POST /doctor/appointments/{appointment_id}/prescription`)

### Nurse
- [ ] Appointments List (`GET /nurse/appointments`)
- [ ] Appointment Details (`GET /nurse/appointments/{appointment_id}`)
- [ ] Add Telemetry (`POST /nurse/telemetry`)
- [ ] ICU Telemetry (`GET /nurse/telemetry/icu`)
- [ ] Telemetry Alerts (`GET /nurse/telemetry/alerts`)
- [ ] Rooms (`GET /nurse/rooms`)
- [ ] Equipment (`GET /nurse/equipment`)

### Pharmacy Staff
- [x] Inventory List
- [ ] Restock (`POST /pharmacy/inventory/restock`)
- [ ] Adjust Stock (`PUT /pharmacy/inventory/{item_id}`)
- [ ] Inventory Analytics (`GET /pharmacy/inventory/analytics`)
- [ ] Orders List (`GET /pharmacy/orders?status=...`)
- [ ] Fulfill Order (`PUT /pharmacy/orders/{order_id}/fulfill`)
- [ ] Low Stock (`GET /pharmacy/inventory/low-stock`)

### Patient
- [x] Appointments
- [x] Book Appointment
- [ ] Medical History (`GET /patient/medical-history`)
- [ ] Prescriptions (`GET /patient/prescriptions`)
- [ ] Browse Doctors (`GET /patient/doctors?specialization=...`)

### Receptionist
- [x] Create Patient
- [ ] Update Patient (`PUT /receptionist/patients/{patient_id}`)
- [x] Appointments List
- [ ] Create Appointment (`POST /receptionist/appointments`)
- [ ] Update Appointment (`PUT /receptionist/appointments/{appointment_id}`)
- [ ] Doctor Availability (`GET /receptionist/doctors/availability?doctor_id=...&date=...`)
- [ ] Patient Search (`GET /receptionist/patients/search?query=...`)

### Common
- [x] Branches
- [ ] Rooms (`GET /rooms`)
- [ ] Equipment (`GET /equipment`)

### Billing & Insurance
- [ ] Create Bill (`POST /billing`)
- [ ] Bill Details (`GET /billing/{bill_id}`)
- [ ] Record Payment (`POST /billing/{bill_id}/payment`)
- [ ] Submit Insurance Claim (`POST /insurance/claims`)
- [ ] Claim Details (`GET /insurance/claims/{claim_id}`)
- [ ] Update Claim Status (`PUT /insurance/claims/{claim_id}/status`)

## Query Filters and Parameters

### Using Query Parameters

For endpoints with query parameters like `?status=...` or `?date=...`:

```typescript
const [statusFilter, setStatusFilter] = useState('');

const { data } = useQuery({
  queryKey: ['items', statusFilter], // Include filter in query key
  queryFn: async () => {
    const params = statusFilter ? `?status=${statusFilter}` : '';
    const response = await apiClient.get(`/endpoint${params}`);
    return response.data;
  },
});

// UI for filter
<select
  value={statusFilter}
  onChange={(e) => setStatusFilter(e.target.value)}
  className="px-3 py-2 border border-gray-300 rounded-md"
>
  <option value="">All</option>
  <option value="pending">Pending</option>
  <option value="completed">Completed</option>
</select>
```

### Multiple Filters

```typescript
const [dateFilter, setDateFilter] = useState('');
const [doctorFilter, setDoctorFilter] = useState('');

const { data } = useQuery({
  queryKey: ['appointments', dateFilter, doctorFilter],
  queryFn: async () => {
    const params = new URLSearchParams();
    if (dateFilter) params.append('date', dateFilter);
    if (doctorFilter) params.append('doctor_id', doctorFilter);
    const queryString = params.toString();
    const response = await apiClient.get(
      `/appointments${queryString ? `?${queryString}` : ''}`
    );
    return response.data;
  },
});
```

## Best Practices

1. **Always use Loading/Error/Empty states** - Every data-fetching page must handle all three states

2. **Query keys should include filters** - This enables proper cache invalidation and updates

3. **Use mutations for data changes** - POST, PUT, DELETE operations should use `useMutation`

4. **Invalidate queries after mutations** - Use `queryClient.invalidateQueries()` in `onSuccess`

5. **Handle errors gracefully** - Display server error messages to users

6. **No mock data** - All data must come from the backend API

7. **Respect role boundaries** - Only call endpoints allowed for the user's role

8. **Use proper TypeScript types** - Define interfaces for API responses when possible

9. **Keep forms controlled** - Use useState for form data

10. **Navigation consistency** - Use `useNavigate` for programmatic navigation

## Testing Backend Connection

Before implementing pages, verify the backend is running:

```typescript
// Add to any page temporarily
const { data: health } = useQuery({
  queryKey: ['health'],
  queryFn: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
});
```

If the backend is down, you'll see clear error messages.

## Directory Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx
│   ├── ProtectedRoute.tsx
│   ├── LoadingState.tsx
│   ├── ErrorState.tsx
│   └── EmptyState.tsx
├── context/            # React contexts
│   └── AuthContext.tsx
├── lib/                # Utilities
│   └── api.ts
├── pages/              # Page components by role
│   ├── super-admin/
│   ├── org-admin/
│   ├── branch-admin/
│   ├── doctor/
│   ├── nurse/
│   ├── pharmacy/
│   ├── patient/
│   ├── receptionist/
│   ├── common/
│   ├── LoginPage.tsx
│   ├── UnauthorizedPage.tsx
│   └── HomePage.tsx
├── types/              # TypeScript types
│   └── index.ts
├── App.tsx             # Main routing
└── main.tsx            # Entry point
```

## Next Steps

1. Identify which pages you need for your use case
2. Follow the patterns above to create page components
3. Add routes to `App.tsx`
4. Test with the backend running at `http://localhost:8000`
5. Verify authentication and authorization work correctly

The foundation is complete and production-ready. You can now extend it systematically to cover all remaining endpoints.
