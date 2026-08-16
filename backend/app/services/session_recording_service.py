import os
import uuid

import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import Session

from app.models.session_recording import SessionRecording

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)


class SessionRecordingService:

    def save_recording(self, db: Session, user: str, document: str, file):

        filename = f"{uuid.uuid4().hex}.webm"

        upload_result = cloudinary.uploader.upload(
            file.file,
            resource_type="video",
            public_id=f"recordings/{filename}",
            folder="recordings",
        )
        permanent_url = upload_result["secure_url"]

        entry = SessionRecording(
            user=user,
            document=document,
            filename=filename,
            url=permanent_url,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)

        return {
            "success": True,
            "message": "Session recording saved",
            "record": {
                "user": entry.user,
                "document": entry.document,
                "filename": entry.filename,
                "url": entry.url,
                "recorded_at": entry.created_at.isoformat() + "Z",
            },
        }

    def get_recordings(self, db: Session):

        records = (
            db.query(SessionRecording)
            .order_by(SessionRecording.created_at.desc())
            .all()
        )

        return {
            "total_recordings": len(records),
            "recordings": [
                {
                    "user": r.user,
                    "document": r.document,
                    "filename": r.filename,
                    "url": r.url,
                    "recorded_at": r.created_at.isoformat() + "Z",
                }
                for r in records
            ],
        }