from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import JSONResponse
from database import get_db
from models.target import Target, TargetUser
from schemas.target import (TargetBase, TargetUpdate, TargetUpdatePatch,
                                  TargetResponse, TargetUserBase, TargetUserPatch,
                                  TargetUserResponse)
from typing import List
import pandas as pd
from io import BytesIO


router = APIRouter(
    prefix="/target",
    tags=["Target"]
)

@router.get("/",
            response_model=List[TargetResponse],
            summary="List of Target",
            description="List of Target")
async def target_list(db: Session = Depends(get_db)):
    targets = db.query(Target).all()

    if not targets:
        raise HTTPException(status_code=404, detail="Target not found")

    return targets


@router.get("/detail/{target_id}",
            response_model=TargetResponse,
            summary="Detail of Target",
            description="Detail of Target")
async def target_detail(target_id: int,
                        db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    return target


@router.get("/detail/user/{target_user_id}",
            response_model=TargetUserResponse,
            summary="Detail of Target Users",
            description="Detail of Target User")
async def target_user_detail(target_user_id: int,
                             db: Session = Depends(get_db)):
    target_user = db.query(TargetUser).filter(TargetUser.id == target_user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    return target_user


@router.post("/create",
             response_model=TargetResponse,
             summary="Create a New Target List")
async def create_target(list_name: str = Form(...),
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db)):

    new_target = Target(
        name=list_name
    )

    db.add(new_target)
    db.commit()

    contents = await file.read()
    # Convert the bytes data into a BytesIO object
    datas = pd.read_excel(BytesIO(contents), engine='openpyxl')

    # iterate the dataframe
    for index, row in datas.iterrows():
        new_target_user = TargetUser(
            first_name=row.iloc[0],
            last_name=row.iloc[1],
            email=row.iloc[2],
            company=row.iloc[3],
            job_title=row.iloc[4],
            target_id=new_target.id,
        )

    try:
        db.add(new_target_user)
        db.commit()
    except IntegrityError as e:
        db.rollback()

        raise HTTPException(status_code=409, detail="The list contains an exists email that is already uploaded")

    db.refresh(new_target)

    return new_target


@router.put("/update/{target_id}",
            response_model=TargetResponse,
            summary="Update Target",
            description="Update Target")
async def update_target(target_id: int,
                        target: TargetUpdate,
                        db: Session = Depends(get_db)):
    upt_target = db.query(Target).filter(Target.id == target_id).first()

    if not upt_target:
        raise HTTPException(status_code=404, detail="Target not found")

    upt_target.name = target.name

    db.commit()
    db.refresh(upt_target)

    return upt_target


@router.patch("/update/{target_id}",
            response_model=TargetResponse,
            summary="Update Target",
            description="Update Target")
async def update_target_patch(target_id: int,
                              target: TargetUpdatePatch,
                              db: Session = Depends(get_db)):
    upt_target = db.query(Target).filter(Target.id == target_id).first()

    if not upt_target:
        raise HTTPException(status_code=404, detail="Target not found")

    if target.name is not None:
        upt_target.name = target.name

    db.commit()
    db.refresh(upt_target)

    return upt_target

    
@router.delete("/delete/{target_id}",
               summary="Delete Target",
               description="Delete Target")
async def delete_target_user(target_id: int,
                             db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == target_id).first()

    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    db.delete(target)
    db.commit()

    content = {
        "message": "Target deleted successfully"
    }

    return JSONResponse(status_code=200, content=content)


@router.put("/update/user/{target_user_id}",
            response_model=TargetUserResponse,
            summary="Update Target User",
            description="Update Target User")
async def update_target_user(target_user_id: int,
                             user_target: TargetUserBase,
                             db: Session = Depends(get_db)):
    upt_user_target = db.query(TargetUser).filter(TargetUser.id == target_user_id).first()

    if not upt_user_target:
        raise HTTPException(status_code=404, detail="Target User not found")

    upt_user_target.first_name = user_target.first_name
    upt_user_target.last_name = user_target.last_name
    upt_user_target.email = user_target.email
    upt_user_target.company = user_target.company
    upt_user_target.job_title = user_target.job_title

    db.commit()
    db.refresh(upt_user_target)

    return upt_user_target


@router.patch("/update/user/{target_user_id}",
            response_model=TargetUserResponse,
            summary="Update Target User",
            description="Update Target User")
async def update_target_user_patch(target_user_id: int,
                             target_user: TargetUserPatch,
                             db: Session = Depends(get_db)):
    upt_user_target = db.query(TargetUser).filter(TargetUser.id == target_user_id).first()

    if not upt_user_target:
        raise HTTPException(status_code=404, detail="Target User not found")

    update_data = target_user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if value is not None:
            setattr(upt_user_target, key, value)

    db.commit()
    db.refresh(upt_user_target)

    return upt_user_target


@router.delete("/delete/user/{target_user_id}",
               summary="Delete Target User",
               description="Delete Target User")
async def delete_target_user(target_user_id: int,
                             db: Session = Depends(get_db)):
    target_user = db.query(TargetUser).filter(TargetUser.id == target_user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Target User not found")

    db.delete(target_user)
    db.commit()

    content = {
        "message": "Target User deleted successfully"
    }

    return JSONResponse(status_code=200, content=content)