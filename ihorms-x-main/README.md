# IHORMS-X Frontend

Production-ready frontend for IHORMS-X Hospital Management System built with React, TypeScript, and Vite.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **TanStack Query** - Data fetching and caching
- **React Hook Form + Zod** - Form handling and validation

## Prerequisites

- Node.js 18+ and npm
- Running FastAPI backend at `http://localhost:8000`

## Installation

```bash
npm install
```

## Running the App

```bash
npm run dev
```

The app will run at `http://localhost:5173` (or next available port).

## Project Structure

```
src/
├── components/        # Reusable UI components
├── context/          # React context providers (Auth)
├── lib/              # API client and utilities
├── pages/            # Page components organized by role
│   ├── super-admin/
│   ├── org-admin/
│   ├── branch-admin/
│   ├── doctor/
│   ├── nurse/
│   ├── pharmacy/
│   ├── patient/
│   ├── receptionist/
│   └── common/
├── types/            # TypeScript type definitions
├── App.tsx           # Main app with routing
└── main.tsx          # App entry point
```

## Features

### Authentication
- JWT-based authentication with Bearer tokens
- Automatic token refresh and logout on 401
- Protected routes with role-based access control

### Role-Based Access Control
Supports 8 user roles with dedicated UIs:
- **Super Admin** - Organization management and platform analytics
- **Org Admin** - Staff management and org-level analytics
- **Branch Admin** - Branch staff and operations management
- **Doctor** - Appointments, patient history, clinical actions
- **Nurse** - Appointment support, telemetry, resources
- **Pharmacy Staff** - Inventory and order management
- **Patient** - Medical records, appointments, prescriptions
- **Receptionist** - Patient and appointment coordination

### API Integration
- All data fetched from FastAPI backend at `http://localhost:8000/api`
- No mock data - real-time backend integration
- Comprehensive error handling and loading states
- Empty state handling for all lists/tables

### UI/UX
- Clean, professional design with sidebar navigation
- Responsive layout
- Loading, error, and empty states for all data
- Form validation with clear error messages
- Role-based navigation menu

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript type checking

## API Backend Requirements

The frontend expects a FastAPI backend running at:
- **Base URL**: `http://localhost:8000/api`
- **Auth**: JWT Bearer token from `POST /api/auth/login`

If the backend is down, a clear error banner will be displayed.

## Environment

The API base URL is hardcoded to `http://localhost:8000/api`. To change this, modify `src/lib/api.ts`.

## Role Navigation Patterns

Each role has a default landing page:
- Super Admin → Organizations list
- Org Admin → Staff directory
- Branch Admin → Branch staff
- Doctor → My appointments
- Nurse → Appointments
- Receptionist → Appointments
- Pharmacy Staff → Inventory
- Patient → My appointments

## Security

- JWT tokens stored in localStorage under `ihorms_token`
- Automatic token injection via Axios interceptor
- Auto-logout on 401 responses
- Role-based route protection at component level

## Development Notes

- Uses React Query for efficient data caching
- All API calls include loading/error/empty state handling
- Forms use controlled components with validation
- No hardcoded data - all content from backend API
- Sidebar menu items generated dynamically from user role
