from sqlalchemy.orm import Session
from sqlalchemy import not_
from fastapi import APIRouter, Depends, HTTPException, Form, status, Request
from fastapi.responses import JSONResponse
from phish.routers import auth
from phish.dependencies import get_db
from phish.models.users import User
from phish.routers.auth import get_user
from phish.models.administration import Administration, Invite
from phish.schemas.administration import (AdministrationBase, AdministrationUpdate,
                                          AdministrationPatch, AdministrationResponse,
                                          SendInvite)
from phish.utils.uid import encode_uid, decode_uid
from phish.utils.email_sender import send_email_with_tracking, send_email
from enum import Enum as PyEnum
from typing import List
import uuid

router = APIRouter(
    prefix="/administration",
    tags=["Administration"]
)


@router.get("/",
            response_model=List[AdministrationResponse],
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
                      current_user: User = Depends(auth.get_current_user),
                      db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    check_administration = db.query(Administration).filter(Administration.user_id == user.id).first()
    if check_administration:
        if check_administration.status == "ACTIVE":
            raise HTTPException(status_code=409, detail="User is already in campaign")
        if check_administration.status == "INVITED":
            db.delete(check_administration)
            db.commit()

    check_invite = db.query(Invite).filter(Invite.user == user).first()
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

    # current_admin = db.query(Administration).filter(Administration.user_id == current_user.id).first()
    # if not current_admin or not current_admin.campaign_id:
    #     raise HTTPException(status_code=404, detail="Please create or assign a campaign before sending invites.")

    # campaign_id = current_admin.campaign_id

    invite = Invite(
        user_id=user.id,
        verification_code=code
    )
    db.add(invite)
    db.commit()

    name = user.email.split("@")[0]
    administration = Administration(
        name=name,
        status="INVITED",
        user_id=user.id,
    )
    db.add(administration)
    db.commit()

    return JSONResponse({"message": "Invitation sent successfully"}, status_code=200)


@router.post("/get-invite")
async def get_invite(uid: str = Form(...),
                     code: str = Form(...),
                     invite: bool = Form(...),
                     db: Session = Depends(get_db)):
    pk = decode_uid(uid)
    user = db.query(User).filter(User.id == pk).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    check_invite = db.query(Invite).filter(Invite.user == user, Invite.verification_code == code).first()
    get_administration = db.query(Administration).filter(Administration.user_id == user.id,
                                                         Administration.status == "INVITED").first()

    if not check_invite:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if not get_administration:
        raise HTTPException(status_code=404, detail="User was not invited")

    if invite:
        get_administration.status = "ACTIVE"
        check = "accepted"
    else:
        db.delete(get_administration)
        check = "declined"

    db.commit()

    db.delete(check_invite)
    db.commit()

    return JSONResponse(status_code=200,
                        content={"message": f"Invitation {check}"})


@router.put("/update/user/{user_id}", response_model=AdministrationResponse,
            summary="Update user",
            description="Update user")
async def update_user(user_id: int, user_update: AdministrationUpdate, db: Session = Depends(get_db)):
    administrator = db.query(Administration).filter(Administration.user_id == user_id).first()

    if not administrator:
        raise HTTPException(sttus_code=404, detail="User not found")

    existing_email = db.query(User).filter(not_(User.email == administrator.user.email)).filter(
        User.email == user_update.user.email).first()

    if existing_email:
        raise HTTPException(status_code=409, detail="This email already exists")

    hashed_password = auth.get_password_hash(user_update.user.password)

    administrator.name = user_update.name
    administrator.is_active = user_update.is_active
    administrator.user.email = user_update.user.email
    administrator.user.hashed_password = hashed_password
    administrator.user.role = user_update.user.role

    db.commit()
    db.refresh(administrator)

    return administrator


@router.patch("/update/user/{user_id}", response_model=AdministrationResponse,
              summary="Update user",
              description="Update user")
async def update_user_patch(user_id: int, user_update: AdministrationPatch, db: Session = Depends(get_db)):
    administrator = db.query(Administration).filter(Administration.user_id == user_id).first()

    if not administrator:
        raise HTTPException(sttus_code=404, detail="User not found")

    existing_email = db.query(User).filter(not_(User.email == administrator.user.email)).filter(
        User.email == user_update.user.email).first()

    if existing_email:
        raise HTTPException(status_code=409, detail="This email already exists")

    if user_update.name is not None:
        administrator.name = user_update.name
    if user_update.is_active is not None:
        administrator.is_active = user_update.is_active
    if user_update.user.email is not None:
        administrator.user.email = user_update.user.email
    if user_update.user.password is not None:
        hashed_password = auth.get_password_hash(user_update.user.password)
        administrator.user.hashed_password = hashed_password
    if user_update.user.role_id is not None:
        administrator.user.role_id = user_update.user.role_id

    db.commit()
    db.refresh(administrator)

    return administrator


@router.delete("/remove/user/{user_id}", summary="Remove user from campaign")
async def remove_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Administration).filter(Administration.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return JSONResponse(status_code=200, content={"message": "User successfully removed"})
