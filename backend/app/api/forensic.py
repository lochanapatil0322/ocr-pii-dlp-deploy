from fastapi import APIRouter, Form, File, UploadFile, Depends
from sqlalchemy.orm import Session

from app.services.forensic_service import ForensicService
from app.services.session_recording_service import SessionRecordingService
from app.database.database import get_db
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(
    prefix="/forensic",
    tags=["Forensic Investigation"]
)

recording_service = SessionRecordingService()


@router.post("/record")
def create_record(
    user: str = Form(...),
    action: str = Form(...),
    document: str = Form(...),
    db: Session = Depends(get_db),
):
    return ForensicService.create_forensic_record(db, user, action, document)


@router.get("/logs")
def get_forensic_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_filter = None if current_user.role == "admin" else current_user.email
    return ForensicService.get_forensic_logs(db, user=user_filter)


@router.post("/record-session")
def record_session(
    user: str = Form(...),
    document: str = Form("Live Session"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    result = recording_service.save_recording(db, user, document, file)
    ForensicService.create_forensic_record(db, user, "SESSION_RECORDED", document)
    return result


@router.get("/recordings")
def list_recordings(db: Session = Depends(get_db)):
    return recording_service.get_recordings(db)