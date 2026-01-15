export type UserRole = 
  | 'super_admin'
  | 'org_admin'
  | 'branch_admin'
  | 'doctor'
  | 'nurse'
  | 'receptionist'
  | 'pharmacy_staff'
  | 'patient';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  full_name?: string;
  organization_id?: string;
  branch_id?: string;
  is_active?: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
