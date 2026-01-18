/**
 * Authentication Handler
 */

class AuthManager {
    constructor() {
        this.checkAuth();
    }

    checkAuth() {
        const token = localStorage.getItem('access_token');
        const user = localStorage.getItem('user');

        if (!token || !user) {
            if (!window.location.pathname.includes('index.html') &&
                window.location.pathname !== '/' &&
                !window.location.pathname.endsWith('G_v/frontend/')) {
                window.location.href = '/index.html';
            }
            return false;
        }
        return true;
    }

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    getRole() {
        const user = this.getUser();
        return user ? user.role : null;
    }

    redirectToDashboard() {
        const role = this.getRole();
        const dashboards = {
            'super_admin': '/pages/super-admin.html',
            'org_admin': '/pages/org-admin.html',
            'branch_admin': '/pages/branch-admin.html',
            'doctor': '/pages/doctor.html',
            'nurse': '/pages/nurse.html',
            'receptionist': '/pages/receptionist.html',
            'pharmacy_staff': '/pages/pharmacy.html',
            'patient': '/pages/patient.html'
        };

        const dashboard = dashboards[role];
        if (dashboard) {
            window.location.href = dashboard;
        } else {
            console.error('Unknown role:', role);
        }
    }

    logout() {
        api.logout();
        window.location.href = '/index.html';
    }
}

const auth = new AuthManager();
