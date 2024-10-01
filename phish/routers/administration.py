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


@router.post("/send-invite")
async def send_invite(email: SendInvite,
                      request: Request,
                      db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    scheme = request.url.scheme
    host = request.client.host
    domain_url = f"{scheme}://{host}"

    code = str(uuid.uuid4())
    user.verification_code = code

    db.commit()
    db.refresh(user)

    uid = encode_uid(user.id)

    link = f"{domain_url}/invitation-request/{uid}/{code}"
    subject = "Invitation Request"
    recipient = email.email
    message = f"Click on the link below to accept or decline the invitation: \n{link}"

    await send_email(subject, [recipient], message)

    Invite(
        user_id=user.id,
    )

    return JSONResponse({"message": "Invitation sent successfully"}, status_code=250)
