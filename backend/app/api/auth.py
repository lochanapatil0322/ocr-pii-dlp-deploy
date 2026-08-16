from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from datetime import datetime, timedelta, UTC
from app.schemas.user import (
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
)
from app.services.otp_service import generate_otp, send_otp_email

from app.schemas.user import (
    UserRegister,
    UserResponse,
    UserLogin,
)

from app.schemas.token import Token

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -------------------------
# Get Current Logged-in User
# -------------------------
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# -------------------------
# Register User
# -------------------------
@router.post("/register", response_model=UserResponse)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    AuditService.log(
        db,
        new_user.email,
        "USER_REGISTERED",
        "Account created for username '%s'" % new_user.username,
    )

    return new_user


# -------------------------
# Login User
# -------------------------
@router.post(
    "/login",
    response_model=Token
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user by email
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    # Email not found
    if db_user is None:
        AuditService.log(
            db,
            user.email,
            "LOGIN_FAILED",
            "Login attempt with unknown email",
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    # Verify password
    if not verify_password(
        user.password,
        db_user.password
    ):
        AuditService.log(
            db,
            user.email,
            "LOGIN_FAILED",
            "Invalid password supplied for account",
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    # Create JWT Access Token
    access_token = create_access_token(
        data={
            "sub": db_user.email
        }
    )

    AuditService.log(
        db,
        db_user.email,
        "USER_LOGIN",
        "User logged in successfully",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
# -------------------------
# Forgot Password - Send OTP
# -------------------------
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == data.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp = generate_otp()
    db_user.otp_code = otp
    db_user.otp_expiry = datetime.now(UTC) + timedelta(minutes=10)
    db.commit()

    send_otp_email(db_user.email, otp)

    AuditService.log(
        db,
        db_user.email,
        "OTP_SENT",
        "Password reset OTP sent",
    )

    return {"message": "OTP sent to your email"}


# -------------------------
# Verify OTP
# -------------------------
@router.post("/verify-otp")
def verify_otp(
    data: VerifyOtpRequest,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == data.email).first()

    if not db_user or db_user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if db_user.otp_expiry.replace(tzinfo=UTC) < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified"}


# -------------------------
# Reset Password
# -------------------------
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == data.email).first()

    if not db_user or db_user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if db_user.otp_expiry.replace(tzinfo=UTC) < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="OTP expired")

    db_user.password = hash_password(data.new_password)
    db_user.otp_code = None
    db_user.otp_expiry = None
    db.commit()

    AuditService.log(
        db,
        db_user.email,
        "PASSWORD_RESET",
        "Password reset successfully",
    )

    return {"message": "Password reset successful"}