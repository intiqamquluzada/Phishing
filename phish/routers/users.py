import pyotp
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import json
from io import BytesIO
import qrcode
from fastapi.responses import StreamingResponse

from ..database import get_db
from phish.external_services.mfa_helpers import generate_mfa_secret, generate_backup_codes, use_backup_code, \
    verify_mfa_token, mfa_dependency
from phish.routers import auth

from phish.models.users import User as UserModel
from phish.schemas.users import User, UserCreate, ForgotPassword, ForgotPasswordConfirm, Token, TokenData
from phish.models.role import Role
import sqlalchemy
from phish.utils.uid import encode_uid, decode_uid
from phish.utils.email_sender import send_email_with_tracking, send_email
import uuid
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
security = HTTPBearer()


@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(
        UserModel.email == user.email
    ).first()

    db_role = db.query(Role).filter(Role.id == user.role_id).first()

    if db_user:
        return JSONResponse(status_code=400, content={"message": "Email already registered"})
    if not db_role:
        return JSONResponse(status_code=404, content={"message": "Role not found"})

    hashed_password = auth.get_password_hash(user.password)
    db_user = UserModel(email=user.email, hashed_password=hashed_password, role=db_role)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        return JSONResponse(status_code=400, content={"message": "Integrity error: this email may already exist"})

    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
        token: str = None  # MFA token passed optionally
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If MFA is enabled, verify the token
    if user.mfa_enabled and not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA token required",
        )
    if user.mfa_enabled and not verify_mfa_token(user.mfa_secret, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token",
        )

    access_token_expires = timedelta(days=auth.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role_id": user.role_id}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id
    }


@router.get("/users/me", response_model=User)
async def read_users_me(
        current_user: User = Depends(mfa_dependency)
):
    return current_user


@router.post("/forgot-password-confirm/{uid}/{code}")
async def forgot_password_confirm(
        uid: str,
        code: str,
        password: ForgotPasswordConfirm,
        db: Session = Depends(get_db),
        current_user: User = Depends(mfa_dependency),  # Add MFA validation
):
    pk = decode_uid(uid)
    get_user = db.query(UserModel).filter(UserModel.id == pk, UserModel.verification_code == code).first()

    if get_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if password.password != password.password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    get_user.hashed_password = auth.pwd_context.hash(password.password)
    db.commit()
    db.refresh(get_user)

    return JSONResponse(
        {'message': 'Password has been reset successfully.'},
        status_code=status.HTTP_200_OK
    )


@router.post("/forgot-password-confirm/{uid}/{code}")
async def forgot_password_confirm(uid: str, code: str, password: ForgotPasswordConfirm, db: Session = Depends(get_db)):
    pk = decode_uid(uid)
    get_user = db.query(UserModel).filter(UserModel.id == pk, UserModel.verification_code == code).first()

    if get_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if password.password != password.password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    get_user.hashed_password = auth.pwd_context.hash(password.password)
    db.commit()
    db.refresh(get_user)

    return JSONResponse({'message': 'Password has been reset successfully.'}, status_code=status.HTTP_200_OK)


@router.post("/enable-mfa/")
def enable_mfa(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is already enabled")

    # Generate MFA secret and backup codes
    secret = generate_mfa_secret()
    backup_codes = generate_backup_codes()

    # Save in the database
    user.mfa_secret = secret
    user.mfa_backup_codes = json.dumps(backup_codes)
    user.mfa_enabled = True
    db.commit()

    # Generate QR Code
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user.email, issuer_name="YourApp")
    qr = qrcode.make(uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


@router.post("/verify-mfa/")
def verify_mfa(user_id: int, token: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=404, detail="MFA is not enabled for this user")

    if verify_mfa_token(user.mfa_secret, token):
        return {"message": "MFA verification successful"}

    raise HTTPException(status_code=401, detail="Invalid MFA token")


@router.post("/use-backup-code/")
def use_backup_code_route(user_id: int, code: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=404, detail="MFA is not enabled for this user")

    valid, updated_codes = use_backup_code(user.mfa_backup_codes, code)
    if valid:
        user.mfa_backup_codes = updated_codes
        db.commit()
        return {"message": "Backup code used successfully"}

    raise HTTPException(status_code=401, detail="Invalid backup code")


@router.post("/disable-mfa/")
def disable_mfa(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.mfa_enabled = False
    user.mfa_secret = None
    user.mfa_backup_codes = None
    db.commit()

    return {"message": "MFA disabled successfully"}
