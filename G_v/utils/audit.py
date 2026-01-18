"""
Audit Logging Utility
"""
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session

from models import AuditLog, PatientAccessLog


class AuditLogger:
    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        before_state: Optional[Dict] = None,
        after_state: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log any action to audit log"""
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    
    @staticmethod
    def log_patient_access(
        db: Session,
        patient_id: int,
        accessed_by: int,
        access_type: str,
        access_reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log patient record access (compliance requirement)"""
        access_log = PatientAccessLog(
            patient_id=patient_id,
            accessed_by=accessed_by,
            access_type=access_type,
            access_reason=access_reason,
            ip_address=ip_address,
            accessed_at=datetime.utcnow()
        )
        db.add(access_log)
        db.commit()


audit_logger = AuditLogger()
