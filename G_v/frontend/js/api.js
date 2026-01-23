/**
 * IHORMS API Helper
 * Handles all API communications with the backend
 */

const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    getToken() {
        return localStorage.getItem('access_token');
    }

    setToken(token) {
        localStorage.setItem('access_token', token);
    }

    setRefreshToken(token) {
        localStorage.setItem('refresh_token', token);
    }

    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    }

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    clearAuth() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const token = this.getToken();

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                // Try to refresh token
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    headers['Authorization'] = `Bearer ${this.getToken()}`;
                    const retryResponse = await fetch(url, { ...options, headers });
                    return this.handleResponse(retryResponse);
                } else {
                    this.clearAuth();
                    window.location.href = '/index.html';
                    return null;
                }
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async handleResponse(response) {
        const data = await response.json().catch(() => null);

        if (!response.ok) {
            const error = new Error(data?.detail || 'An error occurred');
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setToken(data.access_token);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }

    // ==================== Auth ====================
    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (data) {
            this.setToken(data.access_token);
            this.setRefreshToken(data.refresh_token);
            this.setUser(data.user);
        }

        return data;
    }

    async logout() {
        // await this.request('/auth/logout', { method: 'POST' }).catch(() => {}); // Optional
        this.clearAuth();
    }

    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // ==================== Super Admin ====================
    async getOrganizations() {
        return this.request('/super-admin/organizations');
    }

    async createOrganization(data) {
        return this.request('/super-admin/organizations', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async disableOrganization(orgId) {
        return this.request(`/super-admin/organizations/${orgId}/toggle`, {
            method: 'PATCH'
        });
    }

    async enableOrganization(orgId) {
        return this.request(`/super-admin/organizations/${orgId}/toggle`, {
            method: 'PATCH'
        });
    }

    async getPlatformAnalytics() {
        return this.request('/super-admin/analytics');
    }

    // ==================== Org Admin ====================
    async getBranches() {
        return this.request('/org-admin/branches');
    }

    async createBranch(data) {
        return this.request('/org-admin/branches', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getOrgStaff(role = null, page = 1) {
        let url = `/org-admin/staff?page=${page}`;
        if (role) url += `&role=${role}`;
        return this.request(url);
    }

    async createDoctor(branchId, data) {
        return this.request(`/org-admin/doctors?branch_id=${branchId}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getOrgAnalytics() {
        return this.request('/org-admin/analytics');
    }

    async toggleStaffAccess(userId) {
        return this.request(`/org-admin/staff/${userId}/toggle`, {
            method: 'POST'
        });
    }

    async getBillingAnalytics(months = 6) {
        return this.request(`/org-admin/billing-analytics?months=${months}`);
    }

    // ==================== Doctor ====================
    async getDoctorAppointments() {
        return this.request('/doctor/appointments');
    }

    async getAppointmentDetail(id) {
        return this.request(`/doctor/appointments/${id}`);
    }

    async getDoctorSchedule(date) {
        return this.request(`/doctor/schedule?schedule_date=${date}`);
    }

    async acceptAppointment(appointmentId) {
        return this.request(`/doctor/appointments/${appointmentId}/accept`, {
            method: 'POST'
        });
    }

    async addDoctorNotes(appointmentId, data) {
        return this.request(`/doctor/appointments/${appointmentId}/notes`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async searchPatient(uid) {
        return this.request(`/doctor/patients/search?uid=${uid}`);
    }

    async getPatientHistory(patientId) {
        return this.request(`/doctor/patients/${patientId}/history`);
    }

    async admitPatient(appointmentId, roomType) {
        return this.request(`/doctor/appointments/${appointmentId}/admit?room_type=${roomType}`, {
            method: 'POST'
        });
    }

    // ==================== Branch Admin ====================
    async getBranchAnalytics() {
        return this.request('/branch-admin/analytics');
    }

    async getBranchStaff() {
        return this.request('/branch-admin/staff');
    }

    async createBranchDoctor(data) {
        return this.request('/branch-admin/doctors', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async createBranchNurse(data) {
        return this.request('/branch-admin/nurses', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async createBranchReceptionist(data) {
        return this.request('/branch-admin/receptionists', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async createBranchPharmacy(data) {
        return this.request('/branch-admin/pharmacy', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async disableStaff(userId) {
        return this.request(`/branch-admin/staff/${userId}/disable`, {
            method: 'POST'
        });
    }

    async getDoctorAccessLogs() {
        return this.request('/branch-admin/access-logs');
    }

    // ==================== Nurse ====================
    async getNurseAppointments() {
        return this.request('/nurse/appointments');
    }

    async getWardRooms() {
        return this.request('/nurse/rooms');
    }

    async addTelemetry(data) {
        return this.request('/nurse/telemetry', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // ==================== Receptionist ====================
    async createPatient(data) {
        return this.request('/receptionist/patients', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async searchPatients(query = '') {
        return this.request(`/receptionist/patients/search?query=${query}`);
    }

    async createAppointment(data) {
        return this.request('/receptionist/appointments', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async rescheduleAppointment(appointmentId, data) {
        return this.request(`/receptionist/appointments/${appointmentId}/reschedule`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async confirmAppointment(appointmentId) {
        return this.request(`/receptionist/appointments/${appointmentId}/confirm`, {
            method: 'POST'
        });
    }

    async getReceptionistAppointments(date = null, status = null) {
        let url = '/receptionist/appointments?';
        if (date) url += `date=${date}&`;
        if (status) url += `status=${status}`;
        return this.request(url);
    }

    async getBranchDoctors() {
        return this.request('/receptionist/doctors');
    }

    async getRecommendedDoctors(symptoms) {
        return this.request(`/receptionist/doctors/recommend?symptoms=${encodeURIComponent(symptoms)}`);
    }

    // ==================== Pharmacy ====================
    async getInventory(lowStockOnly = false) {
        let url = '/pharmacy/inventory';
        return this.request(url);
    }

    async restockItem(itemId, quantity) {
        return this.request(`/pharmacy/inventory/${itemId}/restock?quantity=${quantity}`, {
            method: 'POST'
        });
    }

    async getPendingOrders() {
        return this.request('/pharmacy/orders/pending');
    }

    async fulfillOrder(orderId) {
        return this.request(`/pharmacy/orders/${orderId}/fulfill`, {
            method: 'POST'
        });
    }

    async getPharmaInsights() {
        return this.request('/pharmacy/insights');
    }

    // ==================== Patient Portal ====================
    async getMyProfile() {
        return this.request('/patient-portal/profile');
    }

    async getMyMedicalHistory() {
        return this.request('/patient-portal/history');
    }

    async getMyAppointments() {
        return this.request('/patient-portal/appointments');
    }

    async bookAppointment(data) {
        // Adjust parameters for backend: doctor_id, appointment_date, appointment_time, chief_complaint
        const url = `/patient-portal/appointments/book?doctor_id=${data.doctor_id}&appointment_date=${data.appointment_date}&appointment_time=${data.appointment_time}&chief_complaint=${data.chief_complaint || ''}`;
        return this.request(url, {
            method: 'POST'
        });
    }

    async getAvailableDoctors() {
        return this.request('/patient-portal/doctors');
    }

    async getRecommendedDoctorsForSymptoms(symptoms) {
        return this.request(`/patient-portal/doctors/recommend?symptoms=${encodeURIComponent(symptoms)}`);
    }

    // ==================== Billing ====================
    async getMyBills() {
        return this.request('/billing/my-bills');
    }

    async payBill(billingId, paymentMethod) {
        return this.request(`/billing/my-bills/${billingId}/pay?payment_method=${paymentMethod}`, {
            method: 'POST'
        });
    }

    async claimInsurance(billingId, insuranceProvider, policyNumber) {
        return this.request(`/billing/my-bills/${billingId}/insurance?insurance_provider=${insuranceProvider}&policy_number=${policyNumber}`, {
            method: 'POST'
        });
    }

    async createBill(data) {
        return this.request('/billing/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async requestDischarge(admissionId, notes) {
        return this.request(`/billing/discharge/request?admission_id=${admissionId}&discharge_notes=${notes}`, {
            method: 'POST'
        });
    }

    async approveDischarge(admissionId, approved, summary) {
        return this.request(`/billing/discharge/approve/${admissionId}?approved=${approved}&discharge_summary=${summary}`, {
            method: 'POST'
        });
    }
}

// Global API instance
const api = new ApiClient();
