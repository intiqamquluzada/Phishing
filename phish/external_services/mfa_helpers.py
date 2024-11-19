import pyotp
import secrets
import json
from fastapi import Depends, HTTPException, status

from phish.database import SessionLocal
from phish.models.users import User as UserModel
from ..database import get_db
from phish.routers.auth import get_current_user
from sqlalchemy.orm import Session


def mfa_dependency(
    user: UserModel = Depends(get_current_user),
    token: str = None,
    db: Session = Depends(get_db),
):
    if user.mfa_enabled:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA token required",
            )
        if not verify_mfa_token(user.mfa_secret, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token",
            )
    return user

def generate_mfa_secret():
    return pyotp.random_base32()


def generate_backup_codes(count=5):
    return [secrets.token_hex(8) for _ in range(count)]


def verify_mfa_token(mfa_secret: str, token: str) -> bool:
    totp = pyotp.TOTP(mfa_secret)
    return totp.verify(token)


def use_backup_code(backup_codes: str, code: str) -> (bool, str):
    codes = json.loads(backup_codes)
    if code in codes:
        codes.remove(code)
        return True, json.dumps(codes)
    return False, backup_codes
