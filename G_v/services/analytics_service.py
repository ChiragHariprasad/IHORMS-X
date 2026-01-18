"""
Analytics Service - Handles reporting and dashboards
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal

from models import (
    Organization, Branch, User, Patient, Appointment, 
    Billing, UserRole, AppointmentStatus, Room, Equipment
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Aggregate data for Super Admin"""
        orgs = self.db.query(Organization).all()
        
        org_data = []
        for org in orgs:
            user_count = self.db.query(User).filter(User.organization_id == org.id).count()
            branch_count = self.db.query(Branch).filter(Branch.organization_id == org.id).count()
            appointment_count = self.db.query(Appointment).join(Patient).filter(
                Patient.organization_id == org.id
            ).count()
            
            billing_total = self.db.query(func.sum(Billing.total_amount)).join(Patient).filter(
                Patient.organization_id == org.id
            ).scalar() or 0
            
            org_data.append({
                "id": org.id,
                "name": org.name,
                "users": user_count,
                "branches": branch_count,
                "appointments": appointment_count,
                "billing_total": float(billing_total)
            })
            
        return {
            "total_organizations": len(orgs),
            "active_organizations": self.db.query(Organization).filter(Organization.is_active == True).count(),
            "total_branches": self.db.query(Branch).count(),
            "total_users": self.db.query(User).count(),
            "total_patients": self.db.query(Patient).count(),
            "total_appointments": self.db.query(Appointment).count(),
            "organizations": org_data
        }
    
    def get_organization_analytics(self, org_id: int) -> Dict[str, Any]:
        """Aggregate data for Org Admin"""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        branch_count = self.db.query(Branch).filter(Branch.organization_id == org_id).count()
        staff_count = self.db.query(User).filter(
            User.organization_id == org_id, 
            User.role != UserRole.PATIENT
        ).count()
        patient_count = self.db.query(Patient).filter(Patient.organization_id == org_id).count()
        
        billing_total = self.db.query(func.sum(Billing.total_amount)).join(Patient).filter(
            Patient.organization_id == org_id
        ).scalar() or 0
        
        # Staff distribution
        dist = self.db.query(User.role, func.count(User.id)).filter(
            User.organization_id == org_id
        ).group_by(User.role).all()
        
        staff_dist = {role.value: count for role, count in dist}
        
        return {
            "organization_id": org_id,
            "organization_name": org.name,
            "total_branches": branch_count,
            "total_staff": staff_count,
            "total_patients": patient_count,
            "total_appointments": self.db.query(Appointment).join(Patient).filter(
                Patient.organization_id == org_id
            ).count(),
            "billing_summary": {"total_revenue": float(billing_total)},
            "staff_distribution": staff_dist
        }
    
    def get_branch_analytics(self, branch_id: int) -> Dict[str, Any]:
        """Aggregate data for Branch Admin"""
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        
        doc_count = self.db.query(User).filter(User.branch_id == branch_id, User.role == UserRole.DOCTOR).count()
        nurse_count = self.db.query(User).filter(User.branch_id == branch_id, User.role == UserRole.NURSE).count()
        
        # Appointments
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        app_today = self.db.query(Appointment).join(Patient).filter(
            Patient.branch_id == branch_id,
            Appointment.appointment_date == today
        ).count()
        
        app_week = self.db.query(Appointment).join(Patient).filter(
            Patient.branch_id == branch_id,
            Appointment.appointment_date >= week_ago
        ).count()
        
        return {
            "branch_id": branch_id,
            "branch_name": branch.name,
            "total_doctors": doc_count,
            "total_nurses": nurse_count,
            "total_patients": self.db.query(Patient).filter(Patient.branch_id == branch_id).count(),
            "appointments_today": app_today,
            "appointments_this_week": app_week,
            "room_occupancy": {
                "total": self.db.query(Room).filter(Room.branch_id == branch_id).count(),
                "available": self.db.query(Room).filter(Room.branch_id == branch_id, Room.is_available == True).count()
            }
        }
