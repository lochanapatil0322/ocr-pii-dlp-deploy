import os
import shutil
import hashlib
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.document import Document
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(
    prefix="/document",
    tags=["Document Features"]
)

UPLOAD_FOLDER = "uploads"


class OwnershipTracker:
    def __init__(self):
        self.records = []

    def add_record(self, filename, user, action):
        record = {
            "filename": filename,
            "user": user,
            "action": action,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.records.append(record)
        return record

    def get_records(self):
        return self.records


class DocumentClassifier:
    def __init__(self):
        self.rules = {
            "secret": "Secret",
            "confidential": "Confidential",
            "internal": "Internal",
            "public": "Public"
        }

    def classify(self, text):
        text_lower = text.lower()
        for keyword, level in self.rules.items():
            if keyword in text_lower:
                return {"success": True, "classification": level}
        return {"success": True, "classification": "Public"}


class RiskAccessControl:
    def __init__(self):
        self.risk_levels = {
            "low": ["viewer", "employee", "manager", "admin"],
            "medium": ["manager", "admin"],
            "high": ["admin"]
        }

    def check_access(self, user_role, risk_level):
        user_role = user_role.lower()
        risk_level = risk_level.lower()
        allowed = self.risk_levels.get(risk_level, [])
        if user_role in allowed:
            return {"success": True, "access": "Granted", "role": user_role, "risk_level": risk_level}
        return {"success": False, "access": "Denied", "role": user_role, "risk_level": risk_level}


class AuditLogger:
    def __init__(self):
        self.logs = []

    def add_log(self, user, action, document):
        log = {
            "user": user,
            "action": action,
            "document": document,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.logs.append(log)
        return {"success": True, "message": "Audit log added.", "log": log}

    def get_logs(self):
        return {"success": True, "total_logs": len(self.logs), "logs": self.logs}



ownership_tracker = OwnershipTracker()
classifier = DocumentClassifier()
risk_controller = RiskAccessControl()
audit_logger = AuditLogger()

@router.post("/watermark/check")
async def watermark_check(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        import cv2
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = "tesseract"
        image = cv2.imread(file_path)
        if image is None:
            return {"success": False, "message": f"Cannot read image: {file_path}"}
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return {"success": True, "ocr_text": text}
    except ImportError:
        return {"success": False, "message": "opencv-python not installed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/signature/verify")
async def verify_signature(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        signatures = []
        if "/AcroForm" in reader.trailer["/Root"]:
            form = reader.trailer["/Root"]["/AcroForm"]
            if "/Fields" in form:
                for field in form["/Fields"]:
                    obj = field.get_object()
                    if obj.get("/FT") == "/Sig":
                        signatures.append({
                            "field_name": obj.get("/T", "Unknown"),
                            "status": "Signature Found"
                        })
        return {"success": True, "signed": len(signatures) > 0, "signature_count": len(signatures), "signatures": signatures}
    except ImportError:
        return {"success": False, "message": "pypdf not installed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/tamper-check")
async def tamper_check(file: UploadFile = File(...), original_hash: str = Form(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    current_hash = sha256.hexdigest()
    return {"success": True, "tampered": current_hash != original_hash, "original_hash": original_hash, "current_hash": current_hash}


@router.post("/classify")
async def classify_document(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    return classifier.classify(text)


@router.post("/upload-with-ownership")
async def upload_with_ownership(user: str = Form(...), file: UploadFile = File(...)):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    record = ownership_tracker.add_record(filename=file.filename, user=user, action="Uploaded")
    return {"success": True, "message": "Upload Successful", "record": record}


@router.get("/ownership/history")
def ownership_history():
    return {"success": True, "history": ownership_tracker.get_records()}


@router.post("/access/check")
def check_access(user_role: str = Form(...), risk_level: str = Form(...)):
    return risk_controller.check_access(user_role, risk_level)


@router.post("/audit/log")
def add_audit_log(user: str = Form(...), action: str = Form(...), document: str = Form(...)):
    return audit_logger.add_log(user, action, document)


@router.get("/audit/logs")
def get_audit_logs():
    return audit_logger.get_logs()


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = db.query(Document)
    if current_user.role != "admin":
        base_query = base_query.filter(Document.uploaded_by == current_user.email)

    return {
        "success": True,
        "dashboard": {
            "total_documents": base_query.count(),
            "classified_documents": base_query.filter(Document.classification.isnot(None)).count(),
            "watermark_detected": base_query.filter(Document.watermark_detected.is_(True)).count(),
            "tampered_documents": base_query.filter(Document.tampered.is_(True)).count(),
            "risk_documents": base_query.filter(Document.risk_level.in_(["HIGH", "CRITICAL"])).count(),
            "expired_documents": base_query.filter(
                Document.expiry_date.isnot(None),
                Document.expiry_date < datetime.utcnow()
            ).count(),
        },
    }