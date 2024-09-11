from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from phish.dependencies import get_db
from phish.routers import auth
from phish.routers.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from phish.models.users import User as UserModel
from phish.schemas.users import User, UserCreate, ForgotPassword, ForgotPasswordConfirm, Token, TokenData
import sqlalchemy
from sqlalchemy import or_
from phish.utils.uid import encode_uid, decode_uid
from phish.utils.email import send_email
import uuid
from fastapi.responses import JSONResponse

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(
        UserModel.email == user.email
    ).first()

    if db_user:
        return JSONResponse(status_code=400, content={"message": "Email already registered"})

    hashed_password = auth.get_password_hash(user.password)
    db_user = UserModel(email=user.email, hashed_password=hashed_password)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        return JSONResponse(status_code=400, content={"message": "Integrity error: this email may already exist"})

    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=auth.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=auth.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = auth.create_access_token(data={"sub": token_data.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user


@router.post("/forgot-password")
async def forgot_password(email: ForgotPassword, request: Request, db: Session = Depends(get_db)):
    get_user = db.query(UserModel).filter(UserModel.email == email.email).first()

    if get_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    scheme = request.url.scheme
    host = request.client.host
    domain_url = f"{scheme}://{host}"

    code = str(uuid.uuid4())

    get_user.verification_code = code
    db.commit()
    db.refresh(get_user)

    uid = encode_uid(get_user.id)

    link = f"{domain_url}/reset-password-confirm/{uid}/{code}"

    subject = "Reset Password"
    print(email.email)
    recipient = email.email

    message = f"Please click on the link below to reset your password: \n{link}"

    await send_email(subject, [recipient], message)

    return JSONResponse(
        {"message": "We have sent a link to your email address to reset your password."},
        status_code=200
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