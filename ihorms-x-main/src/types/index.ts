export type Role =
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
  role: Role;
  organization_id?: string;
  branch_id?: string;
  [key: string]: unknown;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
