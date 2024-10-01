from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form, status, Request
from fastapi.responses import JSONResponse
from phish.dependencies import get_db
from phish.models.users import User
from phish.models.administration import Administration, Invite
from phish.schemas.administration import AdministrationBase, AdministrationResponse, SendInvite
from phish.utils.uid import encode_uid, decode_uid
from phish.utils.email_sender import send_email
from enum import Enum as PyEnum
from typing import List
import uuid


router = APIRouter(
    prefix="/administration",
    tags=["Administration"]
)


@router.get("/",
            response_model=AdministrationResponse,
            summary="List of Users",
            description="List of Users")
async def administration_list(db: Session = Depends(get_db)):
    administration = db.query(Administration).all()

    if not administration:
        raise HTTPException(status_code=404, detail="User not found")

    return administration
