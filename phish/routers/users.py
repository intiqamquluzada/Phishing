from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from models.users import User
from schemas.users import UserCreate
from database import SessionLocal, engine
from dependencies import get_db
import auth

router = APIRouter()
security = HTTPBearer()

@router("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = auth.get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


