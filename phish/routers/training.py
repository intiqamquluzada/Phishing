from typing import List

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from phish.dependencies import get_db
from phish.models.training import Training

from phish.models.users import User as UserModel
from phish.schemas.training import TrainingBase
from phish.utils.uid import encode_uid, decode_uid
from phish.utils.email import send_email
import uuid
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/trainings",
    tags=["Training"]
)

@router.get("", response_model=List[TrainingBase],
            summary="List of trainings", description="List of trainings")
async def get_trainings(db: Session = Depends(get_db)):
    trainings = db.query(Training).all()

    if not trainings:
        raise HTTPException(status_code=404, detail="No trainings found")

    return trainings