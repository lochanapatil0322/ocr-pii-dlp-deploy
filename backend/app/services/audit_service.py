from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    """Persistent, timestamped audit logging backed by SQLAlchemy."""

    @staticmethod
    def log(db: Session, user: str, action: str, details: str = ""):
        entry = AuditLog(
            user=user or "system",
            action=action,
            details=details or "",
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_logs(db: Session, limit: int = 1000, action: str = None, user: str = None):
        query = db.query(AuditLog)
        if action:
            query = query.filter(AuditLog.action == action)
        if user:
            query = query.filter(AuditLog.user == user)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def serialize(entry: AuditLog):
        created = entry.created_at
        if isinstance(created, datetime):
            created = created.isoformat() + "Z"
        return {
            "id": entry.id,
            "user": entry.user,
            "action": entry.action,
            "details": entry.details,
            "created_at": str(created),
        };