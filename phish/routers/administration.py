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

    check_administration = db.query(Administration).filter(user == user).first()
    if check_administration.status == "ACTIVE":
        raise HTTPException(status_code=404, detail="User is already in campaign")
    if check_administration.status == "INVITED":
        db.delete(check_administration)
        db.commit()

    check_invite = db.query(Invite).filter(user == user).first()
    if check_invite:
        db.delete(check_invite)
        db.commit()

    scheme = request.url.scheme
    host = request.client.host
    domain_url = f"{scheme}://{host}"

    code = str(uuid.uuid4())
    uid = encode_uid(user.id)

    link = f"{domain_url}/invitation-request/{uid}/{code}"
    subject = "Invitation Request"
    recipient = email.email
    message = f"Click on the link below to accept or decline the invitation: \n{link}"

    await send_email(subject, [recipient], message)

    invite = Invite(
        user_id=user.id,
        campaign_id=user.administration.campaign_id,
        verification_code=code
    )
    db.add(invite)
    db.commit()

    name = user.email.split("@")[0]

    administration = Administration(
        name=name,
        status="INVITED",
        campaign_id=user.administration.campaign_id
    )
    db.add(administration)
    db.commit()

    return JSONResponse({"message": "Invitation sent successfully"}, status_code=250)


@router.post("/get-invite")
async def get_invite(uid: str = Form(...),
                     code: str = Form(...),
                     invite: bool = Form(...),
                     db: Session = Depends(get_db)):
    pk = decode_uid(uid)
    get_user = db.query(User).filter(User.id == pk).first()

    if not get_user:
        raise HTTPException(status_code=404, detail="User not found")

    check_invite = db.query(Invite).filter(Invite.user == get_user, verification_code=code).first()
    get_administration = db.query(Administration).filter(Invite.user == get_user, status == "INVITED").first()

    if not check_invite:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if not get_administration:
        raise HTTPException(status_code=404, detail="User was not invited")

    if invite:
        get_administration.status="ACTIVE"
        check = "accepted"
    else:
        db.delete(get_administration)
        check = "declined"

    db.commit()

    db.delete(check_invite)
    db.commit()

    return JSONResponse(status_code=200,
                        content = {"message": f"Invitation {check}"})
