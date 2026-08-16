from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.audit import AuditLogCreate
from app.services.audit_service import AuditService
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)


@router.post("/log")
def create_audit_log(
    entry: AuditLogCreate,
    db: Session = Depends(get_db),
):
    record = AuditService.log(db, entry.user, entry.action, entry.details)
    return {
        "success": True,
        "message": "Audit log entry created",
        "log": AuditService.serialize(record),
    }


@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(1000, ge=1, le=10000),
    action: str = Query(None),
):
    user_filter = None if current_user.role == "admin" else current_user.email
    records = AuditService.get_logs(db, limit=limit, action=action, user=user_filter)
    return {
        "success": True,
        "total": len(records),
        "logs": [AuditService.serialize(rec) for rec in records],
    }