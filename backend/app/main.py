from app.api.policy_alerts import router as policy_alert_router
from app.api.email_dlp import router as email_dlp_router
from app.api.clipboard import router as clipboard_router
from app.api.print_control import router as print_control_router
from app.api.usb_control import router as usb_control_router
from app.api.shadow_ai import router as shadow_ai_router
from app.api.ueba import router as ueba_router
from app.api.forensic import router as forensic_router
from app.api.document_features import router as document_features_router
from app.api.reports import router as reports_router
from app.api.audit import router as audit_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.encryption import router as encryption_router

from app.database.database import engine
from app.database.base import Base
from app.api.auth import router as auth_router
from app.api.upload import router as upload_router
from app.api.ocr import router as ocr_router
from app.api.pii import router as pii_router
from app.api.qr_barcode import router as qr_barcode_router
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OCR-Based DLP Backend",
    description="Backend API for OCR-Based Data Loss Prevention System",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ocr-pii-dlp-deploy.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(ocr_router, prefix="/api")
app.include_router(pii_router, prefix="/api")
app.include_router(policy_alert_router, prefix="/api")
app.include_router(email_dlp_router, prefix="/api")
app.include_router(clipboard_router, prefix="/api")
app.include_router(print_control_router, prefix="/api")
app.include_router(usb_control_router, prefix="/api")
app.include_router(shadow_ai_router, prefix="/api")
app.include_router(ueba_router, prefix="/api")
app.include_router(forensic_router, prefix="/api")
app.include_router(document_features_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(encryption_router, prefix="/api")
app.include_router(qr_barcode_router, prefix="/api")
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

@app.get("/")
def root():
    return {
        "message": "OCR-Based DLP Backend is Running Successfully!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "server": "running",
        "version": "1.0.0"
    }